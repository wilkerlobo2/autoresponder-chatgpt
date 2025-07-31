from flask import Flask, request, jsonify
import openai
import requests
import re

app = Flask(__name__)
openai.api_key = "SUA_API_KEY_AQUI"

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

def cliente_novo(nome):
    return nome.startswith("+55")

def gerar_boas_vindas():
    return (
        "👋 Olá! Seja bem-vindo(a)! Aqui você tem acesso a *canais, filmes e séries* direto na sua TV ou celular.\n"
        "Vamos começar seu teste gratuito?\n\nMe diga qual é o seu dispositivo (TV ou celular) pra eu indicar o app ideal. 😉"
    )

def gerar_login(webhook_url):
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            username = dados.get("username", "")
            password = dados.get("password", "")
            dns = dados.get("dns", "")
            msg = f"🔓 *Login liberado:*\n👤 Usuário: `{username}`\n🔐 Senha: `{password}`"
            if dns:
                msg += f"\n🌐 DNS: `{dns}`"
            msg += "\n\n⏳ *Seu teste dura 3 horas.*"

            alerta = ""
            if re.search(r"[IlO0]", username):
                alerta += "\n\n⚠️ Atenção: seu login contém letras parecidas. Veja com cuidado:\n"
                if "I" in username:
                    alerta += "✔️ Letra *I* de *Índia*\n"
                if "l" in username:
                    alerta += "✔️ Letra *l* minúscula de *lápis*\n"
                if "O" in username:
                    alerta += "✔️ Letra *O* de *Ovo*\n"
                if "0" in username:
                    alerta += "✔️ Número *0* (zero)\n"
                alerta += "\nDigite exatamente como foi enviado, respeitando maiúsculas e minúsculas."
            return msg + alerta
        return "❌ Erro ao gerar login. Tente novamente em instantes."
    except:
        return "❌ Erro de conexão ao gerar o login. Tente mais tarde."

def detectar_dispositivo(msg):
    msg = msg.lower()
    if "roku" in msg:
        return "roku"
    elif "samsung" in msg:
        return "samsung"
    elif "lg" in msg:
        return "lg"
    elif "iphone" in msg or "ios" in msg or "computador" in msg:
        return "ios"
    elif "philco" in msg and "antiga" in msg:
        return "smart stb"
    elif "philco" in msg or "aoc" in msg or "philips" in msg:
        return "duplecast"
    elif any(palavra in msg for palavra in ["tv box", "android", "celular", "projetor", "fire stick"]):
        return "android"
    return None

@app.route("/", methods=["GET"])
def responder():
    nome = request.args.get("name", "")
    mensagem = request.args.get("message", "").lower()
    respostas = []

    if cliente_novo(nome) and "teste" in mensagem:
        respostas.append({"message": gerar_boas_vindas()})
        return jsonify({"replies": respostas})

    dispositivo = detectar_dispositivo(mensagem)

    if dispositivo == "roku" or dispositivo == "samsung" or dispositivo == "lg":
        respostas.append({"message": "✅ Baixe o app *Xcloud* (ícone verde com preto) na sua TV.\nMe avise quando tiver instalado para eu liberar o login!"})
        return jsonify({"replies": respostas})

    if dispositivo == "android":
        respostas.append({"message": "✅ Baixe o app *Xtream IPTV Player* no seu aparelho Android, TV Box, Fire Stick, etc.\nMe avise quando instalar para liberar o login!"})
        return jsonify({"replies": respostas})

    if dispositivo == "ios":
        respostas.append({"message": "✅ Baixe o app *Smarters Player Lite* no seu iPhone ou computador.\nMe avise quando instalar para liberar o login!"})
        return jsonify({"replies": respostas})

    if dispositivo == "duplecast":
        respostas.append({"message": "✅ Baixe o app *Duplecast IPTV* ou *OTT Player* na sua TV.\nEnvie a *foto do QR Code* da tela para eu liberar o acesso."})
        return jsonify({"replies": respostas})

    if dispositivo == "smart stb":
        respostas.append({"message": (
            "✅ Faça o procedimento do vídeo:\nhttps://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0\n\n"
            "*DNS:* `64.31.61.14`\n\nDepois:\n1 - Desligue e ligue a TV\n2 - Instale o app *SMART STB*\n\nMe avise que eu gero seu login!"
        )})
        return jsonify({"replies": respostas})

    if "instalei" in mensagem or "já instalei" in mensagem:
        if any(p in mensagem for p in ["xcloud", "roku", "samsung", "lg"]):
            login = gerar_login(WEBHOOK_XCLOUD)
        elif any(p in mensagem for p in ["iphone", "ios", "computador"]):
            login = gerar_login(WEBHOOK_GERAL)
        else:
            login = gerar_login(WEBHOOK_GERAL)

        respostas.append({"message": f"{login}"})
        respostas.append({"message": "⏳ Em breve pergunto se deu tudo certo. 😉"})
        return jsonify({"replies": respostas})

    if "não funcionou" in mensagem or "erro" in mensagem:
        respostas.append({"message": "🚫 Verifique se digitou corretamente, respeitando maiúsculas, minúsculas e sem espaços. Pode enviar uma *foto da tela* que eu te ajudo."})
        return jsonify({"replies": respostas})

    if "terminou o teste" in mensagem:
        respostas.append({"message": (
            "⏳ Seu teste foi encerrado!\n\nVeja nossos planos:\n"
            "✅ R$ 26,00 - 1 mês\n✅ R$ 47,00 - 2 meses\n✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n✅ R$ 185,00 - 1 ano\n\n"
            "*PIX:* 41.638.407/0001-26\nBanco C6 (CNPJ Axel Castelo)\n\n"
            "*Pagamento via cartão:* https://link.mercadopago.com.br/cplay"
        )})
        return jsonify({"replies": respostas})

    if "o que é iptv" in mensagem or "como funciona" in mensagem:
        respostas.append({"message": (
            "📺 *IPTV* é uma forma moderna de assistir TV usando a internet! Você tem acesso a *canais ao vivo*, *filmes*, *séries* e muito mais no seu celular, TV ou computador."
        )})
        return jsonify({"replies": respostas})

    respostas.append({"message": "Me diga o modelo da sua TV ou celular pra eu indicar o melhor aplicativo pra começar seu teste. 😉"})
    return jsonify({"replies": respostas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
