import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai  # ✅ Correto para versões 1.0 ou superiores

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # ✅ Corrigido

@app.route("/", methods=["GET"])
def home():
    return "AutoResponder ChatGPT Flask App is running"

@app.route("/webhook", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    mensagem = query.get("message")
    sender = query.get("sender")

    if not mensagem:
        return jsonify({"replies": [{"message": "Mensagem não recebida."}]})

    try:
        resposta = openai.ChatCompletion.create(  # ✅ Corrigido
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem}],
            temperature=0.7,
            max_tokens=200
        )
        texto = resposta.choices[0].message.content.strip()
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"Erro ao processar: {str(e)}"}]})

if __name__ == "__main__":
    app.run()
