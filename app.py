from flask import Flask, request, jsonify
import openai
import requests
import random

app = Flask(__name__)

openai.api_key = "SUA_API_KEY_AQUI"

# Webhooks para geração automática de login
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_PADRAO = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

def gerar_login(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return data[0].get("message", "")
            return "Erro: resposta inválida do servidor de login."
        else:
            return f"Erro ao gerar login. Código: {response.status_code}"
    except Exception as e:
        return f"Erro ao gerar login automático: {str(e)}"

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    mensagem = data.get("query", {}).get("message", "").lower()
    nome = data.get("query", {}).get("sender", "cliente")

    if mensagem in ["oi", "olá", "bom dia", "boa tarde", "boa noite"]:
        return jsonify({"replies": [{"message": f"Olá! 👋 Seja bem-vindo(a)! Que tal fazer um teste grátis de IPTV com qualidade top? Qual é o modelo da sua TV ou aparelho?"}]})

    if "baixei" in mensagem or "já instalei" in mensagem or "pronto" in mensagem:
        numero = random.choice(["221", "225", "500", "555"])
        return jsonify({"replies": [{"message": f"Perfeito! 🙌 Agora digite o número *{numero}* aqui na conversa para eu gerar seu login de teste!"}]})

    if mensagem == "224":
        login = gerar_login(WEBHOOK_PADRAO)
        return jsonify({"replies": [{"message": login}]})

    if mensagem == "91":
        login = gerar_login(WEBHOOK_XCLOUD)
        return jsonify({"replies": [{"message": login}]})

    if mensagem == "88":
        resposta = (
            "Faça o procedimento do vídeo⬇️
"
            "https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0

"
            "Coloque a numeração ⬇️
DNS: 64.31.61.14

"
            "Depois de fazer o procedimento:
"
            "1 - Desligue a TV e ligue novamente
"
            "2 - Instale e abra o aplicativo *SMART STB*

"
            "*SEGUE OS DADOS PARA ACESSAR* ⬇️
"
            "*Usuário:* 👤 {USERNAME}
"
            "*Senha:* 🔐 {PASSWORD}
"
            "*3 horas de Teste*

"
            "*MENSALIDADE:* R$ 26,00
"
            "Se você gostou e quer assinar, digite *100*"
        )
        return jsonify({"replies": [{"message": resposta}]})

    return jsonify({"replies": [{"message": "🤖 Não entendi exatamente... me diga o modelo da sua TV ou se já baixou o app para começarmos o teste!"}]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
