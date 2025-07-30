from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Sua chave da API da OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Lista de palavras-chave e modelos associados
modelos_tv = {
    "roku": "Roku",
    "lg": "LG",
    "samsung": "Samsung",
    "philco": "Philco",
    "aoc": "AOC",
    "philips": "Philips",
    "tcl": "TCL",
    "vizzion": "Toshiba/Vizzion/Vidaa",
    "toshiba": "Toshiba/Vizzion/Vidaa",
    "tv box": "Android TV / TV Box",
    "box": "Android TV / TV Box",
    "android": "Android TV / TV Box",
    "computador": "Computador",
    "pc": "Computador",
    "fire": "Fire Stick",
    "iphone": "iPhone / iOS",
    "ios": "iPhone / iOS"
}

numeros_resposta = {
    "Android TV / TV Box": ["221", "225", "500", "555"],
    "Samsung antiga": ["88"],
    "Samsung nova": ["91"],  # Xcloud
    "Roku": ["91"],          # Xcloud
    "LG": ["91"],            # Xcloud
    "Philco antiga": ["98"],
    "Computador": ["224"],
    "Fire Stick": ["221"],
    "iPhone / iOS": ["224"],
    "Toshiba/Vizzion/Vidaa": ["221"]
}

pagamento = """
*PIX (CNPJ):* 41.638.407/0001-26
Banco: *C6*
Nome: *Axel Castelo*

💳 *Pagamento via cartão:*
https://link.mercadopago.com.br/cplay

✅ R$ 26,00 - 1 mês  
✅ R$ 47,00 - 2 meses  
✅ R$ 68,00 - 3 meses  
✅ R$ 129,00 - 6 meses  
✅ R$ 185,00 - 1 ano
"""

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    mensagem = query.get("message", "").lower()
    sender = query.get("sender", "cliente")

    # Tenta identificar modelo da TV
    modelo_identificado = None
    for palavra, modelo in modelos_tv.items():
        if palavra in mensagem:
            modelo_identificado = modelo
            break

    # Se for foto ou MAC já conhecido
    if "mac" in mensagem:
        return jsonify({"replies": [{"message": "Por favor, envie o código MAC da sua TV para gerar o acesso."}]})

    if "paguei" in mensagem or "fiz o pix" in mensagem:
        return jsonify({"replies": [{"message": "Pagamento identificado! Em instantes enviaremos a ativação."}]})

    if "forma de pagamento" in mensagem or "preço" in mensagem:
        return jsonify({"replies": [{"message": pagamento}]})

    if modelo_identificado:
        opcoes = numeros_resposta.get(modelo_identificado)
        if modelo_identificado in ["Samsung nova", "Roku", "LG"]:
            return jsonify({"replies": [
                {"message": f"Baixe o app *Xcloud* (ícone verde e preto) na sua TV {modelo_identificado}. Depois digite *{opcoes[0]}* aqui para gerar seu acesso de teste."}
            ]})
        elif modelo_identificado in numeros_resposta:
            numeros = " ou ".join(opcoes)
            return jsonify({"replies": [
                {"message": f"Para a TV {modelo_identificado}, digite *{numeros}* para gerar seu teste automaticamente."}
            ]})

    if "teste" in mensagem or "quero testar" in mensagem:
        return jsonify({"replies": [{"message": "Claro! Me diga o modelo da sua TV para indicar o aplicativo ideal."}]})

    # Resposta padrão com IA (OpenAI)
    try:
        resposta_ia = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um atendente de suporte de IPTV, seu objetivo é ajudar o cliente a configurar o serviço."},
                {"role": "user", "content": mensagem}
            ]
        )
        texto = resposta_ia.choices[0].message["content"]
        return jsonify({"replies": [{"message": texto}]})
    except Exception as e:
        return jsonify({"replies": [{"message": "Houve um erro ao gerar resposta. Tente novamente mais tarde."}]})


# Porta correta para o Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
