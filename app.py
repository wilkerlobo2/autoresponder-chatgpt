from flask import Flask, request, jsonify
import openai
import random
import requests

app = Flask(__name__)

# ✅ Configuração da API da OpenAI
openai.api_key = "SUA_CHAVE_OPENAI_AQUI"  # Substitua pela sua chave

# ✅ Webhooks para login automático
WEBHOOK_ANDROID = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"

# ✅ Mensagens prontas para cada número
mensagens_fixas = {
    "88": """Faça o procedimento do vídeo⬇️
https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0

Coloque a numeração ⬇️
DNS: 64.31.61.14

Depois de fazer o procedimento:
1 - Desligue e ligue a TV
2 - Instale e abra o app *SMART STB*

➖️➖️➖️➖️
*SEGUE OS DADOS PARA ACESSAR:* ⬇️
*Usuário:* 👤 {USERNAME}
*Senha:* 🔐 {PASSWORD}
*Tempo:* 3 horas de teste

*MENSALIDADE:* R$ 26,00
Se gostou e quiser assinar, *digite 100*
""",
}

# ✅ Função para gerar login
def gerar_login(webhook_url):
    try:
        resposta = requests.get(webhook_url, timeout=10)
        dados = resposta.json()
        username = dados.get("user", "usuario_teste")
        password = dados.get("pass", "senha_teste")
        return username, password
    except:
        return None, None

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    mensagem = data.get("query", {}).get("message", "").strip()
    nome = data.get("query", {}).get("sender", "Cliente")

    # Se for número de ativação (login)
    if mensagem in ["555", "221", "500", "225"]:
        username, password = gerar_login(WEBHOOK_ANDROID)
        if username:
            resposta = f"""*CPLAY*

*Usuário:* 👤 {username}
*Senha:* 🔐 {password}
*URL:* http://p8p8.live

⏳ Seu teste dura 3 horas!

Após 30 min envio mensagem pra saber se deu certo, tá bom? 😊"""
        else:
            resposta = "❌ Não consegui gerar o login. Tente novamente mais tarde."
        return jsonify({"replies": [{"message": resposta}]})

    elif mensagem == "91":  # Xcloud
        username, password = gerar_login(WEBHOOK_XCLOUD)
        if username:
            resposta = f"""✅ *Login Xcloud Gerado!*

*Usuário:* 👤 {username}
*Senha:* 🔐 {password}
*URL:* http://p8p8.live

⏳ Você tem 3 horas pra testar.

Depois me diga se funcionou certinho 😊"""
        else:
            resposta = "❌ Não consegui gerar o login do Xcloud. Tente novamente mais tarde."
        return jsonify({"replies": [{"message": resposta}]})

    elif mensagem == "224":
        username, password = gerar_login(WEBHOOK_ANDROID)
        resposta = f"""*CPLAY – iPhone (Smarters Player)*

*Usuário:* 👤 {username}
*Senha:* 🔐 {password}
*URL:* http://p8p8.live

⏳ Teste ativo por 3 horas!

Me avise se funcionar direitinho! 😉"""
        return jsonify({"replies": [{"message": resposta}]})

    elif mensagem == "88":
        username, password = gerar_login(WEBHOOK_ANDROID)
        resposta = mensagens_fixas["88"].format(USERNAME=username, PASSWORD=password)
        return jsonify({"replies": [{"message": resposta}]})

    else:
        # Se não for número fixo, usa a IA para interpretar a pergunta
        prompt = f"Cliente: {mensagem}\nAtendente IPTV:"
        try:
            resposta_ia = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um atendente simpático de IPTV que ajuda o cliente a escolher o app ideal para a TV e só gera o login quando ele disser que já instalou."},
                    {"role": "user", "content": prompt}
                ]
            )
            texto = resposta_ia.choices[0].message.content
            return jsonify({"replies": [{"message": texto}]})
        except Exception as e:
            return jsonify({"replies": [{"message": f"⚠️ Erro ao consultar IA: {str(e)}"}]})

# 🔥 Mantém o app rodando no Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
