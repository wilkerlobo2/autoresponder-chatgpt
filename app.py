from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    data = request.json
    query = data.get("query", {})
    numero = query.get("from", "")
    mensagem = query.get("message", "").strip().lower()

    if mensagem in ["instalei", "já instalei", "ja instalei", "baixei", "baixei o app"]:
        try:
            url = "https://api.autoresponder.chat/send"
            payload = {
                "number": "SEU_NUMERO",  # <- Substitua pelo seu número com DDI, ex: "5598999999999"
                "message": "91",
                "sender": numero
            }
            requests.post(url, json=payload)

            return jsonify({"replies": [{"message": "🔄 Gerando seu login de teste... Aguarde, em breve você receberá os dados!"}]})
        except Exception as e:
            return jsonify({"replies": [{"message": f"❌ Erro ao gerar login: {str(e)}"}]})
    
    return jsonify({"replies": [{"message": "👋 Quando instalar o app, envie *instalei* para liberar o login de teste."}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
