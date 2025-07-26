from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "Webhook do AutoResponder com ChatGPT está online! 🤖"

@app.route("/webhook", methods=["POST"])
def responder():
    data = request.get_json()
    mensagem = data.get("message")  # <-- recebendo diretamente

    if not mensagem:
        return jsonify({"erro": "Nenhuma mensagem recebida"}), 400

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem}],
            temperature=0.7,
            max_tokens=200
        )
        texto = resposta.choices[0].message.content.strip()
        return jsonify({"replies": [texto]})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run()
