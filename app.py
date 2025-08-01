from flask import Flask, request, jsonify
import openai
import re
import requests
import os

app = Flask(__name__)

# Carrega a chave da variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")
print("🔑 Chave usada:", openai.api_key)  # Mostra no log do Render

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

def gerar_boas_vindas(nome):
    if nome.startswith("+55"):
        return (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
    return None

def gerar_login(webhook):
    try:
        r = requests.get(webhook, timeout=10)
        if r.status_code == 200:
            data = r.json()
            username = data.get("username", "")
            password = data.get("password", "")
            dns = data.get("dns", "")
            msg = f"*Usuário:* `{username}`\n*Senha:* `{password}`"
            if dns:
                msg += f"\n*DNS:* `{dns}`"

            aviso = ""
            if re.search(r"[IlO0]", username):
                aviso += "\n\n⚠️ *Atenção com o login:*\n"
                if "I" in username:
                    aviso += "✅ Letra *I* de *Índia*\n"
                if "l" in username:
                    aviso += "✅ Letra *l* minúscula de *lápis*\n"
                if "O" in username:
                    aviso += "✅ Letra *O* de *Ovo*\n"
                if "0" in username:
                    aviso += "✅ Número *0* (zero)\n"
                aviso += "Digite exatamente como enviado, respeitando maiúsculas e minúsculas."

            return msg + "\n\n⏳ *Seu teste dura 3 horas.*" + aviso
        else:
            return "❌ Erro ao gerar o login. Tente novamente em instantes."
    except Exception as e:
        print("Erro ao gerar login:", e)
        return "⚠️ Erro ao conectar com o servidor de testes."

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    nome = data.get("name", "")
    mensagem = data.get("message", "").lower()
    resposta = []

    boasvindas = gerar_boas_vindas(nome)
    if boasvindas:
        resposta.append({"message": boasvindas})
        return jsonify({"replies": resposta})

    # Prompt IA
    prompt = (
        f"O cliente enviou esta mensagem: '{mensagem}'\n\n"
        "Interprete com inteligência e responda conforme as regras abaixo:\n\n"
        "1. Se for novo, convide para teste grátis e peça o modelo do aparelho (TV, celular, etc).\n"
        "2. Se mencionar TV Roku, LG, Samsung, Philco ou similares, indique baixar o *Xcloud* (ícone verde e preto).\n"
        "3. Se mencionar Android, TV Box, Fire Stick, Projetor ou Celular, indique o *Xtream IPTV Player*.\n"
        "4. Se mencionar iPhone, iOS ou Computador, indique o *Smarters Player Lite*.\n"
        "5. Se mencionar AOC ou Philips, indique *OTT Player* ou *Duplecast* e peça o QR code da tela.\n"
        "6. Se mencionar SmartOne, peça o código MAC.\n"
        "7. Se o cliente disser que já instalou (ex: 'instalei', 'baixei', 'pronto', 'foi'), gere o login via webhook.\n"
        f"   - Use {WEBHOOK_XCLOUD} se for Xcloud (Roku, Samsung, LG, etc).\n"
        f"   - Use {WEBHOOK_GERAL} para os demais.\n"
        "8. Sempre seja criativo e gentil, com linguagem humana e clara.\n"
        "9. Não peça para colar o login, diga 'digite o login'.\n"
        "10. Se a mensagem for 'deu certo', responda positivamente.\n"
        "11. Se for erro ou não funcionou, oriente a verificar e enviar print.\n"
        "12. Se disser que acabou o teste, envie os valores dos planos.\n"
        "13. Explique o que é IPTV se ele perguntar.\n\n"
        "Responda com a mensagem exata que o atendente deve enviar no WhatsApp. Apenas a resposta."
    )

    try:
        resposta_ia = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        texto = resposta_ia.choices[0].message["content"]

        # Cliente disse que instalou
        if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
            if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
                login = gerar_login(WEBHOOK_XCLOUD)
            else:
                login = gerar_login(WEBHOOK_GERAL)

            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
            resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        else:
            resposta.append({"message": texto})

    except Exception as e:
        print("❌ Erro no ChatCompletion:", e)
        resposta.append({"message": "⚠️ Ocorreu um erro: " + str(e)})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
