from flask import Flask, request, jsonify
import random
import datetime

app = Flask(__name__)

# Planos disponíveis
planos = """📦 Planos disponíveis:
- R$ 26,00 – 1 mês
- R$ 47,00 – 2 meses
- R$ 68,00 – 3 meses
- R$ 129,00 – 6 meses
- R$ 185,00 – 1 ano

💳 Pagamento via PIX (CNPJ) ou Cartão."""

# Mensagens aleatórias durante o teste
avisos = [
    "➡️ Alguns canais só abrem em dias de eventos, como Disney+, HBO Max, Premiere, etc. A transmissão começa minutos antes do evento.",
    "ℹ️ Se algum canal não abrir, pode ser porque só funciona em horário de jogo, luta ou evento ao vivo.",
    "💡 Alguns conteúdos como Prime Video ou Paramount+ só ativam no momento do evento, isso é normal.",
    "🎯 Lembre-se: canais especiais ficam off até o evento começar. Isso economiza recursos e melhora a performance!"
]

numeros_login = ['221', '225', '500', '555']

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    msg = data.get("message", "").lower()
    nome = data.get("name", "")
    eh_novo = nome.startswith("+55")
    
    # Ignora mensagens com mídia
    if data.get("type") in ["image", "audio", "video", "document"]:
        return jsonify({"reply": "Recebi sua mídia! Já já o suporte vai verificar manualmente. 😉"})

    # Mensagem inicial para quem pede teste
    if "teste" in msg or "quero testar" in msg:
        if eh_novo:
            return jsonify({
                "reply": "👋 Olá! Que bom ter você aqui. Vamos liberar um teste pra você conhecer nosso serviço.\n\nQual dispositivo você vai usar para testar? (Ex: Android TV, Samsung, Roku, LG, Celular, etc)"
            })
        else:
            return jsonify({
                "reply": "Ótimo! Qual dispositivo você vai usar para testar? (Ex: Android TV, Samsung, Roku, LG, Celular, etc)"
            })

    # Exemplo: Android
    if "android" in msg:
        return jsonify({
            "reply": "📲 Para Android TV, TV Box ou modelos Toshiba/Vizzion/Vidaa, baixe o app *Xtream IPTV Player*. Quando terminar, me avise aqui para te passar o número do teste. ⏳"
        })

    if "samsung" in msg:
        if "nova" in msg:
            return jsonify({
                "reply": "📺 Recomendo o app *Xcloud* (verde e preto). Se não funcionar, podemos tentar o *Duplecast* (com QR Code).\n\nBaixe o Xcloud e me avise. 😉"
            })
        elif "antiga" in msg:
            return jsonify({
                "reply": "🔁 Para Samsung antiga, digite o número *88* aqui após instalar o app indicado."
            })
        else:
            return jsonify({
                "reply": "Sua TV Samsung é modelo novo ou antigo? Me avise pra eu indicar o melhor app! 😉"
            })

    if "roku" in msg:
        return jsonify({
            "reply": "📺 Para Roku, use o app *Xcloud*. Se não funcionar, podemos usar o *OTT Player* (com QR Code). Baixe o Xcloud e me avise. 😉"
        })

    if "lg" in msg:
        return jsonify({
            "reply": "📺 Para LG, comece testando com o *Xcloud*. Se não funcionar, tentamos o *Duplecast* (QR Code) ou *SmartOne* (envie o MAC). Baixe o Xcloud e me avise. 😉"
        })

    if "philco" in msg:
        return jsonify({
            "reply": "Sua Philco é nova ou antiga? Se for antiga, digite *98*. Se for nova, posso sugerir um app ideal. 😉"
        })

    if "philips" in msg or "aoc" in msg:
        return jsonify({
            "reply": "📺 Para Philips ou AOC, recomendo *OTT Player* ou *Duplecast* (com QR Code). Me avise quando instalar! 😉"
        })

    # Cliente avisou que já instalou app
    if "baixei" in msg or "instalei" in msg or "pronto" in msg:
        numero = random.choice(numeros_login)
        agora = datetime.datetime.now()
        hora_envio = agora.strftime("%H:%M")
        return jsonify({
            "reply": f"✅ Perfeito! Digite aqui o número *{numero}* para gerar seu login de teste.\n\n⏱️ Login enviado às {hora_envio}. Daqui 30 minutos vou te perguntar se deu certo. Boa sorte! 🚀"
        })

    if "deu certo" in msg or "funcionou" in msg:
        return jsonify({
            "reply": "🙌 Que ótimo! Aproveite bem o teste. Em breve envio mais dicas úteis! 😉"
        })

    if "não funcionou" in msg or "nao funcionou" in msg or "deu erro" in msg:
        return jsonify({
            "reply": "😕 Que pena! Me diga o que aconteceu ou envie uma foto de como digitou o login, senha e DNS. Atenção às letras maiúsculas/minúsculas, sem espaços extras, etc."
        })

    if "acabou o teste" in msg or "acabou" in msg:
        return jsonify({
            "reply": f"⏳ Seu teste chegou ao fim.\n\n📦 Agora escolha seu plano e continue com a gente!\n\n{planos}"
        })

    # Mensagens aleatórias durante o teste
    if "tô testando" in msg or "estou testando" in msg:
        aviso = random.choice(avisos)
        return jsonify({
            "reply": aviso
        })

    return jsonify({
        "reply": "🤖 Atendimento inteligente! Me diga o que você precisa ou o modelo da sua TV, celular ou outro dispositivo. Estou aqui pra te ajudar!"
    })

if __name__ == "__main__":
    app.run(debug=True)
