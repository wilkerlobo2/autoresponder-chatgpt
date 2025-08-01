from flask import Flask, request, jsonify
from openai import OpenAI
import os
import threading
import time
import requests

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

historico_conversas = {}
usuarios_com_login_enviado = set()

WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

IMAGENS_APPS = {
    "xcloud": "https://telegra.ph/file/f16e6f12bca2faed372d7.jpg",
    "duplecast": "https://telegra.ph/file/49689c1148710b86e0213.jpg",
    "smartone": "https://telegra.ph/file/97b991401cf652fc0912f.jpg",
    "ottplayer": "https://telegra.ph/file/42b6595692f1318a81cb4.jpg",
    "xtream": "https://telegra.ph/file/6c2e1446c4a4e229c9d83.jpg",
    "smarters": "https://telegra.ph/file/7032fd15ef1aa6580b9a2.jpg"
}

def enviar_mensagem(numero, texto, imagem=None):
    payload = {"number": numero, "message": texto}
    if imagem:
        payload["media"] = imagem
    requests.post("https://api.autoresponder.chat/send", json=payload)

def agendar_mensagens(numero):
    def lembretes():
        time.sleep(1800)
        enviar_mensagem(numero, "⏳ O teste já está rolando há 30 minutos. Deu tudo certo com o app?")
        time.sleep(5400)
        enviar_mensagem(numero, "⌛ O teste terminou! Temos planos a partir de *R$26,00*. Quer ver as opções?")
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
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida. Tente novamente."}]})

    if numero not in historico_conversas:
        historico_conversas[numero] = []
        boas_vindas = (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
        return jsonify({"replies": [{"message": boas_vindas}]})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    if "instalei" in mensagem and numero not in usuarios_com_login_enviado:
        historico = "\n".join(historico_conversas[numero])
        if "samsung" in historico:
            webhook = WEBHOOK_SAMSUNG
        else:
            webhook = WEBHOOK_GERAL

        try:
            r = requests.get(webhook)
            if r.status_code == 200:
                login = r.text.strip()
                aviso = "\n\n⚠️ Atenção aos caracteres parecidos: I (i maiúsculo), l (L minúsculo), O (letra O), 0 (zero). Digite com cuidado!"
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
        "Você está atendendo um cliente de IPTV no WhatsApp.\n"
        "Responda de forma curta, natural e objetiva. Tipo linha de produção.\n"
        "Se o cliente disser o modelo da TV, indique o app correto e envie o link da imagem do app junto.\n"
        "Se ele disser 'instalei' ou 'baixei', gere o login via webhook e envie.\n"
        "Use respostas simples e claras.\n\n"
        f"Histórico:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Responda:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        texto = response.choices[0].message.content.strip()

        imagem = None
        for chave, url in IMAGENS_APPS.items():
            if chave in texto.lower():
                imagem = url
                break

        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
        if imagem:
            resposta.append({"message": imagem})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
