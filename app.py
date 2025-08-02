from flask import Flask, request, jsonify
import openai
import os
import re
import requests

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Mensagem inicial fixa
MENSAGEM_INICIAL = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# Histórico de conversa por cliente
historico_clientes = {}

# Função principal para responder com IA
def gerar_resposta_ia(mensagem, historico):
    prompt_base = """
Você é um atendente simpático e direto. Ajude o cliente a testar IPTV com o app ideal para o dispositivo dele. Nunca envie login direto. Oriente o cliente a DIGITAR um número conforme o dispositivo:

📺 Dispositivo → App + Número:
- TV Samsung (nova): Xcloud 📺⬇️📲 → login 91
- TV LG ou TV Roku: Xcloud 📺⬇️📲 → login 88
- TV Philco antiga ou Roku antiga: SmartSTB (vídeo, DNS, etc) → login 88
- TV Android (Box, TV, projetor): Xtream IPTV Player 📺⬇️📲 → login 555
- Celular Android: Xtream IPTV Player 📱⬇️📲 → login 555
- iPhone (iOS): Smarters Player Lite 📱⬇️📲 → login 555
- Computador (Windows): Smarters IPTV (link e tutorial) 🧑‍💻 → login 224

📌 Após indicar o app, diga:
“Me avise quando instalar para que eu envie o seu login.”

✅ Se o cliente disser que já instalou, diga:
“Digite *[número]* aqui na conversa para receber seu login. 😉”

⛔️ Só ofereça opções alternativas de apps Android (9Xtream Player, XCIPTV, VU IPTV Player, IPTV Xtream Play) se o cliente tiver dificuldade com Xtream IPTV Player.

⚠️ Após 30 minutos do login, envie algo como:
“Deu certo? Está funcionando bem aí? 😄”

ℹ️ Sempre alerte o cliente:
“Digite o login com atenção, pois letras como I, l, O e 0 podem confundir.”

💡 Responda dúvidas sobre IPTV, DNS, travamentos e uso dos apps de forma simples, humana e criativa.

Mensagem do cliente: """ + mensagem.strip()

    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=historico + [{"role": "user", "content": prompt_base}],
        temperature=0.7,
    )
    return resposta.choices[0].message.content.strip()

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    query = data.get("query", {})
    sender = query.get("from", "")
    mensagem = query.get("message", "").strip()

    # Histórico
    historico = historico_clientes.get(sender, [])

    # Envia mensagem de boas-vindas se for a primeira interação
    if sender not in historico_clientes:
        historico_clientes[sender] = []
        return jsonify({"replies": [{"message": MENSAGEM_INICIAL}]})

    try:
        resposta = gerar_resposta_ia(mensagem, historico)
        historico.append({"role": "user", "content": mensagem})
        historico.append({"role": "assistant", "content": resposta})
        historico_clientes[sender] = historico[-10:]  # Limita o histórico
        return jsonify({"replies": [{"message": resposta}]})
    except Exception as e:
        return jsonify({"replies": [{"message": f"⚠️ Erro ao responder: {str(e)}"}]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
