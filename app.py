from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
historico = {}

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "")
    mensagem = query.get("message", "").lower().strip()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})


    # Se for a primeira mensagem
    if numero not in historico:
        historico[numero] = []
        resposta.append({"message": "Olá! 👋 Me diga qual aparelho você vai usar (ex: TV Samsung, LG, Roku, Android...)?"})
        return jsonify({"replies": resposta})

    historico[numero].append(mensagem)

    # Se disser Samsung, indicar Xcloud
    if "samsung" in mensagem:
        resposta.append({"message": "Baixe o app Xcloud 📺👇️📲 para Samsung!\nMe avise quando instalar para que eu envie o seu login."})
        return jsonify({"replies": resposta})

    # Se disser que já instalou, simula envio do número 91 para webhook
    if any(palavra in mensagem for palavra in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei"]):
        try:
            # Envia o número 91 como requisição
            r = requests.get(WEBHOOK_SAMSUNG)
            if r.status_code == 200 and any(x in r.text.lower() for x in ["usuario", "usuário", "user", "senha", "password"]):
                login = r.text.strip()
                texto = f"🔑 Aqui está seu login de teste:\n\n{login}"
                resposta.append({"message": texto})
            else:
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente."})
        except Exception as e:
            resposta.append({"message": f"❌ Erro: {str(e)}"})

        return jsonify({"replies": resposta})

    # Mensagem genérica caso não reconheça
    resposta.append({"message": "❓ Não entendi. Por favor, diga o modelo da sua TV ou aparelho."})
    return jsonify({"replies": resposta})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
