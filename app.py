from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Webhook da Samsung nova (Xcloud)
WEBHOOK_SAMSUNG_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"

# Frases que indicam que o cliente instalou o app
gatilhos_instalacao = [
    "instalei", "já instalei", "instalado", "baixei", "já baixei", "app baixado", "pronto instalei"
]

@app.route("/autoreply", methods=["POST"])
def autoreply():
    data = request.get_json()
    mensagem = data.get("query", {}).get("message", "").lower()
    numero = data.get("query", {}).get("sender", "")

    # Verifica se a mensagem contém alguma das frases de instalação
    if any(g in mensagem for g in gatilhos_instalacao):
        try:
            # Envia a palavra "91" como se fosse o cliente
            r = requests.post(WEBHOOK_SAMSUNG_XCLOUD, json={"message": "91"})
            if r.status_code == 200:
                login = r.text.strip()
                if login:
                    return jsonify({"replies": [{"message": f"🔐 Pronto! Aqui está seu login de teste:\n\n{login}"}]})
                else:
                    return jsonify({"replies": [{"message": "⚠️ Erro: resposta vazia do servidor."}]})
            else:
                return jsonify({"replies": [{"message": "❌ Erro ao acessar o servidor. Tente novamente mais tarde."}]})
        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro técnico ao gerar login: {str(e)}"}]})

    # Se não for mensagem de instalação
    return jsonify({"replies": [{"message": "👍 Me avise quando instalar o app para eu gerar seu login de teste!"}]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
