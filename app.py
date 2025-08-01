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
    requests.post("https://api.autoresponder.chat/send", json={
        "number": numero,
        "message": texto
    })

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
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida. Tente novamente."}]})

    if numero not in historico_conversas:
        historico_conversas[numero] = []
        resposta.append({"message": "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\nVamos começar seu teste gratuito?\n\nMe diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."})
        historico_conversas[numero].append("IA: Enviou boas-vindas")
        return jsonify({"replies": resposta})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-20:])

    # Se o cliente disse que já instalou
    if any(palavra in mensagem for palavra in ["instalei", "baixei", "já tenho", "pronto"]) and numero not in usuarios_com_login_enviado:
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
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente em instantes."})
        except Exception as e:
            resposta.append({"message": f"⚠️ Erro na geração do login: {str(e)}"})
        return jsonify({"replies": resposta})

    # Se cliente mencionou Samsung, ofereça o Xcloud primeiro
    if "samsung" in mensagem and "xcloud" not in contexto.lower():
        historico_conversas[numero].append("IA: Indicou Xcloud para Samsung")
        return jsonify({"replies": [{
            "message": "Para usar IPTV na sua TV Samsung, baixe o app *Xcloud* (ícone verde e preto). Após instalar, me avise dizendo 'instalei' que gero seu acesso. 😉"
        }]})

    prompt = (
        "Você está atendendo um cliente no WhatsApp sobre IPTV. Seja educado, natural e útil.\n"
        "Se o cliente disser que já instalou o app, apenas diga que está gerando o login.\n"
        "Para Samsung, recomende o app Xcloud primeiro, sem mencionar outros.\n"
        "Só gere o login após o cliente confirmar que instalou o app.\n\n"
        f"Histórico:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Responda como se fosse um atendente real:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        texto = response.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
