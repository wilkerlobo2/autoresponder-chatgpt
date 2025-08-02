from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def autoresponder():
    data = request.get_json()
    query = data.get("query", {})
    message = query.get("message", "").strip().lower()

    if message in ["instalei", "já instalei", "baixei", "já baixei"]:
        try:
            # Envia mensagem 91 para a webhook
            webhook_url = "https://a.opengl.in/chatbot/check/?k=66b125d558"
            payload = {"message": "91"}
            headers = {"Content-Type": "application/json"}
            response = requests.post(webhook_url, json=payload, headers=headers)
            result = response.json()

            # Tenta pegar a primeira mensagem da resposta
            if isinstance(result, dict) and "data" in result:
                data_list = result.get("data", [])
                if isinstance(data_list, list) and len(data_list) > 0:
                    return jsonify({"replies": [{"message": data_list[0]}]})
                else:
                    return jsonify({"replies": [{"message": "⚠️ Nenhum dado retornado pela webhook."}]})
            elif isinstance(result, list):
                return jsonify({"replies": [{"message": result[0]}]})
            else:
                return jsonify({"replies": [{"message": f"⚠️ Resposta inesperada da webhook: {result}"}]})

        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro ao acessar webhook: {str(e)}"}]})

    else:
        return jsonify({"replies": [{"message": "📲 Envie *instalei* quando terminar de baixar o app para liberar seu login de teste."}]})


@app.route('/autoreply', methods=['POST'])
def fallback():
    return jsonify({"replies": [{"message": "✅ Webhook ativa."}]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
