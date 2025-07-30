from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def responder():
    query = request.args.get("query")
    if not query:
        return jsonify({"replies": [{"message": "Erro: mensagem não recebida."}]}), 400

    import json
    try:
        query_data = json.loads(query)
    except:
        return jsonify({"replies": [{"message": "Erro ao ler os dados da mensagem."}]}), 400

    mensagem = query_data.get("message", "").lower()
    resposta = []

    # Verifica modelo de TV
    if "roku" in mensagem:
        resposta.append({"message": "Sua TV é Roku ✅\nVamos tentar com o app *Xcloud* (verde com preto).\nDigite o número *91* aqui para iniciar o teste."})
    elif "lg" in mensagem:
        if "smartone" in mensagem:
            resposta.append({"message": "Você já tem o SmartOne instalado.\nPor favor, envie o *MAC* que aparece nele para ativar."})
        else:
            resposta.append({"message": "Sua TV é LG ✅\nVamos tentar com o app *Xcloud* (verde com preto).\nDigite o número *91* aqui para iniciar o teste."})
    elif "samsung" in mensagem:
        resposta.append({"message": "Sua TV é Samsung ✅\nVamos tentar com o app *Xcloud* (verde com preto).\nDigite o número *91* aqui para iniciar o teste."})
    elif "android" in mensagem or "tv box" in mensagem or "fire stick" in mensagem:
        resposta.append({"message": "Para Android, TV Box ou Fire Stick:\nDigite o número *221* aqui para iniciar o teste."})
    elif "toshiba" in mensagem or "vizzion" in mensagem or "vidaa" in mensagem:
        resposta.append({"message": "Para Toshiba, Vizzion ou Vidaa:\nDigite o número *221* aqui para iniciar o teste."})
    elif "computador" in mensagem or "pc" in mensagem or "notebook" in mensagem:
        resposta.append({"message": "Para usar no computador 💻, baixe o app e digite o número *224* aqui para iniciar o teste."})
    elif "iphone" in mensagem or "ios" in mensagem:
        resposta.append({"message": "Para iPhone 📱, baixe o app Smarters Player Lite e digite o número *224* para testar."})
    elif "philips" in mensagem or "aoc" in mensagem:
        resposta.append({"message": "Sua TV é Philips ou AOC ✅\nVamos testar com *OTT Player* ou *Duplecast*.\nPor favor, envie uma foto do QR code do app para ativar."})
    elif "philco" in mensagem:
        resposta.append({"message": "Sua TV é Philco antiga ✅\nDigite o número *98* aqui para iniciar o teste."})
    elif "quero testar" in mensagem:
        resposta.append({"message": "Ok! Me diga o modelo da sua TV (Samsung, LG, Roku, etc) para eu indicar o melhor app e gerar o teste ✅"})
    elif "pagamento" in mensagem or "pix" in mensagem:
        resposta.append({"message": "💳 Formas de Pagamento:\n\n*PIX:* \n`41.638.407/0001-26`\nBanco: *C6*\nCNPJ: *Axel Castelo*\n\nPara pagar com cartão, use este link:\nhttps://link.mercadopago.com.br/cplay"})
    elif "planos" in mensagem:
        resposta.append({"message": "✅ *Planos disponíveis:*\n\n✔️ R$ 26,00 – 1 mês\n✔️ R$ 47,00 – 2 meses\n✔️ R$ 68,00 – 3 meses\n✔️ R$129,00 – 6 meses\n✔️ R$185,00 – 1 ano"})
    else:
        resposta.append({"message": "Olá! Me diga o modelo da sua TV para indicar o melhor app e gerar seu teste gratuito 📺"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
