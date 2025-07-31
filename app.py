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

💰 Pagamento via:
PIX (CNPJ): 00.000.000/0001-00
Cartão: https://seulinkdepagamento"""

# Função para escolher número de teste aleatório
def gerar_numero_teste():
    return random.choice(['221', '225', '500', '555'])

@app.route('/', methods=['POST'])
def responder():
    data = request.get_json()
    msg = data.get('message', '').lower()
    nome = data.get('name', '')
    eh_novo = nome.startswith('+55')

    respostas = []

    # Saudação para novos clientes
    if 'teste' in msg or 'quero testar' in msg:
        if eh_novo:
            respostas.append("👋 Olá! Que bom ter você aqui. Vamos liberar um teste pra você conhecer nosso serviço.")
        respostas.append("Me diz qual dispositivo você vai usar pra testar? (Android TV, Samsung, Roku, LG, Celular, etc)")
        return jsonify({"replies": respostas})

    # Lógica por tipo de TV
    if 'android' in msg:
        respostas.append("📲 Para Android TV, TV Box ou modelos Toshiba/Vizzion/Vidaa, baixe o app *Xtream IPTV Player*.")
        respostas.append("Quando terminar, me avise aqui pra te passar o número de teste.")
        return jsonify({"replies": respostas})

    if 'samsung' in msg:
        if 'nova' in msg:
            respostas.append("📺 Para Samsung nova, baixe o app *Xcloud* (verde com preto). Me avise quando instalar.")
        elif 'antiga' in msg:
            respostas.append("✅ Seu modelo é antigo. Digite o número *88* para gerar seu teste.")
        else:
            respostas.append("Seu modelo é novo ou antigo?")
        return jsonify({"replies": respostas})

    if 'roku' in msg:
        respostas.append("📺 Baixe o app *Xcloud* (verde com preto). Se não funcionar, podemos testar o *OTT Player* (envie o QR code).")
        respostas.append("Me avise quando instalar o Xcloud.")
        return jsonify({"replies": respostas})

    if 'lg' in msg:
        respostas.append("📺 Para LG, baixe o *Xcloud* primeiro.")
        respostas.append("Se não funcionar, temos como alternativa o *Duplecast* (com QR) ou *SmartOne* (com MAC).")
        respostas.append("Me avise quando instalar.")
        return jsonify({"replies": respostas})

    if 'philco' in msg:
        if 'antiga' in msg:
            respostas.append("✅ Seu modelo é antigo. Digite o número *98* para gerar seu teste.")
        else:
            respostas.append("Seu modelo é antigo ou novo?")
        return jsonify({"replies": respostas})

    if 'philips' in msg or 'aoc' in msg:
        respostas.append("📺 Indico o app *OTT Player* ou *Duplecast*. Me envie o QR code após instalar.")
        return jsonify({"replies": respostas})

    if 'computador' in msg or 'pc' in msg:
        respostas.append("💻 Te envio o link do app e depois você digita o número *224* para gerar o teste.")
        return jsonify({"replies": respostas})

    if 'iphone' in msg or 'ios' in msg:
        respostas.append("📱 Baixe o app *Smarters Player Lite* na App Store. Me avise quando instalar pra te passar o número.")
        return jsonify({"replies": respostas})

    if 'fire stick' in msg or 'amazon' in msg:
        respostas.append("🔥 Para Fire Stick / Amazon, veja esse vídeo tutorial: [seu link aqui]")
        respostas.append("Depois digite o número *221* para gerar o teste.")
        return jsonify({"replies": respostas})

    # Quando cliente já tiver o app instalado
    if 'smartone' in msg:
        respostas.append("📟 Me envie o MAC que aparece no app SmartOne para liberar o teste.")
        return jsonify({"replies": respostas})

    if 'duplecast' in msg or 'ott player' in msg:
        respostas.append("📸 Me envie o QR code do app para que eu possa configurar o teste.")
        return jsonify({"replies": respostas})

    # Após o app ser instalado
    if 'instalei' in msg or 'baixei' in msg or 'pronto' in msg:
        numero = gerar_numero_teste()
        respostas.append(f"✅ Ótimo! Agora digite o número *{numero}* para gerar seu login de teste.")
        return jsonify({"replies": respostas})

    # Após envio de login, 30 minutos depois
    if 'recebi' in msg or 'login' in msg:
        respostas.append("⏱️ Em cerca de 30 minutos te pergunto se deu certo, tudo bem?")
        return jsonify({"replies": respostas})

    if 'deu certo' in msg:
        respostas.append("Show! Aproveite o teste. Qualquer dúvida, estou por aqui. 😉")
        return jsonify({"replies": respostas})

    if 'nao funcionou' in msg or 'não funcionou' in msg or 'erro' in msg:
        respostas.append("😕 Entendi. Pode me mandar uma foto de como digitou login, senha e DNS?")
        respostas.append("Verifique se está copiando tudo certinho: maiúsculas, minúsculas, espaços, etc.")
        return jsonify({"replies": respostas})

    if 'acabou' in msg or 'terminou' in msg:
        respostas.append("🕒 O teste chegou ao fim.")
        respostas.append(planos)
        return jsonify({"replies": respostas})

    # Dicas criativas durante as 3 horas de teste
    if 'dica' in msg or 'canal' in msg:
        respostas.append("➡️ Alguns canais só abrem em dias de eventos.")
        respostas.append("*EX: Disney+, HBO Max, Premiere, Prime Vídeo, Paramount...*")
        respostas.append("Eles funcionam só minutos antes do evento (luta, futebol, etc).")
        return jsonify({"replies": respostas})

    # Atendimento padrão para dúvidas e novas mensagens
respostas.append("🤖 Sou seu assistente para te ajudar com o IPTV.")
respostas.append("Me diga o modelo da sua TV ou o dispositivo que você quer usar.")
return jsonify({"replies": respostas})

# 👇 ESSA LINHA DEVE FICAR FORA DA FUNÇÃO responder()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
