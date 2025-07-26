from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    mensagem = query.get("message")
    sender = query.get("sender")

    if not mensagem:
        return jsonify({"replies": [{"message": "Mensagem não recebida."}]}), 400

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem}],
            temperature=0.7,
            max_tokens=200
        )
        texto = resposta["choices"][0]["message"]["content"].strip()
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"Erro ao processar: {str(e)}"}]}), 500

@app.route("/", methods=["GET"])
def home():
    return "AutoResponder ChatGPT Flask App is running"

if __name__ == "__main__":
    app.run()
