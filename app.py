from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"replies": [{"message": "Erro: dados ausentes."}]})

    message = data['query']['message'].lower()
    sender = data['query']['sender']

    replies = []

    # Cliente já tem app instalado
    if "smartone" in message:
        replies.append({"message": "Ótimo! Me envie o *MAC* que aparece no SmartOne para gerar seu acesso."})

    elif "duplecast" in message or "ott player" in message:
        replies.append({"message": "Certo! Por favor, me envie a *foto do QR Code* que aparece no app para ativar."})

    # Identificação por modelo de TV
    elif "samsung" in message:
        replies.append({"message": "👉 Baixe o app *Xcloud* (ícone verde e preto) na sua TV Samsung."})
        replies.append({"message": "Depois de instalar, digite o número *91* aqui no WhatsApp para liberar o teste."})

    elif "lg" in message:
        replies.append({"message": "👉 Baixe o app *Xcloud* (ícone verde e preto) na sua LG."})
        replies.append({"message": "Depois digite *91*. Se não funcionar, me envie a *foto do QR Code* do Duplecast ou o *MAC* do SmartOne."})

    elif "roku" in message:
        replies.append({"message": "👉 Baixe o app *Xcloud* na sua Roku."})
        replies.append({"message": "Digite o número *91* aqui no WhatsApp. Se não funcionar, me envie o QR Code do OTT Player."})

    elif "android" in message or "tv box" in message or "toshiba" in message or "vizzion" in message or "vidaa" in message:
        replies.append({"message": "👉 Baixe o app *Xtream IPTV Player* na sua TV Android ou TV Box."})
        replies.append({"message": "Depois digite *555* aqui para gerar o login automático."})

    elif "philco" in message:
        replies.append({"message": "Para TV Philco antiga, digite o número *98* aqui para continuar."})

    elif "samsung antiga" in message:
        replies.append({"message": "Para Samsung modelo antigo, digite *88* aqui no WhatsApp para iniciar o teste."})

    elif "computador" in message:
        replies.append({"message": "No computador, baixe o app e depois digite *224* aqui para ativar."})

    elif "iphone" in message or "ios" in message:
        replies.append({"message": "No iPhone, instale o app *Smarters Player Lite* e digite *224* aqui para ativar seu teste."})

    elif "fire stick" in message or "amazon" in message:
        replies.append({"message": "Assista ao vídeo tutorial de instalação no Fire Stick, e depois digite *221* para continuar."})

    elif "quero pagar" in message or "formas de pagamento" in message or "como pagar" in message:
        replies.append({"message": "*💳 Formas de pagamento:*"})
        replies.append({"message": "*PIX (CNPJ):*\n```41.638.407/0001-26```\nBanco C6\nCNPJ: Axel Castelo"})
        replies.append({"message": "*💳 Cartão:* [Clique aqui para pagar com cartão](https://link.mercadopago.com.br/cplay)"})
        replies.append({"message": "*Planos disponíveis:*"})
        replies.append({"message": "✅ R$ 26,00 - 1 mês\n✅ R$47,00 - 2 meses\n✅ R$68,00 - 3 meses\n✅ R$129,00 - 6 meses\n✅ R$185,00 - 1 ano"})

    elif "tempo" in message or "duração" in message or "3 horas" in message:
        replies.append({"message": "O teste é liberado por tempo limitado para avaliação. 😉"})

    else:
        replies.append({"message": f"Olá {sender}, recebi sua mensagem: *{message}*"})
        replies.append({"message": "Pode me dizer o modelo da sua TV ou aparelho para eu indicar o aplicativo correto?"})

    return jsonify({"replies": replies})
