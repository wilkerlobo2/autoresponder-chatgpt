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
            # Enviar código "91" para webhook
            response = requests.post(WEBHOOK_91, json={"query": {"from": sender, "message": "91"}})

            # Espera resposta no formato: lista de strings
            if response.status_code == 200:
                conteudo = response.json()

                # Se for lista de strings, formatar como {"replies": [{"message": "..."}, ...]}
                if isinstance(conteudo, list):
                    respostas_formatadas = [{"message": texto} for texto in conteudo]
                    return jsonify({"replies": respostas_formatadas})

                # Se já estiver no formato correto
                elif isinstance(conteudo, dict) and "replies" in conteudo:
                    return jsonify(conteudo)

                # Qualquer outro formato
                else:
                    return jsonify({"replies": [{"message": "⚠️ Erro: formato inesperado da resposta."}]})
            else:
                return jsonify({"replies": [{"message": "⚠️ Erro ao gerar login. Código 91 falhou."}]})

        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro: {str(e)}"}]})

    return jsonify({
        "replies": [{
            "message": "❗ Envie 'instalei' quando terminar de baixar o app para gerar seu login."
        }]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
