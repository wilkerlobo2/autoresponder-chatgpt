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
    requests.post("https://api.autoresponder.chat/send", json={"number": numero, "message": texto})

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
        boas_vindas = (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
        return jsonify({"replies": [{"message": boas_vindas}]})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    if any(palavra in mensagem for palavra in ["instalei", "baixei", "pronto", "feito", "já instalei"]) and numero not in usuarios_com_login_enviado:
        historico = "\n".join(historico_conversas[numero])
        webhook = WEBHOOK_SAMSUNG if "samsung" in historico else WEBHOOK_GERAL

        try:
            r = requests.get(webhook)
            if r.status_code == 200:
                login = r.text.strip()
                aviso = (
                    "\n\n⚠️ Atenção aos caracteres parecidos: I (i maiúsculo), l (L minúsculo), "
                    "O (letra O), 0 (zero). Digite com cuidado!"
                )
                resposta.append({
                    "message": f"🔓 Pronto! Aqui está seu login de teste:\n\n{login}" +
                    (aviso if contem_caracteres_parecidos(login) else "")
                })
                usuarios_com_login_enviado.add(numero)
                historico_conversas[numero].append("IA: Login enviado")
                agendar_mensagens(numero)
            else:
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente."})
        except Exception as e:
            resposta.append({"message": f"⚠️ Erro na geração do login: {str(e)}"})

        return jsonify({"replies": resposta})

    # IA determina o app com emojis e orienta esperar instalação
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use emojis criativos sempre que indicar um aplicativo. NÃO envie links ou imagens. "
        "Quando o cliente disser o aparelho (ex: TV LG, Roku, iPhone), diga QUAL app ele deve baixar e diga a frase:\n\n"
        "'Baixe o app [NOME] 📺⬇️📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"
        "Histórico da conversa:\n" + contexto + f"\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
    )

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        texto = resposta_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
