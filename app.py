from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    user_message = data.get("query", {}).get("message", "").lower()
    sender_number = data.get("query", {}).get("sender", "")

    # Verifica se o cliente informou que instalou o app
    gatilhos = ["instalei", "baixei", "já instalei", "já baixei"]
    if any(g in user_message for g in gatilhos):
        # Simula o envio de "91" como se fosse o cliente
        payload = {
            "query": {
                "message": "91",
                "from": "cliente",
                "sender": sender_number
            }
        }
        try:
            resposta = requests.post(
                "https://a.opengl.in/chatbot/check/?k=66b125d558",
                json=payload,
                timeout=10
            )

            if resposta.status_code == 200:
                resposta_json = resposta.json()
                mensagens = resposta_json.get("replies", [])  # Assumindo esse formato
                if isinstance(mensagens, list):
                    return jsonify({"replies": mensagens})
                else:
                    return jsonify({"replies": [{"message": "❗Erro: resposta inesperada do servidor de login."}]})
            else:
                return jsonify({"replies": [{"message": "⚠️ Erro ao gerar login. Tente novamente mais tarde."}]})
        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro técnico: {str(e)}"}]})

    # Se não for um gatilho válido
    return jsonify({"replies": [{"message": "❗Envie 'instalei' quando terminar de baixar o app para gerar seu login."}]})


# Rota extra para compatibilidade com números como 91, 88 etc., se quiser manter.
@app.route("/autoreply", methods=["POST"])
def autoreply():
    return responder()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
