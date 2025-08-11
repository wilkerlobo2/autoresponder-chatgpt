from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===================== HELPERS =====================

def bubbles(*msgs, delay_ms=500):
    """
    Converte uma tupla de strings em uma lista de replies com delays.
    - O primeiro balão sai sem delay; os demais saem com delay_ms (0.5s).
    """
    replies = []
    for i, txt in enumerate(msgs):
        replies.append({"message": txt, "delay": 0 if i == 0 else delay_ms})
    return replies

def reply_list(*blocks):
    """
    Achata listas de replies (cada block pode ser uma lista de replies).
    """
    out = []
    for blk in blocks:
        out.extend(blk)
    return out

# ===================== CONSTANTES / TEXTOS =====================

CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}

KEY_OK = {"deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo", "abriu", "logou"}
KEY_NOK = {"não", "nao", "n consegui", "não funcionou", "nao funcionou", "n deu certo", "nao deu certo", "não deu certo"}
KEY_OUTRO = {"tem outro", "quero outro", "outro app", "tem mais algum", "tem mais uma opção", "tem mais opções"}
KEY_ANDROID = {"android", "tv box", "projetor", "celular android", "celular", "philips"}
KEY_XCLOUD_DEV = {"samsung", "lg", "roku", "philco nova", "xcloud"}
KEY_PC = {"pc", "computador", "notebook", "windows", "macbook"}

# pedidos de link/relatos de dificuldade em loja
KEY_LINK_ALT = {
    "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
    "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
    "tem link", "manda o link", "baixar por link", "link alternativo", "apk",
    "aptoide", "ntdown", "downloader", "não achei", "nao achei"
}

KEY_PAG = {"pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"}

KEY_FOTO = {"foto", "imagem", "print", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela"}

MSG_BEM_VINDO = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# ---------- ANDROID (inclui PHILIPS) ----------
ANDROID_MAIN = [
    "📱 Para Android, recomendo o *Xtream IPTV Player* *(preferencial)*.",
    "Se quiser alternativas, temos: *9Xtream*, *XCIPTV* e *IPTV Stream Player*.",
    "Depois de instalar, me avise para eu enviar seu login. 😉",
    "Se não encontrar na loja, me fale que eu te ensino outras formas."
]

ANDROID_ALTS = [
    "✅ *OUTROS APLICATIVOS QUE VOCÊ TAMBÉM PODE USAR* ⬇️",
    "• *9Xtream*\n• *XCIPTV*\n• *IPTV Stream Player*",
    "Instale um deles e me avise para eu enviar seu login. 📲"
]

ANDROID_ENSINO_LOJA = [
    "🛠️ Vamos tentar pela loja:",
    "1) Abra a *Play Store*.\n2) Busque por *Xtream IPTV Player*.\n3) Toque em *Instalar*.",
    "Se não aparecer, busque por: *9Xtream*, *XCIPTV* ou *IPTV Stream Player*.",
    "Conseguiu? Me avise aqui. 😊"
]

ANDROID_LINK = [
    "🔔 *AÇÃO MANUAL NECESSÁRIA*",
    "Como você não achou na loja, tente pelo *link direto* no navegador/Downloader/NTDOWN:",
    "👉 http://xwkhb.info/axc",
    "Digite esse endereço e toque *Enter* — o download começa sozinho. Depois que abrir o app, me avise para eu enviar seu login. ⏳"
]

ANDROID_FOTO_FALLBACK = [
    "🔔 *AÇÃO MANUAL NECESSÁRIA*",
    "Recebi uma imagem durante o fluxo *Android*. Vou verificar e te retorno.",
    "Enquanto isso, me diga: conseguiu instalar *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *IPTV Stream Player*?"
]

# ---------- XCLOUD (TVs Samsung/LG/Roku/Philco nova) ----------
XCLOUD_MAIN = [
    "📺 *TV compatível com Xcloud* detectada!",
    "Use o *Xcloud (ícone verde e preto)* 🟩⬛ *(preferencial)*.",
    "Instale e me avise para eu enviar seu login.",
    "🕒 O teste gratuito dura *3 horas*."
]

XCLOUD_ALTS = [
    "Se preferir, alternativas na sua TV:",
    "• *OTT Player*\n• *Duplecast*\n• *SmartOne*",
    "Instale e me diga qual app escolheu pra eu te guiar certinho. 😉"
]

# ---------- PC ----------
PC_MAIN = [
    "🖥️ Para PC/Windows, baixe o app por este link:",
    "https://7aps.online/iptvsmarters",
    "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
]

# ---------- Pós-login ----------
POS_OK = ["Perfeito! Aproveite seu teste. 😊"]

POS_NOK = [
    "Vamos resolver isso!",
    "Confira se digitou *exatamente* como enviado.",
    "Atenção às *letras maiúsculas e minúsculas* e caracteres parecidos: *I* (i maiúsculo) × *l* (L minúsculo), *O* (letra) × *0* (zero).",
    "Pode me enviar uma *foto da tela* mostrando como você está digitando? 📷"
]

# ---------- Fluxos específicos ----------
DUPLECAST_PASSO = [
    "Certo! No *Duplecast*, siga:",
    "Start ➜ Português ➜ Brasil ➜ Fuso horário *-03* ➜ *Minha duplecast*.",
    "Depois, envie uma *foto do QR code* de perto.",
    "Em seguida, digite **871** aqui na conversa para eu gerar o teste (link M3U)."
]

DUPLECAST_JA_TEM = [
    "Perfeito! Se você *já tem* o Duplecast:",
    "Envie uma *foto do QR code* de perto e depois digite **871** aqui na conversa."
]

SMARTONE = [
    "No *SmartOne*, me envie o **MAC** (ou uma *foto da tela com o MAC*).",
    "Depois disso, digite **871** aqui para eu gerar o teste."
]

OTTPLAYER = [
    "No *OTT Player*, me envie uma *foto do QR code* de perto.",
    "Em seguida, digite **871** aqui para eu gerar o teste."
]

FOTO_QUAL_APP = [
    "Entendi a foto/QR/MAC!",
    "Como não consigo identificar imagens aqui, me diga por favor *qual aplicativo* você está usando:",
    "• Duplecast\n• SmartOne\n• OTT Player\n• Xcloud (ícone verde e preto)\n• Xtream IPTV Player\n• 9Xtream\n• XCIPTV\n• IPTV Stream Player"
]

# ---------- Planos / pagamento ----------
VALORES = [
    "💰 *Planos disponíveis*:",
    "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00"
]

PAGAMENTO = [
    "💳 *Formas de pagamento*: Pix ou Cartão.",
    "Cartão (link seguro): https://mpago.la/2Nsh3Fq",
    "Vou te mandar o *Pix (CNPJ)* em uma mensagem separada para facilitar a cópia."
]

PIX_SOZINHO = ["Pix (CNPJ): 46.370.366/0001-97"]

AUDIO_MSG = [
    "Ops! 😅 Por aqui eu não consigo interpretar *áudios*.",
    "Pode me mandar por *texto*? Eu continuo te ajudando normalmente!"
]

# ===================== SESSÃO POR CONTATO =====================

sessions = {}  # numero -> {"msgs": [...], "ctx": None}

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

    # Inicia sessão
    if numero not in sessions:
        sessions[numero] = {"msgs": [], "ctx": None}
        return jsonify({"replies": bubbles(MSG_BEM_VINDO)})

    s = sessions[numero]
    s["msgs"].append(f"Cliente: {m}")
    contexto = "\n".join(s["msgs"][-15:])

    # ---------- Pós-login ----------
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify({"replies": bubbles(*POS_OK)})

    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify({"replies": bubbles(*POS_NOK)})

    # ---------- Áudio ----------
    if "áudio" in m or "audio" in m:
        return jsonify({"replies": bubbles(*AUDIO_MSG)})

    # ---------- Imagem/QR/MAC ----------
    if any(k in m for k in KEY_FOTO):
        if s["ctx"] == "android":
            return jsonify({"replies": bubbles(*ANDROID_FOTO_FALLBACK)})
        else:
            return jsonify({"replies": bubbles(*FOTO_QUAL_APP)})

    # ---------- “Tem outro?” ----------
    if any(phrase in m for phrase in KEY_OUTRO):
        if s["ctx"] == "android":
            return jsonify({"replies": bubbles(*ANDROID_ALTS)})
        elif s["ctx"] == "xcloud":
            return jsonify({"replies": reply_list(bubbles(*XCLOUD_ALTS))})
        else:
            msg = "Me diga o modelo do aparelho (Android, Samsung/LG/Roku, iPhone ou PC) e te passo as opções certinhas. 😉"
            return jsonify({"replies": bubbles(msg)})

    # ===================== FLUXOS DETERMINÍSTICOS =====================

    # ANDROID (inclui Philips)
    if any(word in m for word in KEY_ANDROID):
        s["ctx"] = "android"
        return jsonify({"replies": bubbles(*ANDROID_MAIN)})

    # Dificuldade na loja / pedido de link
    if any(f in m for f in KEY_LINK_ALT):
        # só libera link se o contexto já é android ou a frase menciona android/tv box
        if s["ctx"] == "android" or any(w in m for w in KEY_ANDROID):
            # Tente insistir mais um pouco ensinando a loja, depois libera link
            return jsonify({"replies": reply_list(bubbles(*ANDROID_ENSINO_LOJA), bubbles(*ANDROID_LINK))})
        else:
            return jsonify({"replies": bubbles("O link direto é para *Android*. Seu aparelho é Android? Se for, te passo agora. 😉")})

    # XCLOUD (Samsung/LG/Roku/Philco nova)
    if any(word in m for word in KEY_XCLOUD_DEV):
        s["ctx"] = "xcloud"
        return jsonify({"replies": reply_list(bubbles(*XCLOUD_MAIN), bubbles(*XCLOUD_ALTS))})

    # PC / Windows
    if any(p in m for p in KEY_PC):
        s["ctx"] = "pc"
        return jsonify({"replies": bubbles(*PC_MAIN)})

    # Menciona explicitamente os apps
    if "duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": bubbles(*DUPLECAST_PASSO)})
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": bubbles(*DUPLECAST_JA_TEM)})
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": bubbles(*SMARTONE)})
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": bubbles(*OTTPLAYER)})

    # Cliente digitou algum código de teste
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": bubbles("🔓 Gerando seu login de teste, só um instante...")})

    # Planos / Pagamento
    if any(k in m for k in KEY_PAG):
        return jsonify({"replies": reply_list(bubbles(*VALORES), bubbles(*PAGAMENTO), bubbles(*PIX_SOZINHO))})

    # ===================== FALLBACK COM IA =====================
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. "
        "Responda curto, objetivo, com emojis, e nunca recomende apps fora desta lista: "
        "Xtream IPTV Player, 9Xtream, XCIPTV, IPTV Stream Player, "
        "Xcloud (ícone verde e preto), OTT Player, Duplecast, SmartOne, "
        "Smarters Player Lite (iOS) e IPTV Smarters para PC. "
        "Teste gratuito sempre 3 horas. Se falar de valores, envie os planos e depois Pix em mensagem separada. "
        "Se o cliente enviar foto/QR/MAC e o contexto for Android, diga '🔔 AÇÃO MANUAL NECESSÁRIA' e peça para aguardar; "
        "caso contrário, pergunte qual aplicativo ele usa. "
        "Para Android, enfatize Xtream IPTV Player e alternativas (9Xtream, XCIPTV, IPTV Stream Player). "
        "Se não encontrar na loja, ensine a procurar e só então ofereça o link http://xwkhb.info/axc.\n\n"
        f"Histórico recente:\n{contexto}\n\n"
        f"Mensagem do cliente: '{mensagem}'\n"
        "Responda em 2–4 frases curtas."
    )

    try:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        texto = result.choices[0].message.content.strip()
        return jsonify({"replies": bubbles(texto)})
    except Exception as e:
        return jsonify({"replies": bubbles(f"⚠️ Erro ao gerar resposta: {str(e)}")})

# ===================== RUN =====================

if __name__ == "__main__":
    # Porta 10000 para compatibilidade com seu Render
    app.run(host="0.0.0.0", port=10000)
