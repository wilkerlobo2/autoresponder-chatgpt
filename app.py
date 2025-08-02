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

def enviar_mensagem(numero, texto):
    payload = {"number": numero, "message": texto}
    requests.post("https://api.autoresponder.chat/send", json=payload)

def agendar_mensagens(numero):
    def lembretes():
        time.sleep(1800)
        enviar_mensagem(numero, "⏳ O teste já está rolando há 30 minutos. Deu tudo certo com o app? 😄")
        time.sleep(5400)
        enviar_mensagem(numero, "⌛ O teste terminou! Espero que tenha gostado. Temos planos a partir de R$26,00. Quer ver as opções? 💸📺")
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
        boas_vindas = (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
        return jsonify({"replies": [{"message": boas_vindas}]})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

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

    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Atenda de forma direta, objetiva e simpática como uma linha de produção. "
        "Sempre que o cliente mencionar o aparelho, diga com certeza qual app ele deve baixar (não use 'recomendo', use 'baixe o app ...'). "
        "Use emojis criativos. NÃO envie imagens ou links. Aguarde o cliente confirmar que instalou para só então dizer que irá gerar o login.\n\n"
        "Apps por dispositivo:\n"
        "- Samsung, LG, Roku, Philco nova → Xcloud 📺⬇️📲\n"
        "- Android, celular, TV Box → Xtream IPTV Player 🤖📲\n"
        "- iPhone ou computador → Smarters Player Lite 🍎💻\n"
        "- LG (caso Xcloud não funcione) → Duplecast 🔁 ou SmartOne 🟩 (se for SmartOne, peça o MAC)\n"
        "- AOC ou Philips → OTT Player 🧩 ou Duplecast 🔁 (peça QR code)\n"
        "- Philco antiga → usar app especial com código 98 🔢\n\n"
        f"Histórico:\n{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResposta:"
    )

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        texto = resposta_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
