from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WEBHOOK_91 = "https://a.opengl.in/chatbot/check/?k=66b125d558"

@app.route("/", methods=["GET"])
def testar_webhook_91():
    teste_sender = "+5599999999999"  # Simula número fictício
    teste_payload = {
        "query": {
            "from": teste_sender,
            "message": "91"
        }
    }

    try:
        resposta = requests.post(WEBHOOK_91, json=teste_payload)
        conteudo = resposta.json()

        print("🔍 RESPOSTA DA WEBHOOK 91:")
        print(conteudo)

        return jsonify({"status": "ok", "mensagem": "Resposta da webhook impressa nos logs."})

    except Exception as e:
        print("❌ Erro ao testar webhook:")
        print(str(e))
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
