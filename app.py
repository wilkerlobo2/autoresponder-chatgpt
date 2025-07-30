import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Cria o cliente OpenAI com a chave da API do ambiente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "Webhook do ChatGPT ativo. Use POST para enviar mensagens."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    user_message = data.get("senderMessage", "")  # Usa "senderMessage" que é o padrão do AutoReply

    if not user_message:
        return jsonify({"error": "Mensagem não encontrada"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um atendente educado e prestativo."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Retorno esperado pelo AutoReply
        return jsonify({
            "data": [
                {"message": reply}
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
