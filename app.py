from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])  # Agora aceita POST e GET
def webhook():
    if request.method == 'GET':
        return "Webhook ativo!"

    data = request.get_json()

    if not data:
        return jsonify({"replies": [{"message": "Erro: nenhuma informação recebida."}]}), 400

    message = data.get('query', {}).get('message', '').lower()
    
    # Lógica inteligente baseada no modelo de TV
    if any(x in message for x in ['android', 'android tv', 'tv box', 'toshiba', 'vizzion', 'vidaa']):
        return jsonify({"replies": [{"message": "✅ Baixe o app *Xtream IPTV Player* na Play Store.\n\nDigite o número *555* aqui para gerar seu teste."}]})

    elif 'samsung' in message:
        return jsonify({"replies": [{"message": "Sua TV Samsung é modelo *novo* ou *antigo*?"}]})

    elif 'samsung nova' in message:
        return jsonify({"replies": [{"message": "✅ Instale o app *Xcloud* (ícone verde e preto).\nDigite o número *91* aqui para gerar seu teste.\nSe não funcionar, vamos tentar o *Duplecast* com QR Code."}]})

    elif 'samsung antiga' in message:
        return jsonify({"replies": [{"message": "✅ Para Samsung modelo antigo, digite o número *88* para gerar seu teste."}]})

    elif 'philco' in message:
        return jsonify({"replies": [{"message": "Sua TV Philco é modelo *antigo* ou *novo*?"}]})

    elif 'philco antiga' in message:
        return jsonify({"replies": [{"message": "✅ Para Philco antiga, digite o número *98* para gerar seu teste."}]})

    elif 'lg' in message:
        return jsonify({"replies": [{"message": "✅ Instale o *Xcloud* (ícone verde com preto). Digite o número *91* para gerar seu teste.\nSe não funcionar, use *Duplecast* (QR code) ou *SmartOne* (com MAC). Se já tiver o app, envie o MAC para ativar."}]})

    elif 'roku' in message:
        return jsonify({"replies": [{"message": "✅ Primeiro instale o *Xcloud* (ícone verde com preto). Digite *91* aqui para gerar o teste.\nSe não funcionar, instale o *OTT Player* e envie o QR Code."}]})

    elif 'philips' in message or 'aoc' in message:
        return jsonify({"replies": [{"message": "✅ Instale o *OTT Player* ou *Duplecast*.\nPor favor, envie o QR Code para liberar o teste."}]})

    elif 'smartone' in message:
        return jsonify({"replies": [{"message": "✅ Envie o *MAC address* do app SmartOne para gerar seu teste."}]})

    elif 'pagamento' in message or 'pix' in message or 'valor' in message:
        return jsonify({"replies": [{
            "message": "💳 *Formas de Pagamento:*\n\n*PIX:* 41.638.407/0001-26\nBanco: C6\nCNPJ: Axel Castelo\n\n💰 *Planos:*\n✅ R$26 - 1 mês\n✅ R$47 - 2 meses\n✅ R$68 - 3 meses\n✅ R$129 - 6 meses\n✅ R$185 - 1 ano\n\n🔗 *Cartão de crédito:* https://link.mercadopago.com.br/cplay"
        }]})

    else:
        return jsonify({"replies": [{"message": "Consegue me informar o modelo da sua TV para que eu te envie o app ideal e o número correto para gerar o teste?"}]})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
