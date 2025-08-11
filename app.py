from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===================== CONSTANTES / MENSAGENS =====================

MSG_BEM_VINDO = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# Android (inclui Philips)
MSG_ANDROID = (
    "📱 Para Android, recomendo o *Xtream IPTV Player* (preferencial). 📺👇📲\n"
    "Se preferir, pode usar também: *9Xtream*, *XCIPTV* ou *IPTV Stream Player*.\n"
    "Me avise quando instalar para eu enviar seu login."
)
MSG_ANDROID_ALTERNATIVAS = (
    "Opções para Android: *Xtream IPTV Player* (preferencial), *9Xtream*, *XCIPTV* ou *IPTV Stream Player*. 😉"
)
MSG_ANDROID_LINK = (
    "🔔 *AÇÃO MANUAL NECESSÁRIA*\n"
    "Se não conseguiu/ não quer instalar pelas lojas, dá pra baixar direto pelo navegador, Downloader ou NTDOWN.\n"
    "Digite no navegador e aperte Enter: **http://xwkhb.info/axc**\n"
    "Quando o app abrir, me avise para eu enviar seu login. ⏳"
)

# Xcloud (verde e preto)
MSG_XCLOUD = (
    "📺 Para sua TV, use o *Xcloud (ícone verde e preto)* — preferencial.\n"
    "Alternativas: *OTT Player*, *Duplecast* ou *SmartOne*.\n"
    "Me avise quando instalar para eu enviar seu login. ⏱️ Teste gratuito: *3 horas*."
)
MSG_XCLOUD_ALTERNATIVAS = (
    "Alternativas ao *Xcloud (ícone verde e preto)*: *OTT Player*, *Duplecast* ou *SmartOne*. 📺"
)

# PC / Windows
MSG_PC = (
    "🖥️ Para PC/Windows, baixe o app por este link:\n"
    "https://7aps.online/iptvsmarters\n\n"
    "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
)

# Pós‑login
MSG_POS_LOGIN_OK = "Perfeito! Aproveite seu teste. 😊"
MSG_POS_LOGIN_FALHOU = (
    "Vamos resolver! Confira se digitou *exatamente* como enviado.\n"
    "Atenção às *letras maiúsculas/minúsculas* e aos parecidos: *I (i maiúsculo)* vs *l (L minúsculo)*, *O* vs *0*.\n"
    "Pode me enviar uma *foto da tela* mostrando como você está digitando? 📷"
)

# Foto/QR/MAC
MSG_FOTO_PERGUNTA_APP = (
    "Entendi a foto/QR/MAC! Como não consigo identificar imagens aqui, me diga **qual aplicativo** você está usando:\n"
    "*Duplecast*, *SmartOne*, *OTT Player*, *Xcloud (ícone verde e preto)*, *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *IPTV Stream Player*? 😉"
)

# Fluxos específicos
MSG_DUBLECAST_PASSO = (
    "No *Duplecast*, siga: Start ➜ Português ➜ Brasil ➜ Fuso horário *-03* ➜ *Minha duplecast*.\n"
    "Depois envie uma *foto do QR code* de perto e digite **871** aqui na conversa (eu gero o teste via link M3U)."
)
MSG_DUBLECAST_JA_TEM = (
    "Se você *já tem* o Duplecast: envie a *foto do QR code* de perto e depois digite **871** aqui na conversa. 😉"
)
MSG_SMARTONE = (
    "No *SmartOne*, me envie o **MAC** (ou *foto da tela com o MAC*). Depois digite **871** para eu gerar o teste."
)
MSG_OTTPLAYER = (
    "No *OTT Player*, me envie uma *foto do QR code* de perto. Em seguida, digite **871** para eu gerar o teste."
)

# Planos / pagamento
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

MSG_AUDIO = "Ops! 😅 Não consigo interpretar *áudios*. Pode me mandar por *texto*? Continuo te ajudando!"

MSG_FLAG_MANUAL = "🔔 *AÇÃO MANUAL NECESSÁRIA*: analisar e enviar login/dados quando o cliente confirmar."

# Dicionários de palavras‑chave
CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}
KEY_OK = {"deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo", "abriu", "logou"}
KEY_NOK = {"não", "nao", "n consegui", "não funcionou", "nao funcionou", "n deu certo", "nao deu certo", "não deu certo"}
KEY_FOTO = {"foto", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela"}
KEY_ANDROID = {"android", "tv box", "projetor", "celular android", "celular", "philips"}  # Philips = Android
KEY_XCLOUD_DEVICES = {"samsung", "lg", "roku", "philco nova", "xcloud"}
KEY_PC = {"pc", "computador", "notebook", "windows", "macbook"}
KEY_LINK_ALT = {
    "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
    "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
    "tem link", "manda o link", "baixar por link", "link alternativo", "apk", "aptoide", "ntdown", "downloader"
}
KEY_PAG = {"pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"}
KEY_OUTRO = {
    "tem outro", "tem mais algum", "quero outro", "outro app", "tem mais uma opção",
    "tem mais opções", "não tem esse", "nao tem esse", "não tem esse.", "nao tem esse."
}

# Sessões por cliente: histórico e contexto (android / xcloud / pc)
sessions = {}  # numero -> {"msgs": [..], "ctx": None}


# ===================== APP =====================

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = (query.get("sender") or "").strip()
    mensagem = (query.get("message") or "").strip()
    m = mensagem.lower()

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Cria sessão e boas‑vindas
    if numero not in sessions:
        sessions[numero] = {"msgs": [], "ctx": None}
        return jsonify({"replies": [{"message": MSG_BEM_VINDO}]})

    # Histórico curto
    s = sessions[numero]
    s["msgs"].append(f"Cliente: {m}")
    contexto = "\n".join(s["msgs"][-15:])

    # ---------------- Pós‑login ----------------
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_OK}]})

    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify({"replies": [{"message": MSG_POS_LOGIN_FALHOU}]})

    # ---------------- Foto/QR/MAC ----------------
    if any(k in m for k in KEY_FOTO):
        return jsonify({"replies": [{"message": MSG_FOTO_PERGUNTA_APP}]})

    # ---------------- Áudio ----------------
    if "áudio" in m or "audio" in m:
        return jsonify({"replies": [{"message": MSG_AUDIO}]})

    # ---------------- “Tem outro?” respeitando contexto ----------------
    if any(phrase in m for phrase in KEY_OUTRO):
        if s["ctx"] == "android":
            return jsonify({"replies": [{"message": MSG_ANDROID_ALTERNATIVAS}]})
        elif s["ctx"] == "xcloud":
            return jsonify({"replies": [{"message": MSG_XCLOUD_ALTERNATIVAS}]})
        else:
            return jsonify({"replies": [{"message": "Me diga o aparelho (Android, Samsung/LG/Roku, iPhone ou PC) que te mostro as opções certinhas. 😉"}]})

    # ===================== RESPOSTAS DETERMINÍSTICAS =====================

    # Android (define contexto)
    if any(word in m for word in KEY_ANDROID):
        s["ctx"] = "android"
        return jsonify({"replies": [{"message": MSG_ANDROID}]})

    # Precisa de link alternativo (apenas se já estiver em contexto Android ou a frase citar Android)
    if any(f in m for f in KEY_LINK_ALT):
        if s["ctx"] == "android" or any(w in m for w in ("android", "tv box", "philips", "celular")):
            return jsonify({"replies": [{"message": MSG_ANDROID_LINK}, {"message": MSG_FLAG_MANUAL}]})
        else:
            return jsonify({"replies": [{"message": "O link alternativo é para *Android*. Seu aparelho é Android? Se for, te passo agora. 😉"}]})

    # Dispositivos com Xcloud (define contexto)
    if any(word in m for word in KEY_XCLOUD_DEVICES):
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_XCLOUD}]})

    # PC / Windows (define contexto)
    if any(p in m for p in KEY_PC):
        s["ctx"] = "pc"
        return jsonify({"replies": [{"message": MSG_PC}]})

    # Apps mencionados explicitamente
    if "duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_DUBLECAST_PASSO}]})
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_DUBLECAST_JA_TEM}]})
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_SMARTONE}]})
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": [{"message": MSG_OTTPLAYER}]})

    # Cliente digitou código de teste (quem envia login é o AutoResponder)
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": [{"message": "🔓 Gerando seu login de teste, só um instante..."}]})

    # Planos + pagamento + Pix separado
    if any(k in m for k in KEY_PAG):
        return jsonify({"replies": [
            {"message": MSG_VALORES},
            {"message": MSG_PAGAMENTO},
            {"message": MSG_PIX_SOZINHO}
        ]})

    # ===================== FALLBACK COM IA (casos gerais) =====================
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Responda curto, objetivo e educado.\n"
        "Nunca recomende apps fora desta lista: Xtream IPTV Player, 9Xtream, XCIPTV, IPTV Stream Player, "
        "Xcloud (ícone verde e preto), OTT Player, Duplecast, SmartOne, Smarters Player Lite (iOS) e IPTV Smarters (PC).\n"
        "Teste gratuito sempre *3 horas*. Ao falar de valores, envie planos + Pix em mensagem separada.\n"
        "Se o cliente enviar foto/QR/MAC, diga que não identifica imagens e pergunte qual app está usando.\n"
        "Se pedir link alternativo para Android, use exatamente: http://xwkhb.info/axc e a frase '🔔 AÇÃO MANUAL NECESSÁRIA'.\n"
        f"Histórico recente:\n{contexto}\n\nMensagem do cliente: '{mensagem}'\nResponda seguindo estritamente as regras."
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
