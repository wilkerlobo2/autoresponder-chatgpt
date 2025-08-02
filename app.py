from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Webhook usada para gerar login do código 91
WEBHOOK_91 = "https://a.opengl.in/chatbot/check/?k=66b125d558"

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    sender = query.get("from", "")
    message = query.get("message", "").strip().lower()

    # Detecta a palavra-chave 'instalei', 'baixei', etc. e envia a requisição 91 para gerar login
    if message in ["instalei", "baixei", "já instalei", "ja instalei", "instalei o app"]:
        try:
            # Requisição para webhook como se tivesse enviado '91'
            response = requests.post(WEBHOOK_91, json={"query": {"from": sender, "message": "91"}})
            if response.status_code == 200:
                resposta_login = response.json()
                return jsonify(resposta_login)
            else:
                return jsonify({
                    "replies": [{
                        "message": "⚠️ Erro ao gerar login. Tente novamente mais tarde."
                    }]
                })
        except Exception as e:
            return jsonify({
                "replies": [{
                    "message": f"⚠️ Erro: {str(e)}"
                }]
            })

    # Mensagem padrão para outros casos
    return jsonify({
        "replies": [{
            "message": "❗ Envie 'instalei' quando terminar de baixar o app para gerar seu login."
        }]
    })

# Correção de porta para funcionar no Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
