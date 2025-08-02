from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SEU_NUMERO_WHATSAPP = "5598999999999"  # Substitua pelo seu número com DDI

def simular_envio_91(numero_cliente):
    url = "https://api.autoresponder.chat/send"
    payload = {
        "number": SEU_NUMERO_WHATSAPP,
        "message": "91",
        "sender": numero_cliente
    }
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    numero = query.get("from", "")
    mensagem = query.get("message", "").strip().lower()

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    if mensagem in ["instalei", "já instalei", "ja instalei", "baixei", "baixei o app"]:
        try:
            simular_envio_91(numero)
            return jsonify({"replies": [{
                "message": "🔄 Login de teste sendo gerado... Aguarde, em instantes você receberá os dados!"
            }]})
        except Exception as e:
            return jsonify({"replies": [{"message": f"❌ Erro ao gerar login: {str(e)}"}]})

    return jsonify({"replies": [{
        "message": "👋 Oi! Quando você instalar o app, envie *instalei* para liberar o login de teste. 📲"
    }]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
