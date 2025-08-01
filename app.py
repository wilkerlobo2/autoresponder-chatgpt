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

# Webhooks
WEBHOOK_SAMSUNG = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Links das imagens dos apps
IMAGENS_APPS = {
    "xcloud": "https://telegra.ph/file/0fd4e48b6b2071a5bdfc3.jpg",
    "xtream": "https://telegra.ph/file/7d3b9e71c7bbcfaf9be86.jpg",
    "duplecast": "https://telegra.ph/file/581f0a7dd9999fa3a46a5.jpg",
    "smartone": "https://telegra.ph/file/37065e5f50f07f8d1c5e4.jpg",
    "ott": "https://telegra.ph/file/cd501aebfc0e9c5bc0c22.jpg",
    "smarters": "https://telegra.ph/file/37f6cd55d75b2194a9e63.jpg"
}

def enviar_mensagem(numero, texto, imagem=None):
    payload = {"number": numero, "message": texto}
    if imagem:
        payload["image"] = imagem
    requests.post("https://api.autoresponder.chat/send", json=payload)

def agendar_mensagens(numero):
    def lembretes():
        time.sleep(1800)
        enviar_mensagem(numero, "⏳ Olá! O teste já está rolando há 30 min. Deu tudo certo com o app?")
        time.sleep(5400)
        enviar_mensagem(numero, "⌛ O teste terminou! Espero que tenha gostado. Temos planos a partir de R$26,00. Quer ver as opções? 😄")
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
        boas_vindas = "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\nVamos começar seu teste gratuito?\n\nMe diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        return jsonify({"replies": [{"message": boas_vindas}]})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    # Verifica se já deve gerar o login
    if any(x in mensagem for x in ["instalei", "baixei", "pronto", "feito"]) and numero not in usuarios_com_login_enviado:
        historico = "\n".join(historico_conversas[numero])
        webhook = WEBHOOK_SAMSUNG if "samsung" in historico else WEBHOOK_GERAL

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
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente."})
        except Exception as e:
            resposta.append({"message": f"⚠️ Erro na geração do login: {str(e)}"})
        return jsonify({"replies": resposta})

    # Prompt com instruções inteligentes
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Atenda de forma direta, clara e simpática.\n"
        "Sempre que o cliente mencionar o aparelho, recomende o app correto e envie o nome e a imagem do app.\n\n"
        "Apps recomendados por dispositivo:\n"
        "- Samsung, LG, Roku, Philco nova → Xcloud\n"
        "- Android, Celular, TV Box → Xtream IPTV Player\n"
        "- iPhone ou computador → Smarters Player Lite\n"
        "- LG (caso não funcione o Xcloud) → Duplecast ou SmartOne (se SmartOne, peça o MAC)\n"
        "- AOC ou Philips → OTT Player ou Duplecast (peça QR code)\n"
        "- Philco antiga → usar app especial com código 98\n\n"
        "Se o cliente disser que já instalou, diga apenas 'Gerando seu acesso...'\n\n"
        f"Histórico da conversa:\n{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
    )

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        texto = resposta_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")

        # Identifica se o nome do app está na resposta e envia imagem
        imagens_enviadas = False
        for app, link in IMAGENS_APPS.items():
            if app in texto.lower():
                resposta.append({"message": texto})
                resposta.append({"message": link})
                imagens_enviadas = True
                break

        if not imagens_enviadas:
            resposta.append({"message": texto})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
