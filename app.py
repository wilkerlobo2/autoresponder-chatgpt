from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===================== MENSAGENS FIXAS / CONSTANTES =====================

MSG_BEM_VINDO = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

MSG_ANDROID = (
    "Para Android, baixe o app **Xtream IPTV Player** 📺👇📲 *(recomendado)*.\n"
    "Também pode usar: *9Xtream*, *XCIPTV* ou *Vu IPTV Player*.\n"
    "Me avise quando instalar para eu enviar seu login."
)

MSG_ANDROID_LINK = (
    "🔔 **AÇÃO MANUAL NECESSÁRIA**: cliente precisa de link alternativo.\n"
    "Não tem problema! Você consegue baixar por link (Chrome/Downloader/NTDOWN)?\n"
    "Use este link: http://xwkhb.info/axc\n"
    "Assim que abrir o app, me avise para eu enviar seu login. ⏳"
)

MSG_XCLOUD = (
    "Para sua TV, use o **Xcloud (ícone verde e preto)** 📺🟩⬛ *(preferencial)*.\n"
    "Se preferir, também dá para usar: *OTT Player*, *Duplecast* ou *SmartOne*.\n"
    "Instale e me avise para eu enviar seu login. O teste gratuito dura **3 horas**. ⏱️"
)

MSG_PC = (
    "Para PC/Windows, baixe o app por este link:\n"
    "https://7aps.online/iptvsmarters\n\n"
    "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
)

MSG_POS_LOGIN_OK = "Perfeito! Aproveite seu teste. 😊"

MSG_POS_LOGIN_FALHOU = (
    "Vamos resolver isso! Verifique se digitou *exatamente* como enviado.\n"
    "Atenção às *letras maiúsculas e minúsculas* e aos caracteres parecidos (*I* vs *l*, *O* vs *0*).\n"
    "Pode me enviar uma *foto da tela* mostrando como você está digitando? 📷"
)

MSG_FOTO_QUAL_APP = (
    "Entendi a foto/QR/MAC! Como não consigo identificar imagens aqui, me diga por favor **qual aplicativo** você está usando:\n"
    "*Duplecast*, *SmartOne*, *OTT Player*, *Xcloud (ícone verde e preto)*, *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *Vu IPTV Player*? 😉"
)

MSG_DUBLECAST_PASSO = (
    "Certo! No *Duplecast*, siga:\n"
    "Start ➜ Português ➜ Brasil ➜ Fuso horário *-03* ➜ *Minha duplecast*.\n"
    "Depois, envie uma *foto do QR code* de perto. Em seguida, digite **871** aqui na conversa para eu gerar o teste (link M3U)."
)

MSG_DUBLECAST_JA_TEM = (
    "Perfeito! Se você *já tem* o Duplecast, envie uma *foto do QR code* de perto e depois digite **871** aqui na conversa."
)

MSG_SMARTONE = (
    "No *SmartOne*, me envie o **MAC** (ou uma *foto da tela com o MAC*). Depois disso, digite **871** aqui para eu gerar o teste."
)

MSG_OTTPLAYER = (
    "No *OTT Player*, me envie uma *foto do QR code* de perto. Em seguida, digite **871** aqui para eu gerar o teste."
)

MSG_VALORES = (
    "💰 *Planos disponíveis*:\n"
    "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00"
)

MSG_PAGAMENTO = (
    "💳 *Formas de pagamento*: Pix ou Cartão.\n"
    "Cartão (link seguro): https://mpago.la/2Nsh3Fq\n"
    "Vou te mandar o *Pix (CNPJ)* em uma mensagem separada para facilitar a cópia."
)

MSG_PIX_SOZINHO = "Pix (CNPJ): 46.370.366/0001-97"

MSG_AUDIO = (
    "Ops! 😅 Por aqui eu não consigo interpretar *áudios*. Pode me mandar por *texto*? Eu continuo te ajudando normalmente!"
)

MSG_ATENCAO_MANUAL = "🔔 **AÇÃO MANUAL NECESSÁRIA**: analisar e enviar login/dados quando o cliente confirmar."

# Palavras-chave/agrupamentos
CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}
KEY_OK = {"deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo", "abriu", "logou"}
KEY_NOK = {"não", "nao", "n consegui", "não funcionou", "nao funcionou", "n deu certo", "nao deu certo", "não deu certo"}
KEY_FOTO = {"foto", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela"}
KEY_ANDROID = {"android", "tv box", "projetor", "celular android", "celular", "philips"}
KEY_XCLOUD_DEVICES = {"samsung", "lg", "roku", "philco nova", "xcloud"}
KEY_PC = {"pc", "computador", "notebook", "windows", "macbook"}
KEY_LINK_ALT = {
    "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
    "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
    "tem link", "manda o link", "baixar por link", "link alternativo", "apk", "aptoide", "ntdown", "downloader"
}
KEY_PAG = {"pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"}

# Histórico por número
historico_conversas = {}


# ===================== APP =====================

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip()
    mensagem_lc = mensagem.lower()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Boas-vindas fixas
    if numero not in historico_conversas:
        historico_conversas[numero] = []
        return jsonify({"replies": [{"message": MSG_BEM_VINDO}]})

    # Guarda no histórico (somente última parte em minúsculas para regras)
    historico_conversas[numero].append(f"Cliente: {mensagem_lc}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    # --- Pós-login: confirmou que funcionou
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in mensagem_lc for k in KEY_OK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_OK}]})

    # --- Pós-login: disse que NÃO conseguiu
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in mensagem_lc for k in KEY_NOK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_FALHOU}]})

    # --- Foto/QR/MAC: perguntar qual app
    if any(k in mensagem_lc for k in KEY_FOTO):
        return jsonify({"replies": [{"message": MSG_FOTO_QUAL_APP}]})

    # --- Áudio
    if "áudio" in mensagem_lc or "audio" in mensagem_lc:
        return jsonify({"replies": [{"message": MSG_AUDIO}]})

    # ===================== RESPOSTAS DETERMINÍSTICAS =====================

    # Android (inclui Philips) – primeiro passo SEM link
    if any(word in mensagem_lc for word in KEY_ANDROID):
        return jsonify({"replies": [{"message": MSG_ANDROID}]})

    # Se o cliente disser que não consegue baixar (aí sim o link alternativo)
    if any(f in mensagem_lc for f in KEY_LINK_ALT):
        return jsonify({"replies": [{"message": MSG_ANDROID_LINK}, {"message": MSG_ATENCAO_MANUAL} ]})

    # Dispositivos com Xcloud (verde e preto) – com alternativas
    if any(word in mensagem_lc for word in KEY_XCLOUD_DEVICES):
        return jsonify({"replies": [{"message": MSG_XCLOUD}]})

    # PC / Windows
    if any(p in mensagem_lc for p in KEY_PC):
        return jsonify({"replies": [{"message": MSG_PC}]})

    # Cliente mencionou explicitamente “duplecast / smartone / ott player”
    if "duplecast" in mensagem_lc:
        return jsonify({"replies": [{"message": MSG_DUBLECAST_PASSO}]})
    if "smartone" in mensagem_lc or "smart one" in mensagem_lc:
        return jsonify({"replies": [{"message": MSG_SMARTONE}]})
    if "ott player" in mensagem_lc or "ottplayer" in mensagem_lc:
        return jsonify({"replies": [{"message": MSG_OTTPLAYER}]})
    if "já tenho duplecast" in mensagem_lc or "ja tenho duplecast" in mensagem_lc:
        return jsonify({"replies": [{"message": MSG_DUBLECAST_JA_TEM}]})

    # --- Se cliente digitar um código de teste (AutoResponder cuidará do login)
    if mensagem_lc.strip() in CODIGOS_TESTE:
        return jsonify({"replies": [{"message": "🔓 Gerando seu login de teste, só um instante..."}]})

    # --- Planos e pagamento
    if any(k in mensagem_lc for k in KEY_PAG):
        return jsonify({"replies": [{"message": MSG_VALORES}, {"message": MSG_PAGAMENTO}, {"message": MSG_PIX_SOZINHO}]})

    # ===================== FALLBACK COM IA (casos gerais) =====================
    # IA com instruções rígidas para não inventar apps
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Responda de forma curta, objetiva e educada. "
        "Nunca recomende aplicativos fora desta lista: Xtream IPTV Player, 9Xtream, XCIPTV, Vu IPTV Player, "
        "Xcloud (ícone verde e preto), OTT Player, Duplecast, SmartOne, Smarters Player Lite (iOS) e IPTV Smarters para PC.\n"
        "Teste gratuito sempre **3 horas**. Se falar sobre valores, enviar planos e depois Pix em mensagem separada.\n"
        "Se o cliente enviar foto/QR/MAC, diga que não identifica imagens e pergunte qual aplicativo está usando.\n"
        "Se pedir ajuda por link alternativo para Android, use exatamente: http://xwkhb.info/axc e a frase '🔔 AÇÃO MANUAL NECESSÁRIA'.\n"
        "Se mandar áudio, diga que não pode interpretar e peça texto.\n\n"
        f"Histórico recente:\n{contexto}\n\n"
        f"Mensagem do cliente: '{mensagem}'\n"
        "Responda agora seguindo essas regras estritas."
    )

    try:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        texto = result.choices[0].message.content.strip()
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"⚠️ Erro ao gerar resposta: {str(e)}"}]})

# =======================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
