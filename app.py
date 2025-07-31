from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Webhooks
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Dispositivos e apps sugeridos
DISPOSITIVOS = {
    "android": "xtream iptv player",
    "tv box": "xtream iptv player",
    "celular": "xtream iptv player",
    "projetor": "xtream iptv player",
    "roku": "xcloud",
    "samsung": "xcloud",
    "lg": "xcloud",
    "philco": "xcloud",
    "philco antiga": "smart stb",
    "aoc": "duplecast ou ott player",
    "philips": "duplecast ou ott player",
    "iphone": "smarters player lite",
    "ios": "smarters player lite",
    "computador": "smarters player lite",
    "fire stick": "xtream iptv player"
}

# Boas-vindas
def gerar_boas_vindas():
    return (
        "Olá! 👋 Aqui você tem acesso a *canais, filmes e séries* no seu dispositivo.\n"
        "Vamos começar seu teste gratuito? Me diga qual é o seu dispositivo ou TV que você quer usar."
    )

# Gera login com base na webhook
def gerar_login(webhook_url):
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            username = dados.get("username", "")
            password = dados.get("password", "")
            dns = dados.get("dns", "")
            msg = f"*Usuário:* `{username}`\n*Senha:* `{password}`"
            if dns:
                msg += f"\n*URL:* `{dns}`"
            msg += "\n\n⏳ *Seu teste dura 3 horas.*"

            # Verifica caracteres parecidos
            alerta = ""
            if re.search(r"[IlO0]", username):
                alerta += "\n\n⚠️ Atenção! Seu usuário contém caracteres parecidos:\n"
                if "I" in username:
                    alerta += "✅ Letra *I* de *Irlanda*\n"
                if "l" in username:
                    alerta += "✅ Letra *l* minúscula de *lápis*\n"
                if "O" in username:
                    alerta += "✅ Letra *O* de *Ovo*\n"
                if "0" in username:
                    alerta += "✅ Número *0* (zero)\n"
                alerta += "\nDigite exatamente como foi enviado, respeitando maiúsculas e minúsculas."
            return msg + alerta
        else:
            return "❌ Erro ao gerar login de teste. Tente novamente em instantes."
    except:
        return "⚠️ Não foi possível gerar o login. Verifique sua conexão."

# Rota principal
@app.route("/", methods=["GET"])
def responder():
    nome = request.args.get("name", "")
    mensagem = request.args.get("message", "").lower()

    respostas = []

    # Mensagem inicial
    if "teste" in mensagem or mensagem in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]:
        respostas.append({"message": gerar_boas_vindas()})
        return jsonify({"replies": respostas})

    # Identifica dispositivo
    for termo, app in DISPOSITIVOS.items():
        if termo in mensagem:
            if app == "xcloud":
                respostas.append({"message": "✅ Baixe o app *Xcloud* (ícone verde e preto) na sua TV.\nMe avise quando instalar para eu liberar o login!"})
            elif app == "xtream iptv player":
                respostas.append({"message": "✅ Baixe o *Xtream IPTV Player* no seu Android, TV Box ou celular.\nMe avise quando instalar para liberar o login!"})
            elif app == "smarters player lite":
                respostas.append({"message": "✅ Baixe o *Smarters Player Lite* no seu iPhone ou computador.\nMe avise quando instalar para liberar o login!"})
            elif "duplecast" in app or "ott player" in app:
                respostas.append({"message": "✅ Baixe o app *Duplecast IPTV* ou *OTT Player*.\nAbra o app e envie a *foto do QR Code* da tela para ativar seu acesso."})
            elif app == "smart stb":
                respostas.append({"message": (
                    "✅ Faça o procedimento deste vídeo:\n"
                    "https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0\n\n"
                    "*DNS:* `64.31.61.14`\n"
                    "Depois:\n1 - Reinicie a TV\n2 - Instale o app *SMART STB*\n3 - Me avise para gerar o login."
                )})
            return jsonify({"replies": respostas})

    # Cliente informou que já instalou
    if "instalei" in mensagem or "já instalei" in mensagem:
        if "samsung" in mensagem or "xcloud" in mensagem or "roku" in mensagem or "lg" in mensagem:
            login = gerar_login(WEBHOOK_XCLOUD)
        else:
            login = gerar_login(WEBHOOK_GERAL)

        respostas.append({"message": f"✅ Aqui está seu login de teste:\n\n{login}"})
        respostas.append({"message": "⏳ Aguarde alguns minutos e me diga se funcionou tudo certinho, beleza? 😉"})
        return jsonify({"replies": respostas})

    # Durante o teste – ajuda
    if "erro" in mensagem or "não funcionou" in mensagem:
        respostas.append({"message": "❌ Verifique se digitou certo: maiúsculas, minúsculas e sem espaços extras.\nSe preferir, envie foto da tela para eu analisar."})
        return jsonify({"replies": respostas})

    # Encerramento do teste
    if "terminou o teste" in mensagem or "acabou o teste" in mensagem:
        respostas.append({"message": (
            "⏳ Seu teste terminou.\n\nPlanos disponíveis:\n"
            "🎯 R$ 26,00 – 1 mês\n"
            "🎯 R$ 47,00 – 2 meses\n"
            "🎯 R$ 68,00 – 3 meses\n"
            "🎯 R$ 129,00 – 6 meses\n"
            "🎯 R$ 185,00 – 1 ano\n\n"
            "*PIX:*\n41.638.407/0001-26 (CNPJ Axel Castelo)\n"
            "*Cartão:* https://link.mercadopago.com.br/cplay"
        )})
        return jsonify({"replies": respostas})

    # Dúvidas gerais sobre IPTV
    if "o que é iptv" in mensagem or "como funciona" in mensagem:
        respostas.append({"message": (
            "📺 *IPTV* é um serviço para assistir *TV ao vivo, filmes e séries* usando a internet. Sem antenas ou cabos!\n"
            "Você só precisa instalar o app e digitar seu login. Pronto!"
        )})
        return jsonify({"replies": respostas})

    # Padrão
    respostas.append({"message": "Me diga o modelo da sua TV ou celular pra eu indicar o app certo! 😉"})
    return jsonify({"replies": respostas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
