from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Planos disponíveis
planos = """
💳 Planos disponíveis:
- R$ 26,00 – 1 mês
- R$ 47,00 – 2 meses
- R$ 68,00 – 3 meses
- R$ 129,00 – 6 meses
- R$ 185,00 – 1 ano

💰 Pagamento por PIX (CNPJ) ou Cartão.
"""

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    msg = data.get("message", "").lower()
    nome = data.get("name", "")
    respostas = []

    eh_novo = nome.startswith("+55")

    if "teste" in msg or "quero testar" in msg:
        if eh_novo:
            respostas.append("👋 Olá! Que bom ter você aqui. Vamos liberar um teste pra você conhecer nosso serviço. Qual dispositivo você vai usar? (Ex: Android TV, Samsung, Roku, LG, Celular...)")
        else:
            respostas.append("📺 Ótimo! Qual dispositivo você quer usar para testar? (Android TV, Roku, LG, Samsung...)")
        return jsonify({"replies": respostas})

    if "android" in msg:
        respostas.append("📲 Para Android TV, TV Box ou modelos Toshiba/Vizzion/Vidaa, baixe o app *Xtream IPTV Player*. Quando terminar, me avise aqui para te passar o número de teste. ✅")
        return jsonify({"replies": respostas})

    if "roku" in msg:
        respostas.append("📺 Para Roku, baixe primeiro o *Xcloud (verde e preto)*. Quando terminar, me avise aqui pra te passar o número de teste. ✅")
        return jsonify({"replies": respostas})

    if "samsung" in msg:
        respostas.append("📺 Sua Samsung é modelo novo ou antigo?")
        return jsonify({"replies": respostas})

    if "philco" in msg:
        respostas.append("📺 Sua Philco é modelo novo ou antigo? Se for antiga, digite o número *98* para gerar o login.")
        return jsonify({"replies": respostas})

    if "lg" in msg:
        respostas.append("📺 Baixe o app *Xcloud (verde com preto)*. Se não funcionar, pode tentar o *Duplecast (QR code)* ou *SmartOne (MAC)*. Me avise quando baixar para gerar o teste. ✅")
        return jsonify({"replies": respostas})

    if "philips" in msg or "aoc" in msg:
        respostas.append("📺 Para TVs Philips ou AOC, baixe o *OTT Player* ou *Duplecast* e me envie o QR Code para liberar o acesso.")
        return jsonify({"replies": respostas})

    if "computador" in msg:
        respostas.append("💻 Vou te enviar o link para baixar o app. Depois digite o número *224* para gerar o teste.")
        return jsonify({"replies": respostas})

    if "iphone" in msg or "ios" in msg:
        respostas.append("🍎 Baixe o app *Smarters Player Lite* na App Store. Depois digite *224* para gerar o teste.")
        return jsonify({"replies": respostas})

    if "fire" in msg or "amazon" in msg:
        respostas.append("🔥 Para Fire Stick, vou te mandar um vídeo tutorial. Depois digite o número *221* para gerar o teste.")
        return jsonify({"replies": respostas})

    if "baixei" in msg or "instalei" in msg:
        numero = random.choice(["221", "225", "500", "555"])
        respostas.append(f"✅ Ótimo! Agora digite o número *{numero}* aqui para gerar o login de teste.")
        return jsonify({"replies": respostas})

    if "recebi" in msg or "login" in msg:
        respostas.append("⏱️ Em cerca de 30 minutos te chamo aqui pra saber se deu tudo certo com o teste, tá bom? 😉")
        return jsonify({"replies": respostas})

    if "deu certo" in msg:
        respostas.append("✅ Show! Aproveite o teste. Se tiver dúvidas, me chame.")
        return jsonify({"replies": respostas})

    if "nao funcionou" in msg or "não funcionou" in msg:
        respostas.append("😕 Entendi. Pode me mandar uma foto de como digitou os dados?")
        respostas.append("Verifique se está copiando tudo certinho (letras maiúsculas, minúsculas, sem espaços...).")
        return jsonify({"replies": respostas})

    if "acabou" in msg or "terminou" in msg:
        respostas.append("⏰ O teste chegou ao fim. Gostou do serviço? Aqui estão os planos disponíveis:")
        respostas.append(planos)
        return jsonify({"replies": respostas})

    if "dica" in msg or "canal" in msg:
        respostas.append("➡️ Alguns canais só abrem em dia de eventos.")
        respostas.append("*EX: Disney+, HBO Max, Premiere, Prime Vídeo, Paramount...*")
        respostas.append("Eles funcionam só minutos antes de começar o evento ao vivo.")
        return jsonify({"replies": respostas})

    # Atendimento padrão para dúvidas e novas mensagens
    respostas.append("🤖 Sou seu assistente para tirar dúvidas e te ajudar com o teste!")
    respostas.append("Me diga o modelo da sua TV ou celular, que te envio o app ideal. 📲")
    return jsonify({"replies": respostas})

# 🟢 Esta linha deve estar fora da função
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
