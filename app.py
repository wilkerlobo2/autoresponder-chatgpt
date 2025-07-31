import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

WEBHOOK_ANDROID = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"

esperando_confirmacao = {}

def gerar_login(webhook):
    try:
        resposta = requests.get(webhook)
        if resposta.status_code == 200:
            dados = resposta.json()
            if isinstance(dados, list) and len(dados) > 0 and "message" in dados[0]:
                return dados[0]["message"]
        return "Erro ao gerar o login de teste."
    except Exception as e:
        return f"Erro na solicitação: {str(e)}"

@app.route("/", methods=["POST"])
def responder():
    dados = request.json
    nome = dados["query"].get("sender", "")
    mensagem = dados["query"].get("message", "").strip().lower()
    resposta = ""

    if nome.startswith("+55") and nome[3].isdigit():
        if mensagem in ["oi", "olá", "ola"]:
            resposta = (
                "Olá! 👋 Seja bem-vindo ao nosso atendimento inteligente.\n"
                "Qual é o seu modelo de TV ou dispositivo para que eu possa indicar o melhor app e número para teste? 📺"
            )
            return jsonify({"replies": [{"message": resposta}]})

    if mensagem == "91":
        login = gerar_login(WEBHOOK_XCLOUD)
        return jsonify({"replies": [{"message": login}]})

    if mensagem == "224":
        login = gerar_login(WEBHOOK_ANDROID)
        return jsonify({"replies": [{"message": login}]})

    if mensagem == "88":
        resposta = (
            "Faça o procedimento do vídeo:\n"
            "https://youtu.be/2ajEjRyKzeU?si=0mb5VYrokIJ_2-h00\n\n"
            "Coloque a numeração:\nDNS: 64.31.61.14\n\n"
            "Depois de fazer o procedimento:\n"
            "1 - Desligue a TV e ligue novamente\n"
            "2 - Instale e abra o aplicativo *SMART STB*\n\n"
            "*SIGA OS DADOS PARA ACESSAR!*"
        )
        return jsonify({"replies": [{"message": resposta}]})

    # Se mensagem for numérica e esperava confirmação
    if mensagem.isdigit() and esperando_confirmacao.get(nome):
        webhook = esperando_confirmacao[nome]
        del esperando_confirmacao[nome]
        login = gerar_login(webhook)
        return jsonify({"replies": [{"message": login}]})

    # Caso contrário, usa IA para responder
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de atendimento de IPTV. "
                        "Se o cliente disser que já baixou o app, peça que digite o número (escolhido aleatoriamente entre 221, 225, 500 ou 555). "
                        "Se disser só a marca da TV, pergunte mais detalhes para indicar o app correto. "
                        "Se for LG, Samsung, Roku ou Philco, siga a lógica fornecida. "
                        "Evite enviar login sem confirmação de que o app foi instalado."
                    ),
                },
                {"role": "user", "content": mensagem},
            ]
        )
        resposta_ia = completion.choices[0].message.content
        return jsonify({"replies": [{"message": resposta_ia}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"Erro ao responder com IA: {str(e)}"}]})

if __name__ == "__main__":
    import os  # já deve estar no topo do seu app.py

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
