from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data["query"]["message"].lower()
    sender = data["query"]["sender"]

    respostas = []

    # Respostas por modelo de TV
    if "roku" in message:
        respostas.append({ "message": f"Olá {sender}, sua TV Roku é compatível com o app *Xcloud (verde com preto)*.\nVocê já tem ele instalado?" })
        respostas.append({ "message": "Se já tiver, digite *91* aqui no WhatsApp para gerar seu login." })

    elif "samsung" in message:
        respostas.append({ "message": f"Olá {sender}, sua TV Samsung é compatível com o app *Xcloud (verde com preto)* (caso seja modelo novo).\nVocê já tem ele instalado?" })
        respostas.append({ "message": "Se já tiver, digite *91* aqui no WhatsApp para gerar seu login." })

    elif "lg" in message:
        respostas.append({ "message": f"Olá {sender}, sua TV LG é compatível com o app *Xcloud (verde com preto)*.\nVocê já tem ele instalado?" })
        respostas.append({ "message": "Se já tiver, digite *91* aqui no WhatsApp para gerar seu login." })

    elif "philco" in message or "philips" in message or "aoc" in message:
        respostas.append({ "message": f"Olá {sender}, sua TV precisa do app *OTT Player* ou *Duplecast*.\nVocê pode me enviar uma foto do QR Code do app instalado?" })

    elif "smartone" in message:
        respostas.append({ "message": "Ótimo! Como você já tem o *SmartOne*, me envie o *MAC* da TV para liberar o acesso." })

    elif "duplecast" in message or "ott" in message:
        respostas.append({ "message": "Perfeito! Me envie a *foto do QR Code* do app para eu gerar seu acesso." })

    elif "android" in message or "tv box" in message or "toshiba" in message or "vizzion" in message or "vidaa" in message:
        respostas.append({ "message": f"Sua TV é compatível com vários apps. Digite um dos números: *221*, *225*, *500* ou *555* para gerar o login." })

    elif "iphone" in message or "ios" in message:
        respostas.append({ "message": "Baixe o app *Smarters Player Lite* na App Store. Depois digite *224* aqui no WhatsApp." })

    elif "computador" in message or "pc" in message or "notebook" in message:
        respostas.append({ "message": "Acesse o app via navegador. Quando estiver pronto, digite *224* para gerar o login." })

    elif "fire stick" in message or "amazon" in message:
        respostas.append({ "message": "Veja este tutorial para instalar: [link do vídeo]. Depois digite *221* aqui no WhatsApp." })

    elif "quero testar" in message:
        respostas.append({ "message": "Beleza! Me diga qual é o modelo da sua TV para te passar o app correto primeiro." })

    elif "deu certo" in message or "funcionou" in message:
        respostas.append({ "message": "Que bom que funcionou! O teste dura cerca de 3 horas. 😉" })

    elif "planos" in message or "valor" in message or "preço" in message:
        respostas.append({ "message": "✅ *Planos disponíveis:* \n\nR$ 26,00 – 1 mês\nR$ 47,00 – 2 meses\nR$ 68,00 – 3 meses\nR$ 129,00 – 6 meses\nR$ 185,00 – 1 ano" })
        respostas.append({ "message": "*💳 Pagamento via cartão:*\nhttps://link.mercadopago.com.br/cplay" })
        respostas.append({ "message": "*📌 PIX:*\n41.638.407/0001-26\nBanco: C6\nCNPJ: Axel Castelo" })

    elif "teste" in message:
        respostas.append({ "message": "Certo, vamos iniciar seu teste! Me informe primeiro o modelo da sua TV para te passar o app correto." })

    elif "não funcionou" in message or "não deu certo" in message:
        respostas.append({ "message": "Vamos resolver! Me envie uma foto da tela da TV ou do app para que eu possa identificar o problema." })

    else:
        respostas.append({ "message": f"Olá {sender}, recebi sua mensagem: {message}" })
        respostas.append({ "message": "Estou aqui para te ajudar com IPTV. Me diga qual o modelo da sua TV ou envie uma foto do menu de aplicativos." })

    return jsonify({ "replies": respostas })

if __name__ == "__main__":
    app.run()
