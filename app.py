from flask import Flask, request, jsonify
from openai import OpenAI
import os, json, time, re
import redis

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========= infra: redis =========
REDIS_URL = os.getenv("REDIS_URL", "")
rds = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None

def sess_key(num): return f"sess:{num}"
def events_key(num): return f"events:{num}"

def get_session(num):
    if not rds: return {"msgs": [], "ctx": None, "audio_count": 0, "loop_score": 0}
    raw = rds.get(sess_key(num))
    if not raw:
        s = {"msgs": [], "ctx": None, "audio_count": 0, "loop_score": 0}
        rds.set(sess_key(num), json.dumps(s), ex=60*60*24*2)  # 2 dias
        return s
    return json.loads(raw)

def save_session(num, s):
    if rds:
        rds.set(sess_key(num), json.dumps(s), ex=60*60*24*2)

def push_event(num, kind, payload=None):
    if not rds: return
    ev = {"t": time.time(), "kind": kind, "payload": payload or {}}
    rds.rpush(events_key(num), json.dumps(ev))
    rds.expire(events_key(num), 60*60*24*7)  # 7 dias

HELPDESK_WEBHOOK_URL = os.getenv("HELPDESK_WEBHOOK_URL", "")

# ========= util =========
DELAY_MS = 500  # 0.5s
def make_replies(blocks):
    replies = []
    for i, msg in enumerate(blocks):
        if i == 0:
            replies.append({"message": msg})
        else:
            replies.append({"message": msg, "delay": DELAY_MS})
    return replies

def handoff(num, reason, context_snapshot):
    """Sinaliza mão-humana e (opcional) dispara webhook externo."""
    push_event(num, "handoff", {"reason": reason, "ctx": context_snapshot})
    msg = [
        "🚨📣 *AÇÃO MANUAL NECESSÁRIA* 📣🚨",
        "Um atendente vai te ajudar em instantes. Obrigado pela paciência!"
    ]
    # webhook opcional para Inbox/CRM
    if HELPDESK_WEBHOOK_URL:
        try:
            import requests
            requests.post(HELPDESK_WEBHOOK_URL, json={
                "number": num, "reason": reason, "context": context_snapshot
            }, timeout=4)
        except Exception:
            pass
    return jsonify({"replies": make_replies(msg)})

# ========= balões / constantes =========
MSG_BEM_VINDO = [
    "Olá! 👋 Bem‑vindo(a)!",
    "Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿",
    "Vamos começar seu *teste gratuito*?",
    "Me diga qual aparelho você quer usar (ex: TV LG, Samsung, Roku, Philips, Android, iPhone, PC…)."
]

# Android (inclui Philips)
ANDROID_PREF = "⬇️ BAIXE *Xtream IPTV Player* (preferencial)."
ANDROID_ALT_TITLE = "✅ OUTRAS OPÇÕES (se preferir):"
ANDROID_ALT_LIST = "• *9Xtream*\n• *XCIPTV*\n• *IPTV Stream Player*"
ANDROID_INST = "Depois de instalar, me avise pra eu enviar seu login. 😉"
ANDROID_INSIST_1 = "Não achou na loja? Vamos tentar *outra opção* da lista acima."
ANDROID_INSIST_2 = "Se ainda assim *não conseguiu*, aí sim tem *link direto*:"
ANDROID_LINK = "🔗 http://xwkhb.info/axc\n(cole no navegador/Downloader/NTDOWN da sua TV Box/Android e o download inicia.)"
ANDROID_MANUAL = "🔔 *AÇÃO MANUAL NECESSÁRIA*: cliente usará o link. Enviar login quando avisar."

# Xcloud (verde e preto)
XCLOUD_PREF = "Use o *Xcloud (ícone verde e preto)* 🟩⬛ *(preferencial).*"
XCLOUD_TESTE = "Instale e me avise para eu enviar seu login. ⏳ O teste gratuito dura *3 horas*."
XCLOUD_ALT_TITLE = "Se preferir, alternativas na sua TV:"
XCLOUD_ALT_LIST = "• *OTT Player*\n• *Duplecast*\n• *SmartOne*"
XCLOUD_ASK_APP = "Instale e me diga *qual app* escolheu pra eu te guiar certinho. 😉"

# PC / iOS
PC_MSG = [
    "🖥️ *PC/Windows*",
    "Baixe o app por este link:",
    "https://7aps.online/iptvsmarters",
    "Depois me avise quando abrir pra eu enviar seu login. 🙂"
]
IOS_MSG = [
    "🍏 *iPhone/iOS*",
    "Use o *Smarters Player Lite* (ícone azul, App Store).",
    "Quando instalar, me avise para eu enviar seu login. ⏳"
]

# Pós-login
POS_OK  = ["Tudo certo! ✅", "Aproveite seu teste. 😄"]
POS_FAIL = [
    "Vamos resolver! ⚙️",
    "Verifique se digitou *exatamente* como enviado.",
    "Atenção a *maiúsculas/minúsculas* e caracteres parecidos (*I/l*, *O/0*).",
    "Pode me enviar *foto da tela* mostrando como está digitando? 📷"
]

# Imagens
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

# Específicos de app
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

# palavras‑chave
CODIGOS_TESTE = {"224","555","91","88","871","98","94"}
KEY_OK   = {"deu certo","acessou","funcionou","sim","consegui","tudo certo","abriu","logou"}
KEY_NOK  = {"não","nao","n consegui","não funcionou","nao funcionou","n deu certo","nao deu certo","não deu certo"}
KEY_FOTO = {"foto","imagem","print","qrcode","qr code","qr-code","qr","mac:","endereço mac","endereco mac","mostrei a tela"}
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
KEY_PEDIR_HUMANO = {"atendente","humano","pessoa","fala comigo","quero falar com uma pessoa"}

# ========= endpoint =========
@app.route("/", methods=["POST"])
def responder():
    data = request.get_json() or {}
    query = data.get("query", {})
    numero = (query.get("sender") or "").strip()
    mensagem = (query.get("message") or "").strip()
    media_url = query.get("mediaUrl")  # se o AutoResponder envia
    media_type = (query.get("type") or "").lower()

    if not numero or not mensagem:
        return jsonify({"replies": make_replies(["⚠️ Mensagem inválida recebida."])})

    s = get_session(numero)
    m = mensagem.lower()

    # log curto em memória/redis
    s["msgs"].append(f"Cliente: {m}")
    s["msgs"] = s["msgs"][-40:]  # mantém curto
    save_session(numero, s)
    contexto = "\n".join(s["msgs"])

    # ===== classificador leve =====
    # áudio -> incrementa contador e pode handoff
    if media_type in {"audio","ptt"} or "áudio" in m or "audio" in m:
        s["audio_count"] = s.get("audio_count", 0) + 1
        save_session(numero, s)
        if s["audio_count"] >= 2:
            return handoff(numero, "audio_excessivo", {"context": contexto})
        # primeira vez: pede texto
        return jsonify({"replies": make_replies([
            "😅 Por aqui eu não consigo interpretar *áudios*.",
            "Pode me mandar por *texto*? Assim sigo te ajudando rapidinho!"
        ])})

    # pedido explícito de humano
    if any(k in m for k in KEY_PEDIR_HUMANO):
        return handoff(numero, "pedido_explicito", {"context": contexto})

    # pós‑login
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_OK):
        return jsonify({"replies": make_replies(POS_OK)})
    if any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE) and any(k in m for k in KEY_NOK):
        return jsonify({"replies": make_replies(POS_FAIL)})

    # foto/qr/mac
    if media_url or any(k in m for k in KEY_FOTO):
        # guarda a última foto/qr/mac para o humano ver (evento)
        if media_url:
            push_event(numero, "media", {"type": media_type, "url": media_url})
        if s.get("ctx") == "android":
            return jsonify({"replies": make_replies(FOTO_ANDROID)})
        else:
            return jsonify({"replies": make_replies(FOTO_TV)})

    # “tem outro?”
    if any(k in m for k in KEY_OUTRO):
        if s.get("ctx") == "android":
            blocks = [ANDROID_ALT_TITLE, ANDROID_ALT_LIST, ANDROID_INST]
            return jsonify({"replies": make_replies(blocks)})
        if s.get("ctx") == "xcloud":
            blocks = [XCLOUD_ALT_TITLE, XCLOUD_ALT_LIST, XCLOUD_ASK_APP]
            return jsonify({"replies": make_replies(blocks)})
        return jsonify({"replies": make_replies(
            ["Me diga o aparelho (Android, Samsung/LG/Roku, iPhone ou PC) que te passo as opções certinhas. 😉"]
        )})

    # ===== fluxos determinísticos =====
    # ANDROID
    if any(w in m for w in KEY_ANDROID):
        s["ctx"] = "android"
        save_session(numero, s)
        blocks = [ANDROID_PREF, ANDROID_ALT_TITLE, ANDROID_ALT_LIST, ANDROID_INST]
        return jsonify({"replies": make_replies(blocks)})

    # link alternativo (só Android)
    if any(w in m for w in KEY_LINK_ALT):
        if s.get("ctx") == "android" or any(w in m for w in ["android","philips","tv box","celular"]):
            blocks = [ANDROID_INSIST_1, ANDROID_INSIST_2, ANDROID_LINK, ANDROID_MANUAL]
            return jsonify({"replies": make_replies(blocks)})
        else:
            return jsonify({"replies": make_replies(
                ["O link é para *Android*. Seu aparelho é Android? Se for, te passo agora o passo a passo. 😉"]
            )})

    # TVs com Xcloud
    if any(w in m for w in KEY_XCLOUD_DEVICES):
        s["ctx"] = "xcloud"
        save_session(numero, s)
        blocks = [XCLOUD_PREF, XCLOUD_TESTE, XCLOUD_ALT_TITLE, XCLOUD_ALT_LIST, XCLOUD_ASK_APP]
        return jsonify({"replies": make_replies(blocks)})

    # PC
    if any(w in m for w in KEY_PC):
        s["ctx"] = "pc"
        save_session(numero, s)
        return jsonify({"replies": make_replies(PC_MSG)})

    # iOS
    if any(w in m for w in KEY_IOS):
        s["ctx"] = "ios"
        save_session(numero, s)
        return jsonify({"replies": make_replies(IOS_MSG)})

    # apps específicos (SEM pedir 91 aqui; seguem regras próprias)
    if "duplecast" in m:
        s["ctx"] = "xcloud"; save_session(numero, s)
        return jsonify({"replies": make_replies(DUPLECAST_STEPS)})
    if "já tenho duplecast" in m or "ja tenho duplecast" in m:
        s["ctx"] = "xcloud"; save_session(numero, s)
        return jsonify({"replies": make_replies(DUPLECAST_HAVE)})
    if "smartone" in m or "smart one" in m:
        s["ctx"] = "xcloud"; save_session(numero, s)
        return jsonify({"replies": make_replies(SMARTONE_STEPS)})
    if "ott player" in m or "ottplayer" in m:
        s["ctx"] = "xcloud"; save_session(numero, s)
        return jsonify({"replies": make_replies(OTT_STEPS)})

    # códigos de teste
    if m.strip() in CODIGOS_TESTE:
        return jsonify({"replies": make_replies(["🔓 Gerando seu login de teste, só um instante..."])})

    # planos/pagamento/pix
    if any(k in m for k in KEY_PAG):
        replies = make_replies(PLANOS) + make_replies(PAGAMENTO) + make_replies(PIX_SOLO)
        return jsonify({"replies": replies})

    # ===== fallback com IA curta =====
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Responda curto, humano e com emojis.\n"
        "Apps permitidos: Xtream IPTV Player, 9Xtream, XCIPTV, IPTV Stream Player, "
        "Xcloud (verde e preto), OTT Player, Duplecast, SmartOne, Smarters Player Lite (iOS) e IPTV Smarters (PC).\n"
        "Android: ênfase no Xtream IPTV Player; só oferecer o link http://xwkhb.info/axc se o cliente disser que não conseguiu/achou.\n"
        "Philips=Android. Samsung/LG/Roku= Xcloud (verde e preto) + alternativas (OTT/Duplecast/SmartOne).\n"
        "Foto/QR/MAC: se contexto Android -> diga que não identifica e marque ação manual; senão, pergunte qual app.\n"
        "Teste sempre 3 horas. Pix vai em mensagem separada se pedir pagamento.\n\n"
        f"Histórico:\n{contexto}\n\n"
        f"Cliente: '{mensagem}'\n"
        "Responda em 1–2 frases."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        texto = resp.choices[0].message.content.strip()
        return jsonify({"replies": make_replies([texto])})
    except Exception as e:
        return jsonify({"replies": make_replies([f"⚠️ Erro ao gerar resposta: {str(e)}"])})

# opcional: endpoint de saúde
@app.route("/health", methods=["GET"])
def health():
    ok = True
    if rds:
        try:
            rds.ping()
        except Exception:
            ok = False
    return {"ok": ok}, 200 if ok else 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
