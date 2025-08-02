from flask import Flask, request, jsonify

app = Flask(__name__)

# 👥 Atendimento principal do AutoResponder (mensagens inteligentes)
@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    query = data.get("query", {})
    user = query.get("sender", "")
    message = query.get("message", "").lower()

    respostas = []

    # 👋 Boas-vindas
    if "oi" in message or "olá" in message:
        respostas.append({"message": "👋 Oi! Tudo bem? Quer fazer um teste grátis de IPTV com canais, filmes e séries? Me diga qual dispositivo você quer usar (TV, celular, computador...)."})

    # ⬇️ Cliente disse que instalou o app
    elif "instalei" in message or "baixei" in message:
        respostas.append({"message": "✅ Perfeito! Para liberar seu login, por favor digite o número correspondente ao seu aparelho:\n\n📺 Samsung: *91*\n📺 TV antiga / Smart STB: *88*\n📲 Android ou iPhone: *555*"})

    # ❓ Ajuda
    elif "ajuda" in message or "suporte" in message:
        respostas.append({"message": "📞 Precisa de ajuda? Me diga qual é o seu dispositivo (TV LG, Samsung, celular, etc.) que eu te explico direitinho o que fazer!"})

    # 🧠 Mensagem genérica
    else:
        respostas.append({"message": "🤖 Estou aqui para ajudar com seu teste IPTV. Informe qual aparelho você usa (TV, celular, etc.) ou digite o número do login como *91*, *88* ou *555* se já estiver pronto!"})

    return jsonify({"replies": respostas})


# 🔁 Endpoint compatível com AutoReply (números como 91, 88, 555...)
@app.route('/autoreply', methods=['POST'])
def autoreply():
    data = request.get_json()
    numero = data.get("number", "")
    respostas = []

    if numero == "91":
        respostas.append({"message": "🔐 Aqui está seu login de teste para TV Samsung:\n\nProvedor: cplayer\nUsuário: 9hkViG\nSenha: Bq38OF\n\n⏳ 3 horas de teste\n💰 Mensalidade: R$ 26,00\n\nSe quiser assinar, digite *100*."})
    elif numero == "88":
        respostas.append({"message": "📺 TV antiga detectada! Siga essas instruções:\n\n1. Instale o app *Smart STB*\n2. Configure o DNS manual: 8.8.8.8\n3. Desligue e ligue a TV\n4. Digite *555* para receber o login\n\n⚠️ Se tiver dúvida, envie uma foto da tela!"})
    elif numero == "555":
        respostas.append({"message": "🔓 Login de teste liberado para Android, iPhone ou computador!\n\nProvedor: cplayer\nUsuário: 7mjGiR\nSenha: Ar92LQ\n\n⏳ 3 horas de teste\n💳 Planos a partir de R$ 26,00\n\nDigite *100* para assinar!"})
    elif numero == "100":
        respostas.append({"message": "🎉 Vamos ativar sua assinatura!\n\n💰 Planos:\n1 mês: R$ 26,00\n2 meses: R$ 47,00\n3 meses: R$ 68,00\n6 meses: R$ 129,00\n1 ano: R$ 185,00\n\n💳 Para pagar:\nPIX (CNPJ): *12.345.678/0001-00*\nCartão: https://pagamento.com/link\n\nAssim que pagar, envie o comprovante aqui ✅"})
    else:
        respostas.append({"message": "❗Código inválido. Digite 91, 88, 555 ou 100 conforme sua necessidade."})

    return jsonify({"replies": respostas})


# 🟢 Iniciar servidor no Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
