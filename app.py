from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===================== CONSTANTES =====================

CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}

MSG_BEM_VINDO = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# ANDROID (inclui PHILIPS)
MSG_ANDROID = (
    "Para Android, baixe **Xtream IPTV Player** 📺👇📲 *(recomendado)*.\n"
    "Alternativas: *9Xtream*, *XCIPTV* ou *IPTV Stream Player*.\n"
    "Me avise quando instalar para eu enviar seu login. 🙂"
)
MSG_ANDROID_ALTERNATIVAS = (
    "Claro! Para Android você pode usar: **Xtream IPTV Player** (recomendado), *9Xtream*, *XCIPTV* ou *IPTV Stream Player*.\n"
    "Instale e me avise para eu enviar seu login. 📲"
)
# Link só quando não der/ não quiser instalar pelas lojas/alternativas
MSG_ANDROID_LINK = (
    "🔔 **AÇÃO MANUAL NECESSÁRIA**\n"
    "Se não conseguir ou não quiser instalar pelas lojas/alternativas, faça assim:\n"
    "• **Navegador (Chrome ou da TV Box)**: digite **http://xwkhb.info/axc** e toque em *Ir/Enter* — o download começa automático.\n"
    "• **Downloader**: cole **http://xwkhb.info/axc** no campo URL e confirme para baixar.\n"
    "• **NTDOWN**: cole o mesmo link e baixe.\n"
    "Depois de *instalar e abrir* o app, me avise para eu enviar seu login. 😉"
)

# Xcloud (verde e preto) + alternativas corretas
MSG_XCLOUD = (
    "Para sua TV, use o **Xcloud (ícone verde e preto)** 📺🟩⬛ *(preferencial)*.\n"
    "Se preferir, alternativas: *OTT Player*, *Duplecast* ou *SmartOne*.\n"
    "Instale e me avise para eu enviar seu login. Teste gratuito: **3 horas**. ⏱️"
)
MSG_XCLOUD_ALTERNATIVAS = (
    "Alternativas ao **Xcloud (ícone verde e preto)**: *OTT Player*, *Duplecast* ou *SmartOne*. "
    "Instale e me avise para eu enviar seu login. 📺"
)

# PC / Windows
MSG_PC = (
    "Para PC/Windows, baixe o app por este link:\n"
    "https://7aps.online/iptvsmarters\n\n"
    "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
)

# Pós-login
MSG_POS_LOGIN_OK = "Perfeito! Aproveite seu teste. 😊"
MSG_POS_LOGIN_FALHOU = (
    "Vamos resolver isso! Verifique se digitou *exatamente* como enviado.\n"
    "Atenção às *letras maiúsculas/minúsculas* e aos caracteres parecidos (*I ↔ l*, *O ↔ 0*).\n"
    "Me envie uma *foto da tela* mostrando como está digitando. 📷"
)

# Imagens / QR / MAC
MSG_FOTO_QUAL_APP = (
    "Entendi a foto/QR/MAC! Como não consigo identificar imagens aqui, me diga por favor **qual aplicativo** você está usando:\n"
    "*Duplecast*, *SmartOne*, *OTT Player*, *Xcloud (ícone verde e preto)*, *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *IPTV Stream Player*? 😉"
)

# Fluxos específicos
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

# Planos / Pagamento
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

# Palavras‑chave
KEY_OK = {"deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo", "abriu", "logou"}
KEY_NOK = {"não", "nao", "n consegui", "não funcionou", "nao funcionou", "n deu certo", "nao deu certo", "não deu certo"}
KEY_FOTO = {"foto", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela"}
KEY_ANDROID = {"android", "tv box", "projetor", "celular android", "celular", "philips"}
KEY_XCLOUD_DEVICES = {"samsung", "lg", "roku", "philco nova", "xcloud"}
KEY_PC = {"pc", "computador", "notebook", "windows", "macbook"}

# cliente não consegue/quer instalar das lojas OU pede link
KEY_LINK_ALT = {
    "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
    "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
    "tem link", "manda o link", "baixar por link", "link alternativo", "apk", "aptoide",
    "ntdown", "downloader", "por link", "quero por link"
}
# recusa alternativas → oferece link se for Android
KEY_RECUSA_ALT = {
    "não quero", "nao quero", "não gostei", "nao gostei", "quero outro", "tem outro", "outro app",
    "tem mais algum", "tem mais opções", "não tem esse", "nao tem esse"
}
KEY_PAG = {"pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"}

# Sessões por número
sessions = {}  # numero -> {"msgs":[...], "ctx": None}


# ===================== APP =====================

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip()
    m = mensagem.lower()

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Início da sessão
    if numero not in sessions:
        sessions[numero] = {"msgs": [], "ctx": None}
        return jsonify({"replies": [{"message": MSG_BEM_VINDO}]}])

    s = sessions[numero]
    s["msgs"].append(f"Cliente: {m}")
    contexto = "\n".join(s["msgs"][-15:])

    # Pós‑login
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_OK}]})
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_FALHOU}]})

    # Foto/QR/MAC
    if any(k in m for k in KEY_FOTO):
        return jsonify({"replies": [{"message": MSG_FOTO_QUAL_APP}]})

    # Áudio
    if "áudio" in m or "audio" in m:
        return jsonify({"replies": [{"message": MSG_AUDIO}]})

    # ======== FLUXOS DETERMINÍSTICOS ========

    # Android (inclui Philips) – define contexto e NÃO envia link aqui
    if any(word in m for word in KEY_ANDROID):
        s["ctx"] = "android"
        return jsonify({"replies": [{"message": MSG_ANDROID}]})

    # “Tem outro?/quero outro” respeitando contexto Android → só alternativas (sem link)
    if any(word in m for word in KEY_RECUSA_ALT) and s["ctx"] == "android":
        return jsonify({"replies": [{"message": MSG_ANDROID_ALTERNATIVAS}]})

    # Pedidos/necessidade de link — só se for Android (contexto ou menção)
    if (any(word in m for word in KEY_LINK_ALT) or (any(word in m for word in KEY_RECUSA_ALT) and s["ctx"] == "android")):
        if s["ctx"] == "android" or any(w in m for w in ("android", "tv box", "philips", "celular")):
            return jsonify({"replies": [{"message": MSG_ANDROID_LINK}]})
        else:
            return jsonify({"replies": [{"message": "O link alternativo é para *Android*. Seu aparelho é Android? Se for, te passo agora. 😉"}]})

    # Dispositivos de Xcloud (verde e preto) – define contexto
    if any(word in m for word in KEY_XCLOUD_DEVICES):
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_XCLOUD}]})

    # “Tem outro?” no contexto Xcloud → alternativas corretas
    if any(word in m for word in KEY_RECUSA_ALT) and s["ctx"] == "xcloud":
        return jsonify({"replies": [{"message": MSG_XCLOUD_ALTERNATIVAS}]})

    # PC
    if any(p in m for p in KEY_PC):
        s["ctx"] = "pc"
        return jsonify({"replies": [{"message": MSG_PC}]})

    # Apps citados explicitamente
    if "duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_DUBLECAST_PASSO}]})
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_SMARTONE}]})
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_OTTPLAYER}]})
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_DUBLECAST_JA_TEM}]})

    # Códigos de teste
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": [{"message": "🔓 Gerando seu login de teste, só um instante..."}]})

    # Planos e pagamento
    if any(k in m for k in KEY_PAG):
        return jsonify({"replies": [{"message": MSG_VALORES}, {"message": MSG_PAGAMENTO}, {"message": MSG_PIX_SOZINHO}]})

    # ======== FALLBACK COM IA ========
    prompt = (
        "Você é atendente de IPTV no WhatsApp. Responda curto e objetivo.\n"
        "Android: destacar **Xtream IPTV Player** (recomendado) e listar **9Xtream**, **XCIPTV**, **IPTV Stream Player** como alternativas.\n"
        "Só oferecer o link **http://xwkhb.info/axc** quando o cliente não conseguir/não quiser instalar pelas lojas/alternativas; "
        "explique navegador/Downloader/NTDOWN. Philips = Android.\n"
        "Para TVs com app: **Xcloud (ícone verde e preto)**; alternativas: OTT Player, Duplecast, SmartOne.\n"
        "Foto/QR/MAC: perguntar qual app está usando. Teste gratuito sempre 3 horas.\n\n"
        f"Histórico recente:\n{contexto}\n\n"
        f"Mensagem do cliente: '{mensagem}'\n"
        "Responda seguindo as regras."
    )
    try:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        texto = result.choices[0].message.content.strip()
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"⚠️ Erro ao gerar resposta: {str(e)}"}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
