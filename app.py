from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Seu número (que tem o AutoReply ativado)
SEU_NUMERO_WHATSAPP = "seu_numero_completo_com_55"

# Função que simula o cliente enviando "91" para o seu número
def simular_cliente_enviando_91(numero_cliente):
    url_envio = "https://api.autoresponder.chat/send"
    payload = {
        "number": SEU_NUMERO_WHATSAPP,
        "message": "91",
        "sender": numero_cliente
    }
    print(f"Enviando '91' para {SEU_NUMERO_WHATSAPP}, como se fosse o cliente {numero_cliente}")
    return requests.post(url_envio, json=payload)

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    numero_cliente = query.get("from", "")
    mensagem = query.get("message", "").strip().lower()

    if not numero_cliente or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Se o cliente disser que já instalou
    if mensagem in ["instalei", "baixei", "já instalei", "ja instalei", "instalei o app"]:
        try:
            simular_cliente_enviando_91(numero_cliente)
            return jsonify({"replies": [{
                "message": "🔄 Gerando seu login de teste... Aguarde, em instantes ele será enviado aqui no WhatsApp! 📡"
            }]})
        except Exception as e:
            return jsonify({"replies": [{
                "message": f"⚠️ Erro ao solicitar login: {str(e)}"
            }]})

    # Mensagem padrão
    return jsonify({"replies": [{
        "message": "📲 Baixe o app recomendado para sua TV ou aparelho, e envie 'instalei' quando concluir!"
    }]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
