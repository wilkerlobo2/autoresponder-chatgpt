from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========= util =========
DELAY_MS = 500  # 0.5s entre mensagens

def make_replies(blocks):
    """Converte lista de balões em replies com delay de 0.5s."""
    replies = []
    for i, msg in enumerate(blocks):
        if i == 0:
            replies.append({"message": msg})
        else:
            replies.append({"message": msg, "delay": DELAY_MS})
    return replies

# ========= constantes de texto =========
MSG_BEM_VINDO = [
    "Olá! 👋 Bem‑vindo(a)!",
    "Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿",
    "Vamos começar seu *teste gratuito*?",
    "Me diga qual aparelho você quer usar (ex: TV LG, Samsung, Roku, Philips, Android, iPhone, PC…)."
]

# ANDROID (inclui PHILIPS) — sem “detectado”
ANDROID_PREF = "⬇️ BAIXE *Xtream IPTV Player* (preferencial)."
ANDROID_ALT_TITLE = "✅ OUTRAS OPÇÕES (se preferir):"
ANDROID_ALT_LIST = "• *9Xtream*\n• *XCIPTV*\n• *IPTV Stream Player*"
ANDROID_INST = "Depois de instalar, me avise pra eu enviar seu login. 😉"
ANDROID_INSIST_1 = "Não achou na loja? Vamos tentar *outra opção* da lista acima."
ANDROID_INSIST_2 = "Se ainda assim *não conseguiu*, aí sim tem *link direto*:"
ANDROID_LINK = "🔗 http://xwkhb.info/axc\n(cole no navegador/Downloader/NTDOWN da sua TV Box/Android e o download inicia.)"
ANDROID_MANUAL = "🔔 *AÇÃO MANUAL NECESSÁRIA*: cliente usará o link. Enviar login quando avisar."

# XCLOUD (verde e preto) — sem “detectada”
XCLOUD_PREF = "Use o *Xcloud (ícone verde e preto)* 🟩⬛ *(preferencial).*"
XCLOUD_TESTE = "Instale e me avise para eu enviar seu login. ⏳ O teste gratuito dura *3 horas*."
XCLOUD_ALT_TITLE = "Se preferir, alternativas na sua TV:"
XCLOUD_ALT_LIST = "• *OTT Player*\n• *Duplecast*\n• *SmartOne*"
XCLOUD_ASK_APP = "Instale e me diga *qual app* escolheu pra eu te guiar certinho. 😉"

# PC
PC_MSG = [
    "🖥️ *PC/Windows*",
    "Baixe o app por este link:",
    "https://7aps.online/iptvsmarters",
    "Depois me avise quando abrir pra eu enviar seu login. 🙂"
]

# iPhone / iOS
IOS_MSG = [
    "🍏 *iPhone/iOS*",
    "Use o *Smarters Player Lite* (ícone azul, App Store).",
    "Quando instalar, me avise para eu enviar seu login. ⏳"
]

# Pós‑login
POS_OK = ["Tudo certo! ✅", "Aproveite seu teste. 😄"]
POS_FAIL = [
    "Vamos resolver! ⚙️",
    "Verifique se digitou *exatamente* como enviado.",
    "Atenção a *maiúsculas/minúsculas* e caracteres parecidos (*I/l*, *O/0*).",
    "Pode me enviar *foto da tela* mostrando como está digitando? 📷"
]

# Imagens / QR / MAC
FOTO_ANDROID = [
    "Recebi uma *imagem*. 👀",
    "Como estamos no *Android*, não dá para identificar a imagem aqui.",
    "🔔 *AÇÃO MANUAL NECESSÁRIA*: assim que concluir a instalação, me avise que eu envio o login. 😉"
]
FOTO_TV = [
    "Recebi uma *imagem*. 👀",
    "Como não identifico imagem aqui, me diga *qual aplicativo* você está usando:",
    "*Duplecast*, *SmartOne*, *OTT Player* ou *Xcloud (ícone verde e preto)*?"
]

# Fluxos específicos
DUPLECAST_STEPS = [
    "📲 *Duplecast*",
    "Siga: *Start → Português → Brasil → Fuso -03 → Minha duplecast*.",
    "Depois me envie *foto do QR* de perto. 👍",
    "Em seguida, digite **871** aqui na conversa (vou gerar seu teste *M3U*)."
]
DUPLECAST_HAVE = [
    "Perfeito! 👍",
    "Se você *já tem* o Duplecast, envie *foto do QR* de perto e depois digite **871**."
]
SMARTONE_STEPS = [
    "🧠 *SmartOne*",
    "Me envie o *MAC* (ou *foto da tela com o MAC*).",
    "Depois disso, digite **871** pra eu gerar seu teste."
]
OTT_STEPS = [
    "🎛️ *OTT Player*",
    "Me envie *foto do QR* de perto.",
    "Depois, digite **871** pra eu gerar seu teste."
]

# Planos / pagamento
PLANOS = [
    "💰 *Planos*",
    "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00"
]
PAGAMENTO = [
    "💳 *Pagamento*",
    "Pix ou Cartão (link seguro): https://mpago.la/2Nsh3Fq",
    "Vou mandar o *Pix (CNPJ)* *separado* pra facilitar a cópia."
]
PIX_SOLO = ["Pix (CNPJ): *46.370.366/0001-97*"]

# Palavras‑chave e contexto
CODIGOS_TESTE = {"224", "555", "91", "88", "871", "98", "94"}
KEY_OK = {"deu certo","acessou","funcionou","sim","consegui","tudo certo","abriu","logou"}
KEY_NOK = {"não","nao","n consegui","não funcionou","nao funcionou","n deu certo","nao deu certo","não deu certo"}
KEY_FOTO = {"foto","imagem","print","qrcode","qr code","qr-code","qr","mac:" ,"endereço mac","endereco mac","mostrei a tela"}
KEY_ANDROID = {"android","tv box","projetor","celular android","celular","philips"}
KEY_XCLOUD_DEVICES = {"samsung","lg","roku","philco nova","xcloud","tv samsung","tv lg","tv roku"}
KEY_PC = {"pc","computador","notebook","windows","macbook"}
KEY_IOS = {"iphone","ios","ipad"}
KEY_LINK_ALT = {
    "não consigo baixar","nao consigo baixar","não acho na loja","nao acho na loja",
    "não encontra na loja","nao encontra na loja","não tem na loja","nao tem na loja",
    "tem link","manda o link","baixar por link","link alternativo","apk","aptoide","ntdown","downloader","não achei","nao achei"
}
KEY_OUTRO = {"tem outro","quero outro","outro app","tem mais algum","tem mais opções","tem mais uma opção","não tem esse","nao tem esse"}
KEY_PAG = {"pix","pagamento","valor","quanto","plano","planos","preço","preco"}

# sessões (histórico + contexto)
sessions = {}  # numero -> {"msgs": [...], "ctx": None}

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender","").strip()
    mensagem = query.get("message","").strip()
    m = mensagem.lower()

    if not numero or not mensagem:
        return jsonify({"replies": make_replies(["⚠️ Mensagem inválida recebida."])})

    # cria sessão
    if numero not in sessions:
        sessions[numero] = {"msgs": [], "ctx": None}
        return jsonify({"replies": make_replies(MSG_BEM_VINDO)})

    s = sessions[numero]
    s["msgs"].append(f"Cliente: {m}")
    contexto = "\n".join(s["msgs"][-20:])

    # pós‑login
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify({"replies": make_replies(POS_OK)})
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify({"replies": make_replies(POS_FAIL)})

    # foto/qr/mac – depende do contexto
    if any(k in m for k in KEY_FOTO):
        if s["ctx"] == "android":
            return jsonify({"replies": make_replies(FOTO_ANDROID)})
        else:
            return jsonify({"replies": make_replies(FOTO_TV)})

    # “tem outro?”
    if any(k in m for k in KEY_OUTRO):
        if s["ctx"] == "android":
            blocks = [ANDROID_ALT_TITLE, ANDROID_ALT_LIST, ANDROID_INST]
            return jsonify({"replies": make_replies(blocks)})
        if s["ctx"] == "xcloud":
            blocks = [XCLOUD_ALT_TITLE, XCLOUD_ALT_LIST, XCLOUD_ASK_APP]
            return jsonify({"replies": make_replies(blocks)})
        return jsonify({"replies": make_replies(
            ["Me diga o aparelho (Android, Samsung/LG/Roku, iPhone ou PC) que te passo as opções certinhas. 😉"]
        )})

    # ===== fluxos determinísticos =====

    # ANDROID (inclui Philips) — sem o balão “detectado”
    if any(w in m for w in KEY_ANDROID):
        s["ctx"] = "android"
        blocks = [ANDROID_PREF, ANDROID_ALT_TITLE, ANDROID_ALT_LIST, ANDROID_INST]
        return jsonify({"replies": make_replies(blocks)})

    # insistiu que não achou / quer link – só Android
    if any(w in m for w in KEY_LINK_ALT):
        if s["ctx"] == "android" or "android" in m or "philips" in m or "tv box" in m or "celular" in m:
            blocks = [ANDROID_INSIST_1, ANDROID_INSIST_2, ANDROID_LINK, ANDROID_MANUAL]
            return jsonify({"replies": make_replies(blocks)})
        else:
            return jsonify({"replies": make_replies(
                ["O link é para *Android*. Seu aparelho é Android? Se for, te passo agora o passo a passo. 😉"]
            )})

    # TVs que usam Xcloud — sem o balão “detectada”
    if any(w in m for w in KEY_XCLOUD_DEVICES):
        s["ctx"] = "xcloud"
        blocks = [XCLOUD_PREF, XCLOUD_TESTE, XCLOUD_ALT_TITLE, XCLOUD_ALT_LIST, XCLOUD_ASK_APP]
        return jsonify({"replies": make_replies(blocks)})

    # PC
    if any(w in m for w in KEY_PC):
        s["ctx"] = "pc"
        return jsonify({"replies": make_replies(PC_MSG)})

    # iOS
    if any(w in m for w in KEY_IOS):
        s["ctx"] = "ios"
        return jsonify({"replies": make_replies(IOS_MSG)})

    # apps específicos
    if "duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": make_replies(DUPLECAST_STEPS)})
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": make_replies(DUPLECAST_HAVE)})
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": make_replies(SMARTONE_STEPS)})
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"
        return jsonify({"replies": make_replies(OTT_STEPS)})

    # cliente digitou um dos códigos
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": make_replies(["🔓 Gerando seu login de teste, só um instante..."])})

    # planos/pagamento/pix
    if any(k in m for k in KEY_PAG):
        replies = make_replies(PLANOS) + make_replies(PAGAMENTO) + make_replies(PIX_SOLO)
        return jsonify({"replies": replies})

    # ===== fallback com IA =====
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Responda curto, objetivo e com emojis.\n"
        "Nunca recomende apps fora desta lista: Xtream IPTV Player, 9Xtream, XCIPTV, IPTV Stream Player, "
        "Xcloud (ícone verde e preto), OTT Player, Duplecast, SmartOne, Smarters Player Lite (iOS) e IPTV Smarters para PC.\n"
        "Android: ênfase no Xtream IPTV Player; só oferecer link http://xwkhb.info/axc se o cliente disser que não conseguiu/achou.\n"
        "Philips = Android. Samsung/LG/Roku usam Xcloud (verde e preto) com alternativas (OTT/Duplecast/SmartOne).\n"
        "Se mandar foto/QR/MAC: se contexto Android -> 'Ação Manual Necessária'; senão, pergunte qual app está usando.\n"
        "Teste sempre *3 horas*. Pix deve ir em mensagem separada se pedir pagamento.\n\n"
        f"Histórico recente:\n{contexto}\n\n"
        f"Mensagem: '{mensagem}'\n"
        "Responda em 1–2 frases."
    )
    try:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.4
        )
        texto = result.choices[0].message.content.strip()
        return jsonify({"replies": make_replies([texto])})
    except Exception as e:
        return jsonify({"replies": make_replies([f"⚠️ Erro ao gerar resposta: {str(e)}"])})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
