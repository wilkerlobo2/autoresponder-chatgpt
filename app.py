from flask import Flask, request, jsonify
import openai
import random
import re
import time
import requests

app = Flask(__name__)
openai.api_key = "SUA_API_KEY"

# Webhooks de geração de login
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Lista de palavras-chave para dispositivos
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

# Respostas padrão para boas-vindas
def gerar_boas_vindas():
    return (
        "Olá! 👋 Aqui você tem acesso a *canais, filmes e séries* no seu dispositivo.\n"
        "Vamos começar seu teste gratuito? Me diga qual é o seu dispositivo ou TV que você quer usar."
    )

# Verifica se é cliente novo (sem nome salvo)
def cliente_novo(nome):
    return nome.startswith("+55")

# Envia login de teste a partir da webhook
def gerar_login(webhook_url):
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            username = dados.get("username", "")
            password = dados.get("password", "")
            dns = dados.get("dns", "")
            mensagem = f"*Usuário:* `{username}`\n*Senha:* `{password}`"
            if dns:
                mensagem += f"\n*DNS:* `{dns}`"
            mensagem += "\n\n⏳ *Seu teste dura 3 horas.*"
            # Aviso sobre caracteres parecidos
            alerta = ""
            if re.search(r"[IlO0]", username):
                alerta += "\n⚠️ Atenção: o login contém caracteres parecidos. Observe:\n"
                if "I" in username:
                    alerta += "✅ Letra *I* de *Índia*\n"
                if "l" in username:
                    alerta += "✅ Letra *l* minúscula de *lápis*\n"
                if "O" in username:
                    alerta += "✅ Letra *O* de *Ovo*\n"
                if "0" in username:
                    alerta += "✅ Número *0* (zero)\n"
                alerta += "\nDigite exatamente como foi enviado, respeitando letras maiúsculas e minúsculas."
            return mensagem + alerta
        else:
            return "❌ Erro ao gerar login de teste. Tente novamente mais tarde."
    except Exception as e:
        return "⚠️ Ocorreu um erro ao gerar o teste."

# Função principal de atendimento
@app.route("/", methods=["GET"])
def responder():
    nome = request.args.get("name", "")
    mensagem = request.args.get("message", "").lower()

    respostas = []

    # Se cliente for novo
    if cliente_novo(nome) and "teste" in mensagem:
        respostas.append({"message": gerar_boas_vindas()})
        return jsonify({"replies": respostas})

    # Dispositivo citado
    for chave in DISPOSITIVOS:
        if chave in mensagem:
            app_indicado = DISPOSITIVOS[chave]
            if app_indicado == "xcloud":
                respostas.append({"message": "✅ Baixe o app *Xcloud* (ícone verde e preto) na sua TV.\nMe avise quando tiver instalado para eu liberar o login!"})
                return jsonify({"replies": respostas})
            elif app_indicado == "xtream iptv player":
                respostas.append({"message": "✅ Baixe o app *Xtream IPTV Player* no seu aparelho Android, TV box ou celular. Me avise quando terminar para eu liberar o login!"})
                return jsonify({"replies": respostas})
            elif app_indicado == "smarters player lite":
                respostas.append({"message": "✅ Baixe o app *Smarters Player Lite*. Me avise quando tiver instalado no seu iPhone ou computador para eu liberar o login!"})
                return jsonify({"replies": respostas})
            elif "duplecast" in app_indicado or "ott player" in app_indicado:
                respostas.append({"message": "✅ Baixe o app *Duplecast IPTV* ou *OTT Player*.\nAbra o app e envie a *foto do QR Code* da tela para eu ativar seu acesso!"})
                return jsonify({"replies": respostas})
            elif app_indicado == "smart stb":
                respostas.append({"message": (
                    "✅ Faça o procedimento deste vídeo:\n"
                    "https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0\n\n"
                    "*DNS:* `64.31.61.14`\n"
                    "Depois de fazer:\n1 - Desligue e ligue a TV\n2 - Instale o app *SMART STB*\n\n"
                    "Em seguida, me avise para eu gerar seu login!"
                )})
                return jsonify({"replies": respostas})

    # Cliente disse que instalou
    if "instalei" in mensagem or "já instalei" in mensagem:
        if "xcloud" in mensagem or "roku" in mensagem or "samsung" in mensagem or "lg" in mensagem:
            login_msg = gerar_login(WEBHOOK_XCLOUD)
        elif "iphone" in mensagem or "ios" in mensagem or "computador" in mensagem:
            login_msg = gerar_login(WEBHOOK_GERAL)
        else:
            login_msg = gerar_login(WEBHOOK_GERAL)
        respostas.append({"message": f"Aqui está seu login de teste:\n\n{login_msg}"})

        # Mensagem após 30 minutos
        respostas.append({"message": "⏳ Aguarde, em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        return jsonify({"replies": respostas})

    # Mensagens de apoio durante teste
    if "não funcionou" in mensagem or "deu erro" in mensagem:
        respostas.append({"message": "❌ Verifique se digitou certo: maiúsculas, minúsculas e sem espaços extras.\nSe possível, envie uma foto da tela pra eu analisar."})
        return jsonify({"replies": respostas})

    # Padrão de dúvidas gerais
    if "o que é iptv" in mensagem or "como funciona" in mensagem:
        respostas.append({"message": (
            "📺 *IPTV* é um serviço de TV pela internet, onde você assiste *canais ao vivo*, *filmes* e *séries* direto no seu aparelho, sem antenas ou cabos.\n"
            "Basta instalar o app e digitar seu login. Simples assim!"
        )})
        return jsonify({"replies": respostas})

    # Encerramento de teste (após 3 horas seria ideal fazer isso com agendamento externo)
    if "terminou o teste" in mensagem:
        respostas.append({"message": (
            "⏳ Seu teste expirou.\n\nAqui estão nossos planos:\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$ 47,00 - 2 meses\n"
            "✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n"
            "✅ R$ 185,00 - 1 ano\n\n"
            "*PIX:*\n41.638.407/0001-26\nBanco C6 - CNPJ Axel Castelo\n\n"
            "*Cartão de crédito:* https://link.mercadopago.com.br/cplay"
        )})
        return jsonify({"replies": respostas})

    # Se nenhuma das regras acima foi acionada
    respostas.append({"message": "Me diga o modelo da sua TV ou celular para eu te indicar o aplicativo ideal! 📺"})
    return jsonify({"replies": respostas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
