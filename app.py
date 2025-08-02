from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WEBHOOK_91 = "https://a.opengl.in/chatbot/check/?k=66b125d558"

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    sender = query.get("from", "")
    message = query.get("message", "").strip().lower()

    if message in ["instalei", "baixei", "já instalei", "ja instalei", "instalei o app"]:
        try:
            # Enviar "91" para a webhook, simulando o que o AutoReply faria
            response = requests.post(WEBHOOK_91, json={"query": {"from": sender, "message": "91"}})
            conteudo = response.json()

            # Verifica se a resposta da webhook é uma lista de strings
            if isinstance(conteudo, list):
                replies = [{"message": msg} for msg in conteudo]
                return jsonify({"replies": replies})

            # Caso a resposta seja um dict com 'replies', repassa direto
            if isinstance(conteudo, dict) and "replies" in conteudo:
                return jsonify(conteudo)

            # Se a resposta for apenas uma string simples
            if isinstance(conteudo, str):
                return jsonify({"replies": [{"message": conteudo}]})

            # Caso nenhuma das opções acima funcione
            return jsonify({
                "replies": [{
                    "message": "⚠️ Erro: formato de resposta inesperado da webhook."
                }]
            })

        except Exception as e:
            return jsonify({
                "replies": [{
                    "message": f"❌ Erro ao acessar a webhook: {str(e)}"
                }]
            })

    return jsonify({
        "replies": [{
            "message": "📲 Envie *instalei* quando terminar de baixar o app para liberar seu login de teste."
        }]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
