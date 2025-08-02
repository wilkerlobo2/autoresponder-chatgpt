from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WEBHOOK_91 = "https://a.opengl.in/chatbot/check/?k=66b125d558"

@app.route("/", methods=["POST"])
def testar_envio_91():
    numero = "5511999999999"  # coloque um número real de teste

    # Corpo igual ao AutoReply
    payload = {
        "query": {
            "from": numero,
            "message": "91"
        }
    }

    try:
        response = requests.post(WEBHOOK_91, json=payload)
        print("🔁 Enviado:", payload)
        print("📨 Resposta:", response.text)
        return jsonify({"resposta_do_servidor": response.text})
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
