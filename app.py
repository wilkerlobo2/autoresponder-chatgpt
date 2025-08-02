from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Webhook específica para Samsung (requisição 91)
WEBHOOK_URL = "https://a.opengl.in/chatbot/check/?k=66b125d558"

@app.route("/", methods=["POST"])
def index():
    data = request.get_json()
    
    message = data.get("message", "").lower()
    sender = data.get("sender", "")

    # Apenas responde se o cliente disser "instalei"
    if "instalei" in message:
        # Simula o envio da mensagem "91" como se fosse AutoReply
        payload = {
            "query": {
                "message": "91",
                "from": "cliente",
                "sender": sender
            }
        }

        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            result = response.json()

            # Extrai o conteúdo retornado da webhook
            replies = result.get("replies", [])
            if not replies or "message" not in replies[0]:
                raise ValueError("Login não retornado corretamente.")

            login = replies[0]["message"]

            # Mensagem final para o cliente
            final_message = f"""🔐 Pronto! Aqui está seu login de teste:

{login}

⚠️ Atenção aos caracteres parecidos: I (i maiúsculo), l (L minúsculo), O (letra O), 0 (zero). Digite com cuidado!
"""
            return jsonify({"replies": [{"message": final_message}]})

        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro ao gerar login: {str(e)}"}]})

    # Caso a mensagem não seja "instalei"
    return jsonify({"replies": [{"message": "❗ Envie 'instalei' quando terminar de baixar o app para gerar seu login."}]})


@app.route("/autoreply", methods=["POST"])
def autoreply():
    # Este endpoint é para compatibilidade futura com requisições diretas por número, como 91
    data = request.get_json()
    return jsonify({"replies": [{"message": "🔧 Endpoint /autoreply em modo de teste."}]})


if __name__ == "__main__":
    app.run()
