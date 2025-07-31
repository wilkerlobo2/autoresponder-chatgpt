from flask import Flask, request, jsonify
import os
import random
import requests
from openai import OpenAI

app = Flask(__name__)

# Inicializando a API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Webhooks para geração de login IPTV
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_ANDROID = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Função para gerar login
def gerar_login(webhook_url):
    try:
        resposta = requests.get(webhook_url)
        dados = resposta.json()
        if isinstance(dados, list):
            mensagens = [{"message": msg} for msg in dados]
            return {"data": mensagens}
        return {"data": [{"message": "Erro: resposta do servidor fora do padrão."}]}
    except Exception as e:
        return {"data": [{"message": f"Erro ao gerar login: {str(e)}"}]}

# Função para decidir qual mensagem enviar
def responder_usuario(mensagem, nome):

    mensagem = mensagem.lower().strip()
    nome_salvo = not nome.startswith("+55")

    # Boas-vindas se for número desconhecido
    if not nome_salvo:
        return {"data": [{
            "message": (
                "Olá! 👋 Sou seu atendente virtual de IPTV.\n\n"
                "Temos canais ao vivo 📺, filmes 🎬, séries 📖 e muito mais!\n"
                "Qual é o modelo da sua TV ou dispositivo? (Ex: Samsung, LG, Android TV, iPhone...)"
            )
        }]}

    # Geração automática de login para Xcloud (TVs novas Samsung, LG, Roku, etc.)
    if "baixei" in mensagem or "já instalei" in mensagem or "já baixei" in mensagem:
        if "xcloud" in mensagem or "roku" in mensagem or "samsung" in mensagem or "lg" in mensagem:
            return gerar_login(WEBHOOK_XCLOUD)
        elif "android" in mensagem or "tv box" in mensagem or "smartphone" in mensagem:
            return gerar_login(WEBHOOK_ANDROID)
        elif "iphone" in mensagem or "ios" in mensagem or "computador" in mensagem:
            return gerar_login(WEBHOOK_ANDROID)
        elif "88" in mensagem:
            return {"data": [{
                "message": (
                    "📺 Para Samsung antiga, use o app Smart STB com os seguintes dados:\n"
                    "- DNS: 64.31.61.14\n"
                    "- Login: ***\n"
                    "- Senha: ***\n\n"
                    "Se precisar de ajuda, me avise!"
                )
            }]}
        else:
            return {"data": [{
                "message": "Perfeito! Gerando seu login agora... ⏳"
            }]}

    # Marca da TV informada
    if any(tv in mensagem for tv in ["samsung", "lg", "philco", "philips", "aoc", "roku"]):
        if "samsung" in mensagem:
            return {"data": [{
                "message": (
                    "Para TVs Samsung 📺, baixe o app *Xcloud* na loja da sua TV (ícone verde com preto).\n"
                    "Depois de instalar, me avise que eu gero seu acesso automático! 🔐"
                )
            }]}
        elif "lg" in mensagem:
            return {"data": [{
                "message": (
                    "📺 Na sua LG, baixe o app *Xcloud* (ícone verde com preto).\n"
                    "Se já tiver o app SmartOne instalado, envie o MAC.\n"
                    "Me avise quando o app estiver instalado para liberar o teste!"
                )
            }]}
        elif "philco" in mensagem:
            return {"data": [{
                "message": (
                    "Sua TV Philco é modelo novo ou antigo?\n"
                    "Se for antiga, digite o número 98 no WhatsApp para liberar o login de teste."
                )
            }]}
        elif "roku" in mensagem:
            return {"data": [{
                "message": (
                    "Para Roku, baixe o app *Xcloud* (ícone verde com preto).\n"
                    "Se não encontrar, posso te ajudar com outra opção. Me avise!"
                )
            }]}
        elif "philips" in mensagem or "aoc" in mensagem:
            return {"data": [{
                "message": (
                    "Essas TVs funcionam melhor com o app OTT Player ou Duplecast (com QR code).\n"
                    "Envie o QR code do app instalado e sigo com o teste!"
                )
            }]}

    # Solicitação direta de teste sem informações suficientes
    if "teste" in mensagem:
        return {"data": [{
            "message": (
                "Claro! 😊 Só preciso saber o modelo da sua TV ou dispositivo (ex: LG, Samsung, Android TV, iPhone...)\n"
                "Assim consigo indicar o melhor aplicativo pra você."
            )
        }]}

    # Default: usar IA para responder
    prompt = [
        {"role": "system", "content": (
            "Você é um atendente de IPTV. Sempre responda de forma educada e clara. "
            "Se o cliente disser que já baixou o app, gere o login de teste conforme o dispositivo. "
            "Evite enviar login sem confirmação do cliente. Use uma linguagem humana e útil."
        )},
        {"role": "user", "content": mensagem}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=prompt
        )
        resposta = completion.choices[0].message.content
        return {"data": [{"message": resposta}]}
    except Exception as e:
        return {"data": [{"message": f"Erro ao responder com IA: {str(e)}"}]}

# Rota principal
@app.route("/", methods=["POST"])
def home():
    try:
        dados = request.json
        mensagem = dados.get("message") or dados.get("query", {}).get("message") or ""
        nome = dados.get("sender") or dados.get("query", {}).get("sender") or "Cliente"
        return jsonify(responder_usuario(mensagem, nome))
    except Exception as e:
        return jsonify({"data": [{"message": f"Erro no servidor: {str(e)}"}]})

# Inicialização
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
