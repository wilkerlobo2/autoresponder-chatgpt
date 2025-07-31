from flask import Flask, request, jsonify
import os
import random
import requests
from openai import OpenAI

app = Flask(__name__)

# Inicializa cliente da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Webhooks
WEBHOOK_ANDROID = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"

# Função para gerar login
def gerar_login(link_webhook, numero):
    try:
        response = requests.get(f"{link_webhook}&n={numero}")
        if response.status_code == 200:
            return response.text
        return "Erro ao gerar login. Tente novamente."
    except:
        return "Erro ao acessar o servidor. Tente mais tarde."

# Função principal de atendimento com IA
def processar_mensagem(mensagem, nome_contato):
    msg = mensagem.lower()

    # Boas-vindas personalizadas
    if nome_contato.startswith("+55"):
        return [{
            "message": "Olá! Seja bem-vindo(a)! 👋\n\nTemos canais, filmes, séries e esportes ao vivo! Qual é o dispositivo que você deseja usar para testar nosso serviço IPTV?"
        }]

    # Se cliente mencionar TV Samsung
    if "samsung" in msg:
        return [{
            "message": "Para a TV Samsung, recomendamos o app *Xcloud* (ícone verde com preto). Ele está disponível na loja da sua TV. Após instalar, me avise para eu liberar o teste!"
        }]

    # Se cliente mencionar LG
    if "lg" in msg:
        return [{
            "message": "Para TVs LG, recomendamos primeiro o app *Xcloud* (verde com preto). Se não funcionar, temos também o *Duplecast* (com QR Code) ou *SmartOne* (com MAC). Já instalou algum desses? Me avise para seguirmos!"
        }]

    # Se cliente mencionar Roku
    if "roku" in msg:
        return [{
            "message": "Na sua Roku, use o app *Xcloud*. Já instalou? Se sim, me avise que libero o acesso para teste! Caso não funcione, temos o *OTT Player* como opção alternativa."
        }]

    # Se cliente mencionar iPhone, computador ou iOS
    if "iphone" in msg or "ios" in msg or "computador" in msg or "pc" in msg:
        return [{
            "message": "Para iPhone ou computador, baixe o app *Smarters Player Lite* (ícone azul). Assim que estiver instalado, me avise que libero o teste!"
        }]

    # Se cliente mencionar Android ou TV Box
    if "android" in msg or "tv box" in msg or "xtream" in msg:
        return [{
            "message": "Para Android ou TV Box, o melhor app é o *Xtream IPTV Player*. Também funciona com *9Xtream*, *XCIPTV* ou *IPTV Stream Player*. Instale e me avise para liberar o teste!"
        }]

    # Cliente já confirmou que baixou
    if "baixei" in msg or "instalei" in msg or "pronto" in msg:
        numero_aleatorio = random.choice([221, 225, 500, 555])
        return [{
            "message": f"Perfeito! 😊 Agora digite o número *{numero_aleatorio}* aqui para eu liberar o teste automático!"
        }]

    # Cliente digitou número do teste
    if any(n in msg for n in ["221", "225", "500", "555", "88"]):
        if "88" in msg:
            login = gerar_login(WEBHOOK_ANDROID, 88)
        elif any(n in msg for n in ["221", "225", "500", "555"]):
            login = gerar_login(WEBHOOK_XCLOUD, int(''.join(filter(str.isdigit, msg))))
        else:
            login = "Número inválido."
        return [{"message": f"✅ Aqui está seu login para teste:\n\n{login}\n\n🕐 Lembrando que o teste dura cerca de 3 horas.\n\nVolto em 30 minutos para ver se funcionou direitinho! 😉"}]

    # Mensagem padrão para dúvidas
    return [{
        "message": "Olá! Como posso te ajudar hoje com nosso serviço de IPTV? Me diga o dispositivo que você vai usar (Samsung, LG, Android, iPhone, Roku, etc.)."
    }]

# Rota principal
@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()

    # Compatível com AutoResponder (estrutura com "query")
    if "query" in data:
        msg = data["query"].get("message", "")
        nome = data["query"].get("sender", "")
    else:
        msg = data.get("senderMessage", "")
        nome = data.get("senderName", "")

    respostas = processar_mensagem(msg, nome)
    return jsonify({"replies": respostas})

# Teste rápido
@app.route("/", methods=["GET"])
def home():
    return "Servidor ativo! 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
