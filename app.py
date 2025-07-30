import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook do AutoResponder está ativo. Use POST para enviar mensagens."

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_message = data.get("query", {}).get("message", "")
        sender = data.get("query", {}).get("sender", "")

        if not user_message:
            return jsonify({"replies": [{"message": "Mensagem não encontrada"}]}), 400

        # Resposta simples de teste
        reply_1 = f"Olá {sender}, recebi sua mensagem: {user_message}"
        reply_2 = "Tudo certo com o webhook!"

        return jsonify({
            "replies": [
                {"message": reply_1},
                {"message": reply_2}
            ]
        })

    except Exception as e:
        return jsonify({"replies": [{"message": f"Erro no servidor: {str(e)}"}]}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


