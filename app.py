from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================================
# Helpers
# =====================================================================

def replies_from_blocks(blocks):
    """Converte uma lista de strings em múltiplas mensagens para o AutoResponder."""
    return {"replies": [{"message": b} for b in blocks]}

# =====================================================================
# Constantes de fluxo (mensagens em blocos)
# =====================================================================

# Boas-vindas em blocos
WELCOME_BLOCKS = [
    "Olá! 👋 Seja bem-vindo!",
    "Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿",
    "Vamos começar seu *teste gratuito*?",
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Android/TV Box/Philips, iPhone, PC...)."
]

# ------------------ ANDROID (inclui Philips) ------------------

ANDROID_BLOCKS = [
    "⬇️ **BAIXE O APLICATIVO** ⬇️",
    "• **XTREAM IPTV PLAYER** 🔥 *(preferencial)*",
    "🛠️ **DEPOIS DE INSTALAR:** toque em **ADICIONAR / ADD** ➕ e deixe o app aberto.",
    "✅ **OUTRAS OPÇÕES QUE TAMBÉM FUNCIONAM** ⬇️\n• **XCIPTV**\n• **IPTV STREAM PLAYER**\n• **9XTREAM**",
    "🔎 *Dica:* pesquise pelo **nome exato** e confira **ícone** e **desenvolvedor** na loja.",
    "📣 **ME AVISE QUANDO BAIXAR** que eu envio o seu login! 🙂"
]

ANDROID_ALTERNATIVAS_BLOCKS = [
    "Claro! 🙂 Outras opções para Android que funcionam:",
    "• **XCIPTV**\n• **IPTV STREAM PLAYER**\n• **9XTREAM**",
    "Baixe uma delas e me avise pra eu enviar seu login. 📲"
]

# Link alternativo (só quando não achar/instalar de jeito nenhum)
ANDROID_LINK_BLOCKS = [
    "🔁 **NÃO ACHOU OU NÃO CONSEGUIU INSTALAR?** Sem problema! Vamos pelo **link direto**:",
    "🌐 **Navegador (Chrome/qualquer):**\nDigite **http://xwkhb.info/axc** e toque **Enter**. O download começa sozinho. 🔽",
    "📺 **Downloader (TV Box):**\nAbra o app, cole **http://xwkhb.info/axc** e baixe.",
    "📥 **NTDOWN:**\nCole **http://xwkhb.info/axc** e baixe.",
    "🔔 **AÇÃO MANUAL NECESSÁRIA**: assim que abrir o app instalado pelo link, me avise aqui pra eu enviar o login. 😉"
]

# Quando cliente manda foto durante fluxo Android (mantém o rumo)
ANDROID_FOTO_BLOCKS = [
    "Vi sua imagem 👍",
    "Aqui eu não consigo *ler fotos/QR*; siga os passos do Android acima e me diga **qual app** você escolheu (Xtream, XCIPTV, IPTV Stream Player ou 9Xtream).",
    "Assim que instalar, me avise que eu envio seu login. 🙂"
]

# ------------------ TVS COM XCLOUD (Samsung/LG/Roku/Philco nova) ------------------

XCLOUD_PRIMARY_BLOCKS = [
    "📺 **TV compatível com Xcloud** detectada!",
    "Use o **Xcloud (ícone verde e preto)** 🟩⬛ *(preferencial)*",
    "Instale e me avise para eu enviar seu login. ⏱️ O teste gratuito dura **3 horas**."
]

XCLOUD_ALTERNATIVAS_BLOCKS = [
    "Se preferir, alternativas na sua TV:",
    "• **OTT Player**\n• **Duplecast**\n• **SmartOne**",
    "Instale e me diga qual app escolheu pra eu te guiar certinho. 😉"
]

# ------------------ iOS / PC ------------------

IOS_BLOCKS = [
    "🍏 **iPhone/iPad (iOS):**",
    "Baixe o **Smarters Player Lite** (ícone azul, App Store).",
    "Quando instalar, me avise que eu te passo o acesso. 🙂"
]

PC_BLOCKS = [
    "🖥️ **PC / Windows:**",
    "Baixe o aplicativo por este link: https://7aps.online/iptvsmarters",
    "Depois me avise quando abrir o app para eu enviar o seu login. 🙂"
]

# ------------------ PÓS-LOGIN ------------------

POS_LOGIN_OK_BLOCKS = ["Perfeito! ✅", "Aproveite seu teste. Se precisar de algo, estou por aqui. 😊"]

POS_LOGIN_FAIL_BLOCKS = [
    "Vamos resolver isso! ⚙️",
    "Confira se digitou *exatamente* como enviado.",
    "Atenção às *letras maiúsculas/minúsculas* e aos parecidos: **I/l**, **O/0**.",
    "Pode me enviar uma *foto da tela* mostrando como está digitando? 📷"
]

# ------------------ FOTOS/QR/MAC (genérico) ------------------

FOTO_QUAL_APP_BLOCKS = [
    "Entendi a foto/QR/MAC! 👍",
    "Como não consigo identificar imagem aqui, me diga **qual aplicativo** você está usando:",
    "• **Duplecast**\n• **SmartOne**\n• **OTT Player**\n• **Xcloud (ícone verde e preto)**\n• **Xtream IPTV Player**\n• **9Xtream**\n• **XCIPTV**\n• **IPTV Stream Player**"
]

# ------------------ APPS ESPECÍFICOS ------------------

DUPLECAST_PASSO_BLOCKS = [
    "Certo! **Duplecast** 📱",
    "Siga: *Start → Português → Brasil → Fuso horário -03 → Minha duplecast*.",
    "Depois, envie uma *foto do QR code* de perto.",
    "Em seguida, digite **871** aqui na conversa para eu gerar o teste (link M3U)."
]

DUPLECAST_JA_TEM_BLOCKS = [
    "Perfeito! Você já tem **Duplecast** ✅",
    "Envie uma *foto do QR code* de perto.",
    "Depois, digite **871** aqui para eu gerar o teste (link M3U)."
]

SMARTONE_BLOCKS = [
    "App **SmartOne** 📺",
    "Me envie o **MAC** (ou uma *foto da tela com o MAC*).",
    "Depois disso, digite **871** aqui para eu gerar o teste."
]

OTTPLAYER_BLOCKS = [
    "App **OTT Player** 📺",
    "Me envie uma *foto do QR code* de perto.",
    "Depois disso, digite **871** aqui para eu gerar o teste."
]

# ------------------ PLANOS / PAGAMENTO ------------------

PLANOS_BLOCKS = [
    "💰 **Planos disponíveis**:",
    "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00"
]

PAGAMENTO_BLOCKS = [
    "💳 **Formas de pagamento**:",
    "Pix ou Cartão (link seguro): https://mpago.la/2Nsh3Fq",
    "Vou enviar o *Pix (CNPJ)* em uma mensagem separada para facilitar a cópia."
]

PIX_SOZINHO = "Pix (CNPJ): 46.370.366/0001-97"

AUDIO_BLOCKS = [
    "Ops! 😅",
    "Por aqui eu não consigo interpretar *áudios*.",
    "Pode me mandar por *texto*? Eu continuo te ajudando normalmente!"
]

# =====================================================================
# Palavras-chave / grupos
# =====================================================================

CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}

KEY_OK = {"deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo", "abriu", "logou"}
KEY_NOK = {"não", "nao", "n consegui", "não funcionou", "nao funcionou", "n deu certo", "nao deu certo", "não deu certo"}

KEY_FOTO = {"foto", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela", "imagem", "print"}

KEY_ANDROID = {"android", "tv box", "projetor", "celular android", "celular", "philips"}

KEY_XCLOUD_DEVICES = {"samsung", "lg", "roku", "philco nova", "xcloud"}

KEY_PC = {"pc", "computador", "notebook", "windows", "macbook"}

KEY_LINK_ALT = {
    "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
    "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
    "tem link", "manda o link", "baixar por link", "link alternativo", "apk", "aptoide", "ntdown", "downloader",
    "não achei", "nao achei", "não tem", "nao tem", "não encontrei", "nao encontrei"
}

KEY_PAG = {"pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"}

KEY_OUTRO = {
    "tem outro", "tem mais algum", "quero outro", "outro app", "tem mais uma opção", "tem mais opções",
    "não tem esse", "nao tem esse", "não tem esse.", "nao tem esse."
}

# =====================================================================
# Estado por contato (histórico curto + contexto do fluxo)
# =====================================================================

sessions = {}  # numero -> {"msgs": [..], "ctx": None}

# =====================================================================
# Rota principal
# =====================================================================

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip()
    m = mensagem.lower()

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Inicia sessão
    if numero not in sessions:
        sessions[numero] = {"msgs": [], "ctx": None}
        return jsonify(replies_from_blocks(WELCOME_BLOCKS))

    # Atualiza histórico curto
    s = sessions[numero]
    s["msgs"].append(f"Cliente: {m}")
    contexto = "\n".join(s["msgs"][-15:])

    # ---------------- Pós-login ----------------
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify(replies_from_blocks(POS_LOGIN_OK_BLOCKS))

    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify(replies_from_blocks(POS_LOGIN_FAIL_BLOCKS))

    # ---------------- Áudio ----------------
    if "áudio" in m or "audio" in m:
        return jsonify(replies_from_blocks(AUDIO_BLOCKS))

    # ---------------- “Tem outro?” controlado por contexto ----------------
    if any(phrase in m for phrase in KEY_OUTRO):
        if s["ctx"] == "android":
            return jsonify(replies_from_blocks(ANDROID_ALTERNATIVAS_BLOCKS))
        elif s["ctx"] == "xcloud":
            return jsonify(replies_from_blocks(XCLOUD_ALTERNATIVAS_BLOCKS))
        else:
            return jsonify({"replies": [{"message": "Me diga o aparelho (Android/TV Box/Philips, Samsung/LG/Roku, iPhone ou PC) e te passo as opções certinhas. 😉"}]})

    # ---------------- Foto/QR/MAC ----------------
    if any(k in m for k in KEY_FOTO):
        if s["ctx"] == "android":
            return jsonify(replies_from_blocks(ANDROID_FOTO_BLOCKS))
        return jsonify(replies_from_blocks(FOTO_QUAL_APP_BLOCKS))

    # ===================== RESPOSTAS DETERMINÍSTICAS =====================

    # ANDROID (inclui Philips) – define contexto
    if any(word in m for word in KEY_ANDROID):
        s["ctx"] = "android"
        return jsonify(replies_from_blocks(ANDROID_BLOCKS))

    # Pedir link alternativo (somente se Android declarado ou contexto Android)
    if any(f in m for f in KEY_LINK_ALT):
        if s["ctx"] == "android" or any(w in m for w in KEY_ANDROID):
            return jsonify(replies_from_blocks(ANDROID_LINK_BLOCKS))
        else:
            return jsonify({"replies": [{"message": "O link alternativo é para *Android*. Seu aparelho é Android/TV Box/Philips? Se for, te mando agora. 😉"}]})

    # Dispositivos de Xcloud – define contexto
    if any(word in m for word in KEY_XCLOUD_DEVICES):
        s["ctx"] = "xcloud"
        # envia preferencial + alternativas em blocos
        blocks = XCLOUD_PRIMARY_BLOCKS + XCLOUD_ALTERNATIVAS_BLOCKS
        return jsonify(replies_from_blocks(blocks))

    # iOS
    if "iphone" in m or "ios" in m:
        s["ctx"] = "ios"
        return jsonify(replies_from_blocks(IOS_BLOCKS))

    # PC / Windows
    if any(p in m for p in KEY_PC):
        s["ctx"] = "pc"
        return jsonify(replies_from_blocks(PC_BLOCKS))

    # Cliente menciona explicitamente apps
    if "duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify(replies_from_blocks(DUPLECAST_PASSO_BLOCKS))
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify(replies_from_blocks(DUPLECAST_JA_TEM_BLOCKS))
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"
        return jsonify(replies_from_blocks(SMARTONE_BLOCKS))
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"
        return jsonify(replies_from_blocks(OTTPLAYER_BLOCKS))

    # Cliente digita um código de teste (quem envia login é o AutoResponder)
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": [{"message": "🔓 Gerando seu login de teste, só um instante..."}]})

    # ---------------- Confirmação de instalação → enviar código correto ----------------
    if any(p in m for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        # usa contexto + últimas mensagens para inferir
        ultimas = [msg for msg in s["msgs"][-6:] if msg.startswith("Cliente:")]
        recent = " ".join(ultimas).lower()

        if ("xcloud" in recent) or any(d in recent for d in ["samsung", "lg", "roku", "philco nova"]):
            codigo = "91"
        elif any(appkw in recent for appkw in ["xtream", "9xtream", "xciptv", "iptv stream player", "vu iptv", "android", "tv box", "celular", "projetor", "philips"]):
            codigo = "555"
        elif any(d in recent for d in ["iphone", "ios"]):
            codigo = "224"
        elif any(d in recent for d in ["computador", "pc", "notebook", "macbook", "windows"]):
            codigo = "224"
        elif "philco antiga" in recent:
            codigo = "98"
        elif "tv antiga" in recent or "smart stb" in recent:
            codigo = "88"
        elif any(a in recent for a in ["duplecast", "smartone", "ott"]):
            codigo = "871"
        else:
            # fallback pelo contexto
            if s["ctx"] == "android":
                codigo = "555"
            elif s["ctx"] == "xcloud":
                codigo = "91"
            elif s["ctx"] in {"ios", "pc"}:
                codigo = "224"
            else:
                codigo = "91"

        return jsonify({"replies": [{"message": f"Digite **{codigo}** aqui na conversa para receber seu login. 😉"}]})

    # ---------------- Planos / Pagamento ----------------
    if any(k in m for k in KEY_PAG):
        return jsonify({"replies": [{"message": PLANOS_BLOCKS[0] + "\n" + PLANOS_BLOCKS[1]},
                                    {"message": "\n".join(PAGAMENTO_BLOCKS)},
                                    {"message": PIX_SOZINHO}]})

    # ===================== FALLBACK COM IA (casos gerais) =====================
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Responda curto, objetivo e educado. "
        "Nunca recomende aplicativos fora desta lista: Xtream IPTV Player, 9Xtream, XCIPTV, IPTV Stream Player, "
        "Xcloud (ícone verde e preto), OTT Player, Duplecast, SmartOne, Smarters Player Lite (iOS) e IPTV Smarters para PC. "
        "Teste gratuito sempre 3 horas. Se falar sobre valores, envie planos e depois Pix em mensagem separada. "
        "Se o cliente enviar foto/QR/MAC, diga que não identifica imagens e pergunte qual aplicativo está usando. "
        "Fluxo Android deve manter ênfase em Xtream, com alternativas 9Xtream, XCIPTV, IPTV Stream Player; "
        "só ofereça http://xwkhb.info/axc quando ele não achar/instalar na loja. "
        "Se mandar áudio, diga que não interpreta áudio e peça texto.\n\n"
        f"Histórico recente:\n{contexto}\n\n"
        f"Mensagem do cliente: '{mensagem}'\n"
        "Responda seguindo essas regras."
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

# =====================================================================

if __name__ == "__main__":
    # Render/AutoResponder costuma usar porta 10000
    app.run(host="0.0.0.0", port=10000)
