from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def responder():
    if request.method == "POST":
        data = request.get_json()
    else:
        query = request.args.get("query")
        if not query:
            return jsonify({"replies": [{"message": "Erro: mensagem não recebida."}]}), 400
        try:
            data = json.loads(query)
        except:
            return jsonify({"replies": [{"message": "Erro ao ler os dados da mensagem."}]}), 400

    mensagem = data.get("message", "").lower()

    # ======= LÓGICA DE RESPOSTA =======

    resposta = ""

    if "smartone" in mensagem:
        resposta = "Você já está com o app SmartOne instalado! Por favor, me envie o número MAC que aparece na tela para gerar o acesso."

    elif "samsung" in mensagem:
        resposta = (
            "Ótimo! Baixe o app *Xcloud* (ícone verde com preto) direto na loja da TV. "
            "Depois de instalar, digite o número *91* aqui no WhatsApp para gerar seu acesso de teste."
        )

    elif "roku" in mensagem:
        resposta = (
            "Ótimo! Baixe o app *Xcloud* (ícone verde com preto) direto na loja da TV Roku. "
            "Após instalar, digite o número *91* aqui no WhatsApp para iniciar seu teste. "
            "Caso não funcione, podemos testar o *OTT Player* com QR Code."
        )

    elif "lg" in mensagem:
        resposta = (
            "Perfeito! Baixe o app *Xcloud* (verde com preto). Após instalar, digite *91* aqui no WhatsApp. "
            "Se não funcionar, podemos testar o Duplecast (QR Code) ou SmartOne (precisa do MAC)."
        )

    elif "philips" in mensagem or "aoc" in mensagem:
        resposta = (
            "Para Philips ou AOC, podemos usar *OTT Player* ou *Duplecast*. Por favor, envie uma foto do QR Code do app que instalar para continuar."
        )

    elif "quero testar" in mensagem:
        resposta = (
            "Claro! Me diga o modelo da sua TV para indicar o aplicativo ideal e te enviar o código correto."
        )

    elif "planos" in mensagem or "preço" in mensagem or "valores" in mensagem:
        resposta = (
            "*Planos:*\n\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$ 47,00 - 2 meses\n"
            "✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n"
            "✅ R$ 185,00 - 1 ano\n\n"
            "*Formas de pagamento:*\n\n"
            "*PIX:* 41.638.407/0001-26\n"
            "*CNPJ:* Axel Castelo\n"
            "*Banco:* C6\n\n"
            "*Cartão:* [Clique aqui para pagar com cartão](https://link.mercadopago.com.br/cplay)"
        )

    elif "oi" in mensagem or "ola" in mensagem:
        resposta = (
            "Olá! Seja bem-vindo 😄\nMe diga o modelo da sua TV para indicar o aplicativo ideal."
        )

    elif "android" in mensagem or "tv box" in mensagem or "toshiba" in mensagem or "vizzion" in mensagem or "vidaa" in mensagem:
        resposta = (
            "Para Android TV, TV Box ou modelos Toshiba/Vizzion/Vidaa, baixe o app *Xtream IPTV Player*. "
            "Depois, digite um dos seguintes números aqui: *221*, *225*, *500* ou *555* para gerar seu login de teste."
        )

    elif "iphone" in mensagem or "ios" in mensagem:
        resposta = (
            "Para iPhone/iOS, baixe o app *Smarters Player Lite* na App Store. Após isso, digite *224* aqui no WhatsApp para gerar seu login de teste."
        )

    elif "computador" in mensagem or "pc" in mensagem:
        resposta = (
            "Para computador/PC, use o aplicativo compatível com o link e depois digite *224* aqui no WhatsApp para gerar seu login."
        )

    elif "fire stick" in mensagem or "amazon" in mensagem:
        resposta = (
            "Para Fire Stick da Amazon, siga o nosso vídeo tutorial para instalação. Depois, digite *221* aqui no WhatsApp para gerar seu acesso."
        )

    elif "outro" in mensagem or "não sei" in mensagem:
        resposta = (
            "Sem problemas! Me envie uma foto da tela da TV ou do menu de aplicativos para que eu possa identificar e te ajudar da melhor forma possível."
        )

    else:
        resposta = (
            "Consegue me informar o modelo da sua TV para que eu te envie o app ideal e o número correto para gerar o teste?"
        )

    return jsonify({
        "replies": [
            {"message": resposta}
        ]
    })

# ========== INICIAR ==========

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
