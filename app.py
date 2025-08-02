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

    if message in ["instalei", "já instalei", "ja instalei", "instalei o app", "baixei"]:
        try:
            # Requisição à webhook 91
            response = requests.post(WEBHOOK_91, json={"query": {"from": sender, "message": "91"}})

            # Tenta converter para JSON
            try:
                conteudo = response.json()
            except Exception:
                return jsonify({
                    "replies": [{
                        "message": f"⚠️ Webhook respondeu com texto plano: {response.text[:200]}"
                    }]
                })

            # Se for lista de strings
            if isinstance(conteudo, list):
                replies = [{"message": msg} for msg in conteudo]
                return jsonify({"replies": replies})

            # Se for dicionário com 'replies'
            if isinstance(conteudo, dict) and "replies" in conteudo:
                return jsonify(conteudo)

            # Se for uma string simples
            if isinstance(conteudo, str):
                return jsonify({"replies": [{"message": conteudo}]})

            # Qualquer outro formato inesperado
            return jsonify({
                "replies": [{
                    "message": f"⚠️ Resposta inesperada da webhook:\n{str(conteudo)[:200]}"
                }]
            })

        except Exception as e:
            return jsonify({
                "replies": [{
                    "message": f"❌ Erro ao acessar a webhook:\n{str(e)}"
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
