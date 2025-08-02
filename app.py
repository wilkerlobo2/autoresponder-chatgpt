from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Webhooks para geração de login
WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
WEBHOOK_CODIGO_88 = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Mensagem de boas-vindas
MENSAGEM_INICIAL = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook ativo e rodando!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # Verifica se a estrutura da mensagem está correta
    if not data or "query" not in data:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]}), 400

    query = data["query"]
    message = query.get("message", "").strip()
    sender = query.get("from", "")
    nome = query.get("name", "")

    if not message:
        return jsonify({"replies": [{"message": "⚠️ Mensagem vazia recebida."}]}), 200

    # Resposta inicial se for saudação
    saudacoes = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]
    if message.lower() in saudacoes:
        return jsonify({"replies": [{"message": MENSAGEM_INICIAL}]}), 200

    # Cliente digita número 91
    if message == "91":
        try:
            r = requests.post(WEBHOOK_SAMSUNG, timeout=10)
            if r.status_code == 200:
                resposta = r.text.strip()
                if any(char in resposta for char in "IlO0"):
                    resposta += "\n\n⚠️ Atenção aos caracteres parecidos: 'I' maiúsculo, 'l' minúsculo, 'O' e '0'. Digite com cuidado!"
                return jsonify({"replies": [{"message": resposta}]}), 200
            else:
                return jsonify({"replies": [{"message": "❌ Erro ao gerar login (código 91). Tente novamente."}]}), 200
        except Exception as e:
            return jsonify({"replies": [{"message": f"❌ Erro ao gerar login: {str(e)}"}]}), 200

    # Cliente digita número 88 (TV antiga, STB, etc.)
    if message == "88":
        try:
            r = requests.post(WEBHOOK_CODIGO_88, timeout=10)
            if r.status_code == 200:
                resposta = r.text.strip()
                resposta += (
                    "\n\n📹 Veja o tutorial de instalação: https://youtu.be/Xm5cXvRGk2g\n"
                    "🌐 DNS: 1.1.1.1\n"
                    "🔁 Após instalar, desligue e ligue a TV.\n"
                    "💡 App: SMART STB\n"
                    "💳 Mensalidade: R$ 26,00\n\n"
                    "Se quiser assinar, digite *100* ✅"
                )
                return jsonify({"replies": [{"message": resposta}]}), 200
            else:
                return jsonify({"replies": [{"message": "❌ Erro ao gerar login (código 88)."}]}), 200
        except Exception as e:
            return jsonify({"replies": [{"message": f"❌ Erro ao gerar login: {str(e)}"}]}), 200

    # Cliente digita número 555
    if message == "555":
        try:
            r = requests.post(WEBHOOK_GERAL, timeout=10)
            if r.status_code == 200:
                resposta = r.text.strip()
                if any(char in resposta for char in "IlO0"):
                    resposta += "\n\n⚠️ Atenção aos caracteres parecidos: 'I', 'l', 'O', '0'. Digite com cuidado!"
                return jsonify({"replies": [{"message": resposta}]}), 200
            else:
                return jsonify({"replies": [{"message": "❌ Erro ao gerar login (código 555)."}]}), 200
        except Exception as e:
            return jsonify({"replies": [{"message": f"❌ Erro ao gerar login: {str(e)}"}]}), 200

    # Resposta padrão
    resposta_padrao = (
        "🤖 Estou aqui para ajudar com seu teste IPTV.\n"
        "Informe qual aparelho você usa (TV, celular, etc.) ou digite o número do login como *91*, *88* ou *555* se já estiver pronto!"
    )
    return jsonify({"replies": [{"message": resposta_padrao}]}), 200

# Para compatibilidade com chamadas diretas por número (ex: /autoreply?message=91)
@app.route("/autoreply", methods=["POST", "GET"])
def autoreply():
    message = request.args.get("message", "").strip()

    if message == "91":
        try:
            r = requests.post(WEBHOOK_SAMSUNG, timeout=10)
            return r.text, 200
        except:
            return "Erro ao gerar login", 200

    if message == "88":
        try:
            r = requests.post(WEBHOOK_CODIGO_88, timeout=10)
            return r.text, 200
        except:
            return "Erro ao gerar login", 200

    if message == "555":
        try:
            r = requests.post(WEBHOOK_GERAL, timeout=10)
            return r.text, 200
        except:
            return "Erro ao gerar login", 200

    return "Mensagem inválida", 200

if __name__ == "__main__":
    app.run()
