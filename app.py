from flask import Flask, request, jsonify
from openai import OpenAI
import os
import requests
import threading
import time

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

historico_conversas = {}
usuarios_com_login_enviado = set()
usuarios_com_app_enviado = {}

WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

IMAGENS_APPS = {
    "xcloud": "https://telegra.ph/file/0fd4e48b6b2071a5bdfc3.jpg",
    "xtream iptv player": "https://telegra.ph/file/7d3b9e71c7bbcfaf9be86.jpg",
    "smarters lite": "https://telegra.ph/file/99eb88a01d01d4e3130d1.jpg",
    "duplecast": "https://telegra.ph/file/6bb209e086733a3dfd143.jpg",
    "smartone": "https://telegra.ph/file/1cf261e901f6478f43129.jpg",
    "ott player": "https://telegra.ph/file/27d3e1c6f87f5124eab93.jpg",
}

def enviar_mensagem(numero, texto):
    requests.post("https://api.autoresponder.chat/send", json={
        "number": numero,
        "message": texto
    })

def enviar_imagem(numero, url):
    requests.post("https://api.autoresponder.chat/send", json={
        "number": numero,
        "image": url
    })

def agendar_mensagens(numero):
    def lembretes():
        time.sleep(1800)
        enviar_mensagem(numero, "⏳ O teste está rolando há 30 min. Deu tudo certo com o app? Precisa de ajuda?")
        time.sleep(5400)
        enviar_mensagem(numero, "⌛ O teste terminou! Espero que tenha curtido! 😄 Veja nossos planos e aproveite 📺🎉")
    threading.Thread(target=lembretes).start()

def contem_caracteres_parecidos(texto):
    return any(c in texto for c in ['I', 'l', 'O', '0'])

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip().lower()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    if numero not in historico_conversas:
        historico_conversas[numero] = []
        resposta.append({"message": "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n\nVamos começar seu teste gratuito?\n\nMe diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."})
        historico_conversas[numero].append(f"Cliente: {mensagem}")
        return jsonify({"replies": resposta})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    if any(palavra in mensagem for palavra in ["instalei", "baixei", "já tenho", "já está instalado"]) and numero not in usuarios_com_login_enviado:
        historico = "\n".join(historico_conversas[numero])
        if "samsung" in historico:
            webhook = WEBHOOK_SAMSUNG
        else:
            webhook = WEBHOOK_GERAL

        try:
            r = requests.get(webhook)
            if r.status_code == 200:
                login = r.text.strip()
                aviso = "\n\n⚠️ Atenção aos caracteres parecidos: I (i maiúsculo), l (L minúsculo), O (letra O), 0 (zero). Digite com atenção!"
                resposta.append({"message": f"🔓 Pronto! Aqui está seu login de teste:\n\n{login}" + (aviso if contem_caracteres_parecidos(login) else "")})
                usuarios_com_login_enviado.add(numero)
                agendar_mensagens(numero)
                historico_conversas[numero].append("IA: Login enviado")
            else:
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente em instantes."})
        except Exception as e:
            resposta.append({"message": f"⚠️ Erro na geração do login: {str(e)}"})
        return jsonify({"replies": resposta})

    prompt = (
        "Você está atendendo um cliente via WhatsApp sobre IPTV.\n"
        "Seja direto, breve e com linguagem simples (estilo linha de produção).\n"
        "Se o cliente disser o nome do dispositivo (Samsung, LG, Android, Roku, iPhone etc), diga claramente qual app usar.\n"
        "Sempre diga com firmeza: 'Baixe o app Xcloud 📲', e não 'recomendo'.\n"
        "Inclua o nome do app e envie a imagem correspondente.\n"
        "Só envie o login depois que o cliente disser 'instalei', 'baixei', etc.\n"
        "Não repita perguntas. Não pergunte o modelo se já souber pela conversa.\n\n"
        f"Histórico:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Responda de forma clara:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        texto = response.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})

        for nome_app, url_imagem in IMAGENS_APPS.items():
            if nome_app in texto.lower():
                enviar_imagem(numero, url_imagem)
                break

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
