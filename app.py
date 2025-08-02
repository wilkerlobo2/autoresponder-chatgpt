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

    # Verifica se o cliente disse que já instalou o app
    if message in ["instalei", "baixei", "já instalei", "ja instalei", "instalei o app"]:
        try:
            # Envia a mensagem '91' para a webhook
            response = requests.post(WEBHOOK_91, json={"query": {"from": sender, "message": "91"}})

            # Tenta interpretar o conteúdo como JSON
            conteudo = response.json()

            # DEBUG: imprime no terminal o que a webhook retornou
            print("🔎 RESPOSTA DA WEBHOOK 91:")
            print(conteudo)

            # Caso seja lista de strings, reestrutura para o formato esperado
            if isinstance(conteudo, list):
                mensagens = [{"message": msg} for msg in conteudo]
                return jsonify({"replies": mensagens})

            # Caso já venha no formato correto
            if isinstance(conteudo, dict) and "replies" in conteudo:
                return jsonify(conteudo)

            # Qualquer outro formato
            return jsonify({
                "replies": [{
                    "message": "⚠️ Erro: formato inesperado da resposta. Verifique o servidor de login."
                }]
            })

        except Exception as e:
            return jsonify({
                "replies": [{
                    "message": f"⚠️ Erro ao gerar login: {str(e)}"
                }]
            })

    # Mensagem padrão se ainda não instalou o app
    return jsonify({
        "replies": [{
            "message": "❗ Envie 'instalei' quando terminar de baixar o app para gerar seu login."
        }]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
