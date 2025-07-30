from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Servidor ativo!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    mensagem = data.get("query", {}).get("message", "").lower()

    resposta = ""

    if "smartone" in mensagem:
        resposta = "Ótimo! Me envie o MAC da TV que já preparo seu teste."
    
    elif "duplecast" in mensagem or "ott player" in mensagem:
        resposta = "Perfeito! Me envie o QR Code do app que já crio seu acesso."

    elif any(p in mensagem for p in ["android", "tv android", "tv box", "android tv", "toshiba", "vizzion", "vidaa"]):
        resposta = (
            "Para Android TV, TV Box ou modelos Toshiba/Vizzion/Vidaa, baixe o app **Xtream IPTV Player**. "
            "Depois, digite aqui um dos números: *221*, *225*, *500* ou *555* para gerar seu login de teste."
        )

    elif "samsung" in mensagem and "nova" in mensagem:
        resposta = (
            "Para Samsung modelo novo, baixe primeiro o app **Xcloud (verde com preto)** e veja se funciona. "
            "Se não funcionar, baixe o **Duplecast** e me envie a foto do QR Code para gerar o teste."
        )

    elif "samsung" in mensagem and "antiga" in mensagem:
        resposta = "Para Samsung modelo antigo, digite o número *88* aqui para gerar seu login."

    elif "roku" in mensagem:
        resposta = (
            "Para TV Roku, baixe o app **Xcloud (verde com preto)**. Se não funcionar, baixe o **OTT Player** "
            "e me envie a foto do QR Code para liberar o teste."
        )

    elif "lg" in mensagem:
        resposta = (
            "Para LG, primeiro teste o app **Xcloud (verde com preto)**. Se não funcionar, use o **Duplecast** "
            "(envie o QR Code) ou o **SmartOne** (me envie o MAC da TV)."
        )

    elif "philips" in mensagem or "aoc" in mensagem:
        resposta = "Para Philips ou AOC, use o app **OTT Player** ou **Duplecast** e me envie o QR Code."

    elif "philco" in mensagem and "antiga" in mensagem:
        resposta = "Para Philco modelo antigo, digite o número *98* para gerar o login."

    elif "computador" in mensagem or "pc" in mensagem or "notebook" in mensagem:
        resposta = "Para computador, baixe o app no link: https://play.google.com/store/apps/details?id=com.xtream_iptv, depois digite o número *224* para gerar seu login."

    elif "fire stick" in mensagem or "amazon" in mensagem:
        resposta = "Para Fire Stick/Amazon, siga o vídeo tutorial e depois digite o número *221*."

    elif "iphone" in mensagem or "ios" in mensagem:
        resposta = "Para iPhone/iOS, baixe o app **Smarters Player Lite** na App Store e depois digite o número *224*."

    elif "pagamento" in mensagem or "pagar" in mensagem:
        resposta = (
            "*PIX para pagamento:*\n"
            "`41.638.407/0001-26` (CNPJ – Axel Castelo)\n\n"
            "*Pagamento por cartão:*\n"
            "https://link.mercadopago.com.br/cplay\n\n"
            "*Planos:*\n"
            "✅ R$26,00 – 1 mês\n"
            "✅ R$47,00 – 2 meses\n"
            "✅ R$68,00 – 3 meses\n"
            "✅ R$129,00 – 6 meses\n"
            "✅ R$185,00 – 1 ano"
        )

    else:
        resposta = "Consegue me informar o modelo da sua TV para que eu te envie o app ideal e o número correto para gerar o teste?"

    return jsonify({"replies": [{"message": resposta}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
