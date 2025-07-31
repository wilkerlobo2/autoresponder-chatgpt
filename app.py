from flask import Flask, request, jsonify import os import random from openai import OpenAI

app = Flask(name)

Inicializando a API da OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

Webhooks para geração de login IPTV

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558" WEBHOOK_PADRAO = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

Função para gerar login

def gerar_login(webhook): try: import requests r = requests.get(webhook) if r.status_code == 200: return r.text else: return "Ocorreu um erro ao gerar o login. Tente novamente em instantes." except Exception: return "Erro ao conectar com o servidor de testes. Tente novamente."

Função para resposta de boas-vindas

def mensagem_boas_vindas(): return ( "Olá! 👋 Sou seu assistente de IPTV! Temos canais ao vivo, filmes, séries e conteúdos incríveis para sua TV, celular ou computador. 📺🍿\n" "Me diga o modelo da sua TV ou dispositivo e eu vou te ajudar a instalar o melhor aplicativo e gerar seu teste grátis! 💡" )

Função para lidar com mensagens

@app.route("/", methods=["POST"]) def responder(): try: data = request.get_json()

# Compatibilidade com AutoResponder e AutoReply
    mensagem = data.get("message") or data.get("query", {}).get("message")
    nome = data.get("sender") or data.get("query", {}).get("sender")

    if not mensagem:
        return jsonify({"data": [{"message": "Mensagem inválida."}]})

    # Tratamento de número de comando direto (ex: 91, 224, 88, etc)
    if mensagem.strip().isdigit():
        if mensagem == "91":
            login = gerar_login(WEBHOOK_XCLOUD)
            return jsonify({"data": [{"message": login}]})
        elif mensagem in ["221", "225", "500", "555", "224"]:
            login = gerar_login(WEBHOOK_PADRAO)
            return jsonify({"data": [{"message": login}]})
        elif mensagem == "88":
            resposta = (
                "Faça o procedimento do vídeo:\n"
                "https://youtu.be/2ajEjRykzeU\n\n"
                "Coloque a numeração:\nDNS: 64.31.61.14\n\n"
                "Depois de fazer o procedimento:\n"
                "1 - Desligue a TV e ligue novamente\n"
                "2 - Instale e abra o aplicativo *SMART STB*\n\n"
                "*SEGUE OS DADOS PARA ACESSAR*"
            )
            return jsonify({"data": [{"message": resposta}]})

    # IA para atendimento automático
    prompt_sistema = (
        "Você é um assistente de atendimento de IPTV.\n"
        "Dê boas-vindas criativas e ofereça canais, filmes e séries.\n"
        "Peça o modelo da TV ou dispositivo.\n"
        "Se o cliente mencionar 'Samsung', assuma que é nova e indique o app Xcloud.\n"
        "Evite mandar login direto. Pergunte se o cliente já instalou o app.\n"
        "Apenas se o cliente disser que já instalou, envie UM número aleatório entre 221, 225, 500 ou 555.\n"
        "Para computador ou iPhone, use o login do número 224.\n"
        "Para Samsung antiga, use o login do número 88.\n"
        "Nunca diga que o teste dura 3 horas.\n"
    )

    chat = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": mensagem}
    ]

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=chat
    )

    resposta_ia = completion.choices[0].message.content
    return jsonify({"data": [{"message": resposta_ia}]})

except Exception as e:
    return jsonify({"data": [{"message": f"Erro ao responder com IA: {str(e)}"}]})

Inicialização

if name == "main": port = int(os.environ.get("PORT", 10000)) app.run(host="0.0.0.0", port=port)

