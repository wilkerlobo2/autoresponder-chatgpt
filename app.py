import requests
import random
from flask import Flask, request, jsonify
import openai
import os

# Configurações
openai.api_key = os.getenv("OPENAI_API_KEY")

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_PADRAO = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

app = Flask(__name__)

usuarios = {}

def gerar_login(webhook):
    try:
        response = requests.get(webhook)
        data = response.json()
        username = data["username"]
        password = data["password"]
        return f"""🔓 *Login Criado com Sucesso!*

*Usuário:* 👤 {username}
*Senha:* 🔐 {password}
🔗 URL: http://p8p8.live

⏳ Teste válido por 3 horas.
📺 Aproveite e veja se funciona bem no seu dispositivo!

📌 *Dica:* Alguns canais como *Premiere, HBO Max, Disney+* só funcionam ao vivo!
"""
    except Exception as e:
        return f"⚠️ Erro ao gerar login: {str(e)}"

@app.route("/", methods=["POST"])
def responder():
    dados = request.json
    mensagem = dados["query"]["message"].strip()
    numero = dados["query"]["sender"]

    # Verifica se o cliente já tem app instalado
    if "já tenho" in mensagem.lower() or "já instalei" in mensagem.lower() or "baixei" in mensagem.lower():
        usuarios[numero] = {"app_instalado": True}
        return jsonify({
            "replies": [{
                "message": "✅ Que bom! Agora me diga qual número você vê aqui embaixo para gerar seu acesso:"
            }]
        })

    # Se o cliente mandar só número (221, 224, etc.)
    if mensagem in ["221", "225", "500", "555", "224", "91", "88", "98"]:
        if usuarios.get(numero, {}).get("app_instalado"):
            if mensagem == "91":
                login = gerar_login(WEBHOOK_XCLOUD)
                return jsonify({"replies": [{"message": login}]})
            elif mensagem == "224":
                login = gerar_login(WEBHOOK_PADRAO)
                return jsonify({"replies": [{"message": login}]})
            elif mensagem == "88":
                resposta = """📺 *Configuração Smart STB (Samsung antiga)*

🔧 Faça o procedimento do vídeo:
https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0

🔢 Coloque a numeração:
DNS: 64.31.61.14

⚙️ Depois de fazer o procedimento:
1 - Desligue a TV e ligue novamente  
2 - Instale e abra o aplicativo *SMART STB*

➖➖➖➖➖➖➖➖➖  
*SEGUE OS DADOS PARA ACESSAR:*  
*Usuário:* 👤 {USERNAME}  
*Senha:* 🔐 {PASSWORD}  
⏳ *3 horas de Teste*

💰 *MENSALIDADE:* R$ 26,00

Se você Gostou e quer assinar, digite: *100*
"""
                return jsonify({"replies": [{"message": resposta}]})
            else:
                login = gerar_login(WEBHOOK_PADRAO)
                return jsonify({"replies": [{"message": login}]})
        else:
            return jsonify({"replies": [{
                "message": "📲 Antes de gerar o login, me avise quando tiver instalado o aplicativo no seu dispositivo."
            }]})

    # Detecção por IA (ChatGPT)
    try:
        prompt = f"""Você é um atendente inteligente de suporte IPTV via WhatsApp.
Responda de forma natural, criativa e humanizada. Nunca envie login sem o cliente confirmar que já instalou o app.
Se o cliente disser que está com dúvida, oriente.
Se o cliente disser que baixou o app, oriente digitar 1 número aleatório entre: 221, 225, 500 ou 555 para gerar o login.

Mensagem do cliente: "{mensagem}" """

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        resposta = completion.choices[0].message["content"]
        return jsonify({"replies": [{"message": resposta}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"❌ Erro ao responder com IA: {str(e)}"}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
