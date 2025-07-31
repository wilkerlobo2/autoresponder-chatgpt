from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Webhooks
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Palavras que indicam que o app foi instalado
PALAVRAS_CONFIRMADAS = ["instalei", "baixei", "baixado", "foi", "pronto", "já instalei", "tá pronto"]

# Dicionário de dispositivos e apps
DISPOSITIVOS = {
    "roku": {"app": "Xcloud", "webhook": WEBHOOK_XCLOUD},
    "samsung": {"app": "Xcloud", "webhook": WEBHOOK_XCLOUD},
    "lg": {"app": "Xcloud", "webhook": WEBHOOK_XCLOUD},
    "philco antiga": {"app": "Smart STB", "dns": "64.31.61.14"},
    "philco": {"app": "Xcloud", "webhook": WEBHOOK_XCLOUD},
    "aoc": {"app": "OTT Player / Duplecast"},
    "philips": {"app": "OTT Player / Duplecast"},
    "android": {"app": "Xtream IPTV Player", "webhook": WEBHOOK_GERAL},
    "tv box": {"app": "Xtream IPTV Player", "webhook": WEBHOOK_GERAL},
    "celular": {"app": "Xtream IPTV Player", "webhook": WEBHOOK_GERAL},
    "projetor": {"app": "Xtream IPTV Player", "webhook": WEBHOOK_GERAL},
    "iphone": {"app": "Smarters Player Lite", "webhook": WEBHOOK_GERAL},
    "ios": {"app": "Smarters Player Lite", "webhook": WEBHOOK_GERAL},
    "computador": {"app": "Smarters Player Lite", "webhook": WEBHOOK_GERAL},
    "fire stick": {"app": "Xtream IPTV Player", "webhook": WEBHOOK_GERAL},
}

# Função para gerar boas-vindas
def boas_vindas(nome):
    if nome.startswith("+55"):
        return (
            "👋 Olá! Seja bem-vindo(a)! Aqui você tem acesso a *canais, filmes e séries* direto no seu aparelho. "
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual é o modelo da sua TV ou celular. 😉"
        )
    return None

# Função para gerar login
def gerar_login(webhook_url):
    try:
        resp = requests.get(webhook_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            usuario = data.get("username", "")
            senha = data.get("password", "")
            dns = data.get("dns", "")

            msg = f"*Usuário:* `{usuario}`\n*Senha:* `{senha}`"
            if dns:
                msg += f"\n*DNS:* `{dns}`"
            msg += "\n\n⏳ *Seu teste dura 3 horas.*"

            if re.search(r"[IlO0]", usuario):
                msg += (
                    "\n\n⚠️ Atenção: o login contém caracteres parecidos:\n"
                    "✅ Letra *I* de *Índia*\n"
                    "✅ Letra *l* minúscula de *lápis*\n"
                    "✅ Letra *O* de *Ovo*\n"
                    "✅ Número *0* (zero)\n"
                    "Digite exatamente como foi enviado, respeitando letras maiúsculas e minúsculas."
                )

            return msg
        else:
            return "❌ Erro ao gerar login. Tente novamente em instantes."
    except:
        return "⚠️ Ocorreu um erro ao gerar seu login."

@app.route("/", methods=["POST"])
def responder():
    nome = request.args.get("name", "")
    mensagem = request.args.get("message", "").lower()
    respostas = []

    # Boas-vindas para novos clientes
    if nome.startswith("+55") and "teste" in mensagem:
        respostas.append({"message": boas_vindas(nome)})
        return jsonify({"replies": respostas})

    # Identificação do dispositivo
    for chave in DISPOSITIVOS:
        if chave in mensagem:
            info = DISPOSITIVOS[chave]
            app_nome = info["app"]

            if app_nome == "Smart STB":
                respostas.append({"message": (
                    "📺 Para sua Philco antiga:\n"
                    "Assista ao vídeo 👇\n"
                    "https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0\n\n"
                    f"*DNS:* `{info['dns']}`\n"
                    "Depois:\n1️⃣ Desligue e ligue a TV\n2️⃣ Instale o app *SMART STB*\n\n"
                    "Me avise aqui para gerar seu acesso!"
                )})
                return jsonify({"replies": respostas})

            if app_nome == "OTT Player / Duplecast":
                respostas.append({"message": (
                    "📲 Instale o app *Duplecast IPTV* ou *OTT Player* na sua TV.\n"
                    "Depois de instalar, abra o app e envie uma *foto do QR Code* para ativar seu acesso. 📸"
                )})
                return jsonify({"replies": respostas})

            respostas.append({"message": f"✅ Baixe o app *{app_nome}*.\nQuando instalar, me avise para liberar seu acesso. 😉"})
            return jsonify({"replies": respostas})

    # Cliente confirmou que instalou
    if any(palavra in mensagem for palavra in PALAVRAS_CONFIRMADAS):
        if "xcloud" in mensagem or "roku" in mensagem or "samsung" in mensagem or "lg" in mensagem or "philco" in mensagem:
            login = gerar_login(WEBHOOK_XCLOUD)
        else:
            login = gerar_login(WEBHOOK_GERAL)

        respostas.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        respostas.append({"message": (
            "⏳ Daqui 30 minutos te pergunto se deu tudo certo, tá bom?\n\n"
            "⚠️ Lembre-se:\n"
            "➡️ Alguns canais só funcionam durante eventos ao vivo como futebol, lutas, etc.\n"
            "Eles abrem poucos minutos antes de começar!"
        )})
        return jsonify({"replies": respostas})

    # Após 3 horas
    if "terminou o teste" in mensagem or "acabou o teste" in mensagem:
        respostas.append({"message": (
            "⏳ Seu teste gratuito terminou.\n\n"
            "*Planos disponíveis:* 👇\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$ 47,00 - 2 meses\n"
            "✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n"
            "✅ R$ 185,00 - 1 ano\n\n"
            "*PIX:* 41.638.407/0001-26 (CNPJ - Axel Castelo / Banco C6)\n"
            "*Cartão:* https://link.mercadopago.com.br/cplay"
        )})
        return jsonify({"replies": respostas})

    # Dúvidas gerais
    if "o que é iptv" in mensagem or "como funciona" in mensagem:
        respostas.append({"message": (
            "📺 *IPTV* é uma forma moderna de assistir canais, filmes e séries pela internet.\n"
            "Sem antena, sem complicação. Basta instalar o app e digitar seu login!"
        )})
        return jsonify({"replies": respostas})

    # Falha no teste
    if "não funcionou" in mensagem or "erro" in mensagem or "não deu certo" in mensagem:
        respostas.append({"message": (
            "⚠️ Verifique se digitou tudo certinho.\n"
            "Observe letras maiúsculas e minúsculas, sem espaços extras.\n"
            "Se puder, mande uma foto da tela pra eu te ajudar!"
        )})
        return jsonify({"replies": respostas})

    # Resposta padrão
    respostas.append({"message": "Me diga qual é o modelo da sua TV ou celular para indicar o app ideal. 📲"})
    return jsonify({"replies": respostas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
