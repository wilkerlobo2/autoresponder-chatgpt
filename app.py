import os
import json
import re
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mensagem fixa de boas-vindas
MENSAGEM_BOAS_VINDAS = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"replies": [{"message": "Mensagem inválida recebida."}]})

    query = data["query"]
    numero = query.get("sender", "")
    mensagem = query.get("message", "").strip()

    # Detecta início da conversa para enviar mensagem de boas-vindas
    if mensagem.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
        return jsonify({"replies": [{"message": MENSAGEM_BOAS_VINDAS}]})

    # Geração da resposta com a IA
    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um atendente de suporte IPTV. "
                        "Seu papel é orientar o cliente de forma clara, direta e natural, com frases curtas e eficientes. "
                        "Sempre que o cliente disser que já instalou o app, instrua a digitar o número correspondente: \n\n"
                        "- 91 → TV Samsung nova (Xcloud)\n"
                        "- 88 → TV antiga (Smart STB + DNS)\n"
                        "- 555 → Celular, TV Box ou Android TV\n"
                        "- 224 → Computador ou iPhone\n\n"
                        "Evite enviar o número diretamente. Deixe o cliente digitar. "
                        "Se o cliente estiver testando, após cerca de 30 minutos, pergunte se funcionou bem. "
                        "Após 3h, diga que o teste expirou e apresente os planos com emojis e criatividade. "
                        "Se o login tiver letras parecidas como I/l ou O/0, avise o cliente para digitar com atenção.\n\n"
                        "Apenas aja com base no que o cliente disser. Não peça informações desnecessárias. "
                        "Se ele disser 'já tenho o app Xcloud', apenas diga 'Perfeito! Pode digitar o número 91 para receber seu login de teste!'."
                    )
                },
                {"role": "user", "content": mensagem}
            ]
        )
        texto_resposta = resposta_ia.choices[0].message.content.strip()
        return jsonify({"replies": [{"message": texto_resposta}]})
    except Exception as e:
        return jsonify({"replies": [{"message": "Erro ao gerar resposta com IA."}]})


# Endpoint opcional para funcionar com números fixos (como 91, 555, 88 etc.)
@app.route("/autoreply", methods=["POST"])
def autoreply():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"replies": [{"message": "Mensagem inválida recebida."}]})

    query = data["query"]
    mensagem = query.get("message", "").strip()

    # Regras fixas para códigos específicos
    if mensagem == "91":
        return jsonify({"replies": [{"message": "Aguarde... Enviando seu login de teste para TV Samsung com app Xcloud 📺✅"}]})
    elif mensagem == "555":
        return jsonify({"replies": [{"message": "Aguarde... Enviando seu login de teste para Android (celular, TV box, etc.) 🤖✅"}]})
    elif mensagem == "88":
        return jsonify({"replies": [{"message": "Enviando login de teste via SMART STB! Instale o app e siga as instruções. 📺🛠️"}]})
    elif mensagem == "224":
        return jsonify({"replies": [{"message": "Gerando login de teste para computador ou iPhone! 💻📱"}]})
    else:
        return jsonify({"replies": [{"message": "Número inválido. Tente novamente."}]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
