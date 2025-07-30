import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook do ChatGPT ativo. Use POST para enviar mensagens."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    user_message = data.get("senderMessage", "")  # Usa 'senderMessage' que é o padrão do AutoResponder

    if not user_message:
        return jsonify({"error": "Mensagem não encontrada"}), 400

    try:
        # Resposta simulada (sem usar OpenAI)
        reply = f"Mensagem recebida: {user_message}"

        return jsonify({
            "data": {
                "message": reply
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

