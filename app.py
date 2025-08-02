import os
import re
import json
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

# Inicialização do app Flask
app = Flask(__name__)

# Inicialização do cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Requisições fixas para geração automática de login
WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Mensagem de boas-vindas fixa
BOAS_VINDAS_FIXA = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# Histórico de conversas por usuário
usuarios = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"replies": [{"message": "Mensagem inválida recebida."}]})

    query = data["query"]
    numero = query.get("sender", "")
    mensagem = query.get("message", "").strip()

    # Se for um novo usuário, envia as boas-vindas fixas
    if numero not in usuarios:
        usuarios[numero] = []
        return jsonify({"replies": [{"message": BOAS_VINDAS_FIXA}]})

    # Salva mensagem do usuário no histórico
    usuarios[numero].append({"role": "user", "content": mensagem})

    # Monta o histórico com instruções fixas + mensagens anteriores
    historico = [
        {
            "role": "system",
            "content": (
                "Você é um atendente experiente de IPTV. "
                "Seu trabalho é conduzir de forma natural o atendimento com o cliente, "
                "ajudando desde a escolha do aplicativo até o envio do login de teste.\n\n"
                "Regras importantes:\n"
                "- Use sempre linguagem simples e criativa.\n"
                "- Sempre indique qual aplicativo deve ser usado para cada TV ou dispositivo, com emojis.\n"
                "- Aguarde o cliente instalar o app antes de gerar o teste.\n"
                "- Quando ele disser 'instalei', 'baixei', 'pronto', etc., gere o login automaticamente.\n"
                "- Para TV Samsung nova use o número 91 (webhook: https://a.opengl.in/chatbot/check/?k=66b125d558).\n"
                "- Para Android use o número 555 (webhook: https://painelacesso1.com/chatbot/check/?k=76be279cb5).\n"
                "- Para computador use o número 224 (webhook: https://painelacesso1.com/chatbot/check/?k=76be279cb5).\n"
                "- Para TVs antigas (Philco, AOC, etc.), use 88.\n"
                "- Você não deve enviar o número. Só diga algo como: “Gerando seu login…” e chame a URL da webhook.\n"
                "- Avise o cliente que após 30 minutos você vai perguntar se deu certo, e após 3 horas o teste acaba.\n"
                "- Sempre alerte sobre letras parecidas (I, l, O, 0) após enviar o login.\n"
                "- Se o cliente pedir planos, informe os valores após 3 horas.\n"
                "- NUNCA diga o tempo do teste no início.\n"
                "- Não repita perguntas. Não sugira apps errados.\n"
                "- Se o cliente já tiver o app instalado (ex: SmartOne), peça o MAC. Se for Duplecast, oriente o QR code.\n"
            ),
        }
    ] + usuarios[numero]

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-4",
            messages=historico,
        )
        texto = resposta_ia.choices[0].message.content.strip()
        usuarios[numero].append({"role": "assistant", "content": texto})
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"Erro ao processar: {str(e)}"}]})

@app.route("/autoreply", methods=["POST"])
def autoreply():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"replies": [{"message": "Requisição inválida."}]})

    mensagem = data["query"].get("message", "").strip()

    # Requisições manuais (por número, usadas via AutoReply)
    if mensagem == "91":
        resp = requests.get(WEBHOOK_SAMSUNG)
        return jsonify({"replies": [{"message": resp.text}]})

    elif mensagem in ["555", "224", "88"]:
        resp = requests.get(WEBHOOK_GERAL)
        return jsonify({"replies": [{"message": resp.text}]})

    return jsonify({"replies": [{"message": "Código inválido."}]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
