import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Links das imagens dos apps
IMAGENS_APPS = {
    "xcloud": "https://telegra.ph/file/0fd4e48b6b2071a5bdfc3.jpg",
    "xtream iptv player": "https://telegra.ph/file/7d3b9e71c7bbcfaf9be86.jpg",
    "smartone": "https://telegra.ph/file/9edcc4d6b282ad5b36d64.jpg",
    "duplecast": "https://telegra.ph/file/b0ad40eb0fa0f4eb2dc91.jpg",
    "ott player": "https://telegra.ph/file/cf3c5e2d8a30fbb2f5f40.jpg",
    "smarters player lite": "https://telegra.ph/file/203eb88a26a8d35d0b246.jpg"
}

# Webhooks de geração de teste
WEBHOOKS = {
    "samsung": "https://a.opengl.in/chatbot/check/?k=66b125d558",
    "android": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "iphone": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "computador": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "roku": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "lg": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "philco": "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
}

# Histórico de conversas
historico_conversas = {}
status_clientes = {}

def enviar_imagem(numero, url):
    requests.post("https://api.autoresponder.chat/send-image", json={
        "number": numero,
        "url": url
    })

@app.route("/", methods=["POST"])
def receber_mensagem():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "")
    mensagem = query.get("message", "").strip().lower()
    resposta = []

    if numero not in historico_conversas:
        historico_conversas[numero] = []
        status_clientes[numero] = {"aguardando_instalacao": None}
        texto = (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
        resposta.append({"message": texto})
        return jsonify({"replies": resposta})

    historico_conversas[numero].append(f"Usuário: {mensagem}")

    if status_clientes[numero]["aguardando_instalacao"]:
        if any(palavra in mensagem for palavra in ["instalei", "baixei", "já tenho", "já está", "já usei"]):
            tipo = status_clientes[numero]["aguardando_instalacao"]
            url = WEBHOOKS.get(tipo)
            if url:
                try:
                    requests.get(url)
                    resposta.append({"message": "✅ Prontinho! Teste enviado. Digite o login no app e aproveite! 😉"})
                except Exception:
                    resposta.append({"message": "⚠️ Ocorreu um erro ao gerar seu teste. Tente novamente."})
            status_clientes[numero]["aguardando_instalacao"] = None
            return jsonify({"replies": resposta})

    try:
        prompt = f"""Você é um atendente de suporte IPTV. Responda com simplicidade e objetividade.
O cliente enviou: {mensagem}

Com base na mensagem, diga qual dispositivo ele quer usar. Responda da seguinte forma:
- Se mencionar Samsung, diga: "Olá! Para assistir IPTV na sua Samsung, baixe o app *Xcloud* ➡️📲. Assim que instalar, me avise para te enviar o login. 📺👍"
- Se for LG, diga: "Para assistir IPTV na sua LG, baixe o app *Xcloud* ➡️📲. Depois me avise dizendo 'instalei' que envio seu login. 😉"
- Se for Roku, diga: "Use o app *Xcloud* ➡️📲. Após instalar, diga 'instalei' que te envio o login. 🔓📺"
- Se for Android (celular, TV Box, projetor), diga: "Instale o app *Xtream IPTV Player* 📲 e me avise dizendo 'instalei' que envio seu login. 😄"
- Se for iPhone ou iPad, diga: "Baixe o *Smarters Player Lite* na App Store 📲. Após instalar, me avise que envio seu login."
- Se for Computador ou Notebook, diga: "Use o app *Xtream IPTV Player* (Windows). Me avise quando instalar para gerar o login. 💻"
- Se for Philco, diga: "Sua TV Philco pode usar o app *OTT Player* ou *Duplecast*. Escolha um e me avise após instalar! 😉"
- Sempre que possível, use emojis e linguagem simples.

Se não entender o dispositivo, peça que o cliente diga qual aparelho está usando (TV LG, Samsung, celular, etc).
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        texto = response.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})

        # Identificar qual app foi citado e salvar tipo
        for nome_app, url_imagem in IMAGENS_APPS.items():
            if nome_app in texto.lower():
                enviar_imagem(numero, url_imagem)
                if "samsung" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "samsung"
                elif "android" in mensagem or "xtream" in texto.lower():
                    status_clientes[numero]["aguardando_instalacao"] = "android"
                elif "iphone" in mensagem or "ios" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "iphone"
                elif "computador" in mensagem or "notebook" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "computador"
                elif "roku" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "roku"
                elif "philco" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "philco"
                elif "lg" in mensagem:
                    status_clientes[numero]["aguardando_instalacao"] = "lg"
                break

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

# ✅ Final correto para funcionar no Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
