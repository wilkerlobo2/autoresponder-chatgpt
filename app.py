from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/', methods=['POST'])
def responder():
    data = request.get_json()
    msg = data['query']['message'].lower()
    nome = data['query']['sender']
    respostas = []

    # 👋 Boas-vindas para número novo
    if nome.startswith("+55") and len(msg) < 20:
        respostas.append({"message": "👋 Olá! Que bom que chegou até aqui. Posso te liberar um teste agora mesmo!"})
        respostas.append({"message": "Só preciso saber em qual dispositivo você vai assistir (TV, celular, PC, etc.)."})
        return jsonify({"replies": respostas})

    # Atendimento padrão para dúvidas
    if 'oi' in msg or 'olá' in msg:
        respostas.append({"message": "🤖 Sou seu assistente para tirar dúvidas e te ajudar com o teste."})
        respostas.append({"message": "Me diga o modelo da sua TV ou dispositivo para eu te indicar o app ideal."})
        return jsonify({"replies": respostas})

    # Reconhecer marcas e pedir mais detalhes
    if 'samsung' in msg:
        respostas.append({"message": "Sua TV Samsung é modelo novo ou antigo?"})
        return jsonify({"replies": respostas})

    if 'philco' in msg:
        respostas.append({"message": "Sua TV Philco é nova ou antiga?"})
        respostas.append({"message": "Se for antiga, digite o número 98 para gerar o teste."})
        return jsonify({"replies": respostas})

    if 'lg' in msg:
        respostas.append({"message": "Recomendo começar pelo app Xcloud (ícone verde com preto). Já está instalado?"})
        return jsonify({"replies": respostas})

    if 'roku' in msg:
        respostas.append({"message": "Recomendo primeiro testar com o app Xcloud (ícone verde com preto). Já está instalado?"})
        return jsonify({"replies": respostas})

    if 'android' in msg or 'tv box' in msg or 'toshiba' in msg or 'vizzion' in msg or 'vidaa' in msg:
        respostas.append({"message": "Perfeito! Baixe o app Xtream IPTV Player e me avise quando estiver pronto."})
        return jsonify({"replies": respostas})

    if 'baixei' in msg or 'instalei' in msg or 'pronto' in msg:
        numero = random.choice(['221', '225', '500', '555'])
        respostas.append({"message": f"✅ Ótimo! Agora digite o número *{numero}* aqui mesmo pra eu liberar seu teste."})
        return jsonify({"replies": respostas})

    if 'recebi' in msg or 'login' in msg:
        respostas.append({"message": "⏳ Em cerca de 30 minutos vou te perguntar se funcionou, combinado?"})
        return jsonify({"replies": respostas})

    if 'deu certo' in msg:
        respostas.append({"message": "Show! Aproveite o teste. 😉"})
        return jsonify({"replies": respostas})

    if 'nao funcionou' in msg or 'não funcionou' in msg:
        respostas.append({"message": "😕 Entendi. Pode me mandar uma foto de como digitou o login?"})
        respostas.append({"message": "Verifique se está copiando certo, com letras maiúsculas e minúsculas do jeito que foi enviado."})
        return jsonify({"replies": respostas})

    if 'acabou' in msg or 'terminou' in msg:
        respostas.append({"message": "🕒 O teste chegou ao fim. Se curtiu, olha só os planos disponíveis:"})
        respostas.append({"message": "📅 1 mês – R$ 26,00\n📅 2 meses – R$ 47,00\n📅 3 meses – R$ 68,00\n📅 6 meses – R$ 129,00\n📅 1 ano – R$ 185,00"})
        respostas.append({"message": "💰 Formas de pagamento:\nPIX (CNPJ): 00.000.000/0001-00\n💳 Cartão: https://pagamento.exemplo.com"})
        return jsonify({"replies": respostas})

    if 'dica' in msg or 'canal' in msg:
        respostas.append({"message": "➡️ Alguns canais só abrem em dia de eventos."})
        respostas.append({"message": "*EX: Disney+, HBO Max, Premiere, Prime Video, Paramount...*"})
        respostas.append({"message": "Eles funcionam só minutos antes do evento ao vivo começar. 😉"})
        return jsonify({"replies": respostas})

    # Caso nada corresponda
    respostas.append({"message": "💬 Me diga o modelo da sua TV ou dispositivo para eu sugerir o melhor app e o número pra teste."})
    return jsonify({"replies": respostas})

# 👇 Essa linha deve ficar fora da função!
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
