from flask import Flask, request, jsonify
import openai
import requests
import re
import random
import time
import threading

app = Flask(__name__)

openai.api_key = "SUA_CHAVE_API"

# Webhooks por dispositivo
WEBHOOKS = {
    "xcloud": "https://a.opengl.in/chatbot/check/?k=66b125d558",
    "android": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "ios": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "pc": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "88": "https://painelacesso1.com/chatbot/check/?k=76be279cb5",
    "firestick": "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
}

# Controle de testes em andamento
testes_em_andamento = {}

def caracteres_parecidos(texto):
    texto = texto.strip()
    alertas = []
    if re.search(r"[Il]", texto):
        alertas.append("✅ Letra *I* maiúscula (de *Irlanda*) parece com *l* minúsculo (de *lápis*)")
    if re.search(r"[O0]", texto):
        alertas.append("✅ Letra *O* maiúscula (de *Ovo*) parece com *0* (zero)")
    return "\n".join(alertas)

def mensagens_durante_teste(numero, login_info):
    time.sleep(1800)  # 30 minutos
    mensagem = f"{numero}, deu certo o teste? Qualquer erro me diga! 👀\n\nSe não funcionou, me envie uma foto de como digitou o login. Verifique letras maiúsculas e minúsculas!"
    enviar_resposta(numero, mensagem)

    time.sleep(5400)  # mais 1h30 = total 2h
    mensagem2 = (
        "➡️ Alguns canais só abrem em dia de eventos\n"
        "*Ex: Disney+, HBO Max, Premiere, etc.*\n"
        "Esses só funcionam minutos antes da luta, futebol ou corrida começar. 🕒"
    )
    enviar_resposta(numero, mensagem2)

    time.sleep(1800)  # +30min = total 3h
    planos = (
        "⏱️ *Seu teste terminou!*\n\n"
        "👉 Gostou? Veja os planos abaixo:\n\n"
        "✅ R$ 26,00 - 1 mês\n"
        "✅ R$ 47,00 - 2 meses\n"
        "✅ R$ 68,00 - 3 meses\n"
        "✅ R$ 129,00 - 6 meses\n"
        "✅ R$ 185,00 - 1 ano\n\n"
        "💳 *Pagamento via PIX (CNPJ):* `41.638.407/0001-26`\n"
        "🔗 *Cartão:* https://link.mercadopago.com.br/cplay"
    )
    enviar_resposta(numero, planos)

def enviar_resposta(numero, texto):
    print(f"Mensagem para {numero}: {texto}")

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"replies": [{"message": "Dados inválidos."}]})

    mensagem = data["message"].strip()
    numero = data.get("sender", "cliente")

    # Verifica se é novo cliente
    boas_vindas = ""
    if numero.startswith("+55") and len(numero) >= 13:
        boas_vindas = (
            "👋 Olá! Seja bem-vindo!\n\n"
            "Oferecemos canais, filmes, séries e conteúdos ao vivo direto na sua TV, celular ou PC 📺🎬📱\n"
            "Vamos testar? Me diga qual é o seu dispositivo (ex: Android, LG, Roku, Samsung...)."
        )
        return jsonify({"replies": [{"message": boas_vindas}]})

    # Cliente informou o dispositivo
    dispositivo = mensagem.lower()

    if "samsung" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Para Samsung (modelos novos), baixe o app *Xcloud* (ícone verde e preto). Quando instalar, diga *instalei*."}]})

    if "roku" in dispositivo or "lg" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Baixe o app *Xcloud* (ícone verde e preto). Quando instalar, diga *instalei*."}]})

    if "philco" in dispositivo and "antiga" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Baixe o app *Smart STB* e me diga quando instalar."}]})

    if "philips" in dispositivo or "aoc" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Instale o app *OTT Player* ou *Duplecast* e me envie a foto do QR code da tela."}]})

    if "android" in dispositivo or "tv box" in dispositivo or "projetor" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Baixe o app *Xtream IPTV Player*. Quando terminar a instalação, diga *instalei*."}]})

    if "iphone" in dispositivo or "ios" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Baixe o app *Smarters Player Lite*. Quando terminar a instalação, diga *instalei*."}]})

    if "computador" in dispositivo or "pc" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Baixe esse app: https://7aps.online/iptvsmarters. Quando instalar, diga *instalei*."}]})

    if "fire" in dispositivo or "stick" in dispositivo:
        return jsonify({"replies": [{"message": "✅ Assista esse vídeo: https://youtu.be/gbZNfN3KxJs?si=8JDg7y0fHfewINdE\nDepois me diga quando instalou o app."}]})

    if mensagem.lower() == "instalei":
        # Verifica o último dispositivo mencionado
        ultima = data.get("last_device", "")
        tipo = "xcloud"  # padrão

        if "xtream" in ultima or "android" in ultima or "tv box" in ultima:
            tipo = "android"
        elif "iphone" in ultima or "ios" in ultima or "pc" in ultima or "computador" in ultima:
            tipo = "ios"
        elif "88" in ultima:
            tipo = "88"
        elif "fire" in ultima:
            tipo = "firestick"

        webhook = WEBHOOKS.get(tipo)
        if not webhook:
            return jsonify({"replies": [{"message": "❌ Erro ao localizar o app correto para seu dispositivo."}]})

        try:
            response = requests.get(webhook)
            dados = response.json()
            username = dados.get("username", "")
            password = dados.get("password", "")
            dns = dados.get("dns", "")

            login_msg = f"*Usuário:* {username}\n*Senha:* {password}"
            if dns:
                login_msg += f"\n*DNS:* {dns}"

            alertas = caracteres_parecidos(username + password)
            aviso = "\n⚠️ Atenção aos caracteres parecidos:\n" + alertas if alertas else ""
            aviso += "\n✍️ *Digite* o login exatamente como enviado (maiúsculas e minúsculas)."

            # Inicia o cronômetro do teste
            if numero not in testes_em_andamento:
                testes_em_andamento[numero] = True
                threading.Thread(target=mensagens_durante_teste, args=(numero, login_msg)).start()

            return jsonify({"replies": [{"message": f"✅ Teste ativado por 3 horas!\n\n{login_msg}{aviso}"}]})

        except Exception as e:
            return jsonify({"replies": [{"message": f"Erro ao gerar o login: {str(e)}"}]})

    # Resposta padrão
    return jsonify({"replies": [{"message": "🤖 Me diga qual é seu dispositivo (Samsung, Android, LG, Roku, etc) para continuarmos."}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
