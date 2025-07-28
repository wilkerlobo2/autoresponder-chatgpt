import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "AutoResponder ChatGPT Flask App is running"

@app.route("/webhook", methods=["POST"])
def responder():
    data = request.get_json()
    print("DADOS RECEBIDOS:", data)

    if not data or "query" not in data:
        print("FALHA: JSON inválido.")
        return jsonify({"replies": [{"message": "FALHA: JSON inválido."}]}), 400

    query = data.get("query", {})
    mensagem = query.get("message")
    sender = query.get("sender")

    print("MENSAGEM:", mensagem)
    print("SENDER:", sender)

    if not mensagem:
        print("FALHA: Mensagem não recebida.")
        return jsonify({"replies": [{"message": "FALHA: Mensagem não recebida."}]}), 400
    try:
        resposta = openai.Chat.Completion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem}],
            temperature=0.7,
            max_tokens=200
        )
        texto = resposta.choices[0].message.content.strip()
        return jsonify({"replies": [{"message": texto}]})

    except Exception as e:
        print("ERRO GPT:", str(e))
        return jsonify({"replies": [{"message": f"Erro ao processar: {str(e)}"}]}), 500

if __name__ == "__main__":
    app.run()
