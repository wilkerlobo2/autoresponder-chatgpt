from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def index():
    return 'Webhook online!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    query = data.get("query", {})
    numero = query.get("sender", "")
    mensagem = query.get("message", "").strip().lower()

    respostas = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # ✅ Reconhece "instalei" ou similares
    if any(palavra in mensagem for palavra in ["instalei", "baixei", "já instalei", "já baixei"]):
        respostas.append({
            "message": "✅ Que bom que já instalou!\n\nAgora digite o número *91* aqui no WhatsApp para ativar seu login de teste. 😉"
        })

    # ✅ Sugere aplicativo para Samsung, com emoji
    elif "samsung" in mensagem:
        respostas.append({
            "message": "📺 Sua TV é Samsung, né?\n\nBaixe o app *Xcloud* 📲⬇️ e me avise quando terminar a instalação pra liberar o login de teste."
        })

    # ✅ Para LG
    elif "lg" in mensagem:
        respostas.append({
            "message": "📺 Para TV LG, baixe o app *Xcloud* 📲⬇️. Caso não funcione, testamos o *Duplecast* ou *SmartOne*.\n\nMe avise quando instalar pra gente liberar o teste."
        })

    # ✅ Para Roku
    elif "roku" in mensagem:
        respostas.append({
            "message": "📺 Na Roku, baixe primeiro o app *Xcloud* 📲⬇️.\nSe não funcionar, testamos o *OTT Player* depois.\n\nMe avise quando instalar!"
        })

    # ✅ Para Android
    elif "android" in mensagem or "tv box" in mensagem or "projetor" in mensagem:
        respostas.append({
            "message": "📲 Para Android, baixe o app *Xtream IPTV Player* (ícone com losango laranja e roxo).\n\nMe avise quando instalar pra liberar o teste."
        })

    # ✅ Para iPhone
    elif "iphone" in mensagem or "ios" in mensagem:
        respostas.append({
            "message": "📱 Para iPhone, baixe o app *Smarters Player Lite* (ícone azul claro).\n\nDepois me avise com 'instalei' pra liberar o teste!"
        })

    # ✅ Para computador
    elif "computador" in mensagem or "pc" in mensagem or "notebook" in mensagem:
        respostas.append({
            "message": "🖥️ Para usar no computador, me avise que eu te passo o link do painel e login.\n\nMe diga apenas se prefere usar no navegador ou baixar o app."
        })

    # ✅ Caso diga apenas a marca da TV (ex: Philco)
    elif "philco" in mensagem:
        respostas.append({
            "message": "📺 Sua TV é Philco?\nSe for nova, usamos o app *Xcloud*. Se for antiga, talvez precise digitar o número *98* para ativar o teste.\n\nMe avise qual é o caso!"
        })

    elif mensagem in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]:
        respostas.append({
            "message": "👋 Olá! Oferecemos canais, filmes e séries via IPTV com teste grátis por 3 horas.\n\nQual é o seu dispositivo ou modelo de TV pra te indicar o melhor app?"
        })

    else:
        respostas.append({
            "message": "❓ Me diga qual é o seu modelo de TV ou dispositivo pra te indicar o app certo pra IPTV com teste grátis."
        })

    return jsonify({"replies": respostas})

# 🔁 Endpoint opcional para chamadas por número (AutoReply)
@app.route('/autoreply', methods=['POST'])
def autoreply():
    data = request.get_json()
    numero = data.get("number", "")
    respostas = []

    if numero == "91":
        respostas.append({
            "message": "✅ Login liberado! 🟢\n\n(use aqui a resposta automática que o AutoReply já retorna ao detectar o 91)."
        })
    elif numero == "88":
        respostas.append({
            "message": "🛠️ Instruções especiais para TV antiga liberadas."
        })
    else:
        respostas.append({
            "message": "❗Código inválido ou não reconhecido."
        })

    return jsonify({"replies": respostas})
