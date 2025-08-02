from flask import Flask, request, jsonify
from openai import OpenAI
import os
import threading
import time
import requests

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

historico_conversas = {}
usuarios_com_login_enviado = set()

WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

IMAGENS_APPS = {
    "xcloud": "https://telegra.ph/file/0fd4e48b6b2071a5bdfc3.jpg",
    "xtream iptv player": "https://telegra.ph/file/7d3b9e71c7bbcfaf9be86.jpg",
    "duplecast": "https://telegra.ph/file/1c4ad0a4f0a4ed3a02156.jpg",
    "smartone": "https://telegra.ph/file/9077557d6890d303b5f3c.jpg",
    "ott player": "https://telegra.ph/file/2f95c81f441a4c31a6d77.jpg",
    "smarters lite": "https://telegra.ph/file/e15223a3500e63141c915.jpg"
}

def enviar_mensagem(numero, texto):
    requests.post("https://api.autoresponder.chat/send", json={
        "number": numero,
        "message": texto
    })

def agendar_mensagens(numero):
    def enviar():
        time.sleep(1800)  # 30 minutos
        enviar_mensagem(numero, "Tudo certo até agora? Me avise se precisar de ajuda. 📺😉")
        time.sleep(5400)  # mais 1h30
        enviar_mensagem(numero, "⏰ Seu teste terminou. Vamos ativar seu acesso completo? Veja os planos abaixo 👇\n\n"
                                "📆 1 mês – R$ 26\n📆 2 meses – R$ 47\n📆 3 meses – R$ 68\n📆 6 meses – R$ 129\n📆 1 ano – R$ 185\n\n"
                                "Formas de pagamento:\n🔹 PIX (CNPJ): 12345678000199\n🔹 Cartão: https://pagamento.exemplo.com")
    threading.Thread(target=enviar).start()

def gerar_login(numero, dispositivo):
    if numero in usuarios_com_login_enviado:
        return

    webhook = WEBHOOK_SAMSUNG if "samsung" in dispositivo.lower() else WEBHOOK_GERAL

    try:
        requests.get(webhook)
        usuarios_com_login_enviado.add(numero)
        enviar_mensagem(numero, "🔓 Login gerado com sucesso! Digite o login no app com atenção às letras maiúsculas e minúsculas. "
                                "Cuidado com caracteres parecidos como O e 0, I e l. 👍")
        agendar_mensagens(numero)
    except Exception as e:
        enviar_mensagem(numero, f"⚠️ Erro ao gerar login: {str(e)}")

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    numero = query.get("from", "")
    mensagem = query.get("message", "").lower()

    resposta = []

    if numero not in historico_conversas:
        historico_conversas[numero] = {"dispositivo": "", "login_enviado": False}
        resposta.append({
            "message": "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
                       "Vamos começar seu teste gratuito?\n\n"
                       "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        })
    elif any(palavra in mensagem for palavra in ["samsung", "tv samsung"]):
        historico_conversas[numero]["dispositivo"] = "Samsung"
        resposta.append({
            "message": "Olá! Para assistir IPTV na sua Samsung, baixe o app *Xcloud* ➡️📱. "
                       "Assim que instalar, me avise para te enviar o login. 📺👍"
        })
        resposta.append({
            "message": f"[Imagem do app Xcloud]\n{IMAGENS_APPS['xcloud']}"
        })
    elif any(palavra in mensagem for palavra in ["android", "tv box", "celular", "projetor"]):
        historico_conversas[numero]["dispositivo"] = "Android"
        resposta.append({
            "message": "Para seu dispositivo Android, use o app *Xtream IPTV Player* ▶️📱. "
                       "Assim que instalar, me avise dizendo 'instalei' para te enviar o login. 😄"
        })
        resposta.append({
            "message": f"[Imagem do app Xtream IPTV Player]\n{IMAGENS_APPS['xtream iptv player']}"
        })
    elif any(palavra in mensagem for palavra in ["lg"]):
        historico_conversas[numero]["dispositivo"] = "LG"
        resposta.append({
            "message": "Na TV LG, baixe o app *Xcloud* 📺✅. Caso não funcione, me avise que te passo alternativas. 😉"
        })
        resposta.append({
            "message": f"[Imagem do app Xcloud]\n{IMAGENS_APPS['xcloud']}"
        })
    elif any(palavra in mensagem for palavra in ["roku"]):
        historico_conversas[numero]["dispositivo"] = "Roku"
        resposta.append({
            "message": "Para Roku, baixe o app *Xcloud* 🟩⬛. Me avise quando instalar. 📲"
        })
        resposta.append({
            "message": f"[Imagem do app Xcloud]\n{IMAGENS_APPS['xcloud']}"
        })
    elif any(palavra in mensagem for palavra in ["philco", "phillco"]):
        historico_conversas[numero]["dispositivo"] = "Philco"
        resposta.append({
            "message": "Na TV Philco, use o app *Duplecast* (com QR Code) ou *OTT Player*. Me diga qual escolheu! 📡📺"
        })
        resposta.append({
            "message": f"[Imagem Duplecast]\n{IMAGENS_APPS['duplecast']}"
        })
        resposta.append({
            "message": f"[Imagem OTT Player]\n{IMAGENS_APPS['ott player']}"
        })
    elif any(palavra in mensagem for palavra in ["smartone", "smart one"]):
        resposta.append({
            "message": "Ótimo! Me envie o MAC da sua TV para ativar. 🔠📺"
        })
        resposta.append({
            "message": f"[Imagem do app SmartOne]\n{IMAGENS_APPS['smartone']}"
        })
    elif any(palavra in mensagem for palavra in ["instalei", "baixei", "já instalei", "instalado"]):
        dispositivo = historico_conversas[numero].get("dispositivo", "")
        if dispositivo:
            resposta.append({"message": "Perfeito! Gerando seu acesso... 🔄"})
            gerar_login(numero, dispositivo)
        else:
            resposta.append({"message": "Qual dispositivo você está usando mesmo? 🤔"})
    else:
        resposta.append({"message": "Certo! Só preciso saber o modelo do seu aparelho (TV, celular, etc). Me diga, por favor. 📱📺"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(debug=True)
