from flask import Flask, request, jsonify
import random
import time
import threading
import requests

app = Flask(__name__)

# Webhooks para gerar login automaticamente
WEBHOOK_ANDROID = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"
WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_SMARTERS = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Lista de números brasileiros salvos para evitar repetir boas-vindas
clientes_atendidos = {}

# Função para enviar mensagem futura (como lembrete de 30 min, fim de teste, etc)
def enviar_mensagem_futura(resposta_func, delay, *args):
    def tarefa():
        time.sleep(delay)
        resposta_func(*args)
    threading.Thread(target=tarefa).start()

# Simula envio de mensagem (ajuste para usar via API do WhatsApp se desejar)
def simular_envio(mensagem):
    print(f"\n[ENVIO SIMULADO] {mensagem}")

@app.route("/", methods=["GET"])
def home():
    return "Servidor Flask online - Atendimento IPTV"

@app.route("/", methods=["POST"])
def receber_mensagem():
    dados = request.get_json()
    if not dados or "message" not in dados:
        return jsonify({"error": "Formato inválido. Esperado JSON com chave 'message'."}), 400

    mensagem = dados["message"].lower()
    numero = dados.get("number", "cliente")

    resposta = ""

    # Boas-vindas personalizadas para números novos (sem nome)
    if numero.startswith("+55") and numero not in clientes_atendidos:
        clientes_atendidos[numero] = True
        resposta += (
            "Olá! Bem-vindo(a)! 😄\n"
            "Oferecemos acesso a *Canais ao vivo, Filmes e Séries* 🎬📺.\n"
            "Vamos iniciar seu teste gratuito! Me diga: *qual o modelo ou tipo do seu aparelho?*\n"
        )
        return jsonify({"messages": [resposta]})

    # Samsung
    if "samsung" in mensagem:
        if "antiga" in mensagem:
            resposta = (
                "Para Samsung antiga, siga este vídeo tutorial:\n"
                "https://youtu.be/2ajEjRyKzeU?si=0mbSVYrOkU_2-hO0\n\n"
                "Configure com este DNS:\n64.31.61.14\n\n"
                "Depois:\n1 - Desligue e ligue a TV novamente\n"
                "2 - Instale o app *SMART STB*\n\n"
                "Aguarde... preparando seu login de teste..."
            )
            simular_envio(resposta)
            enviar_mensagem_futura(enviar_login_manual, 5, numero, "88")
            return jsonify({"messages": ["Ok! Enviando instruções..."]})
        else:
            resposta = (
                "Certo! Baixe o aplicativo *Xcloud* (ícone verde e preto) na sua Samsung 📺\n"
                "Quando terminar de baixar, me avise escrevendo: *baixei xcloud*"
            )
            return jsonify({"messages": [resposta]})

    # Roku ou LG
    if "roku" in mensagem or "lg" in mensagem:
        resposta = (
            "Perfeito! Baixe o app *Xcloud* (verde e preto) direto na sua TV.\n"
            "Depois que baixar, me envie: *baixei xcloud*"
        )
        return jsonify({"messages": [resposta]})

    # Computador ou iPhone
    if "iphone" in mensagem or "ios" in mensagem or "computador" in mensagem:
        resposta = (
            "Baixe o app *Smarters Player Lite* no seu dispositivo.\n"
            "Quando finalizar, diga: *baixei smarters*"
        )
        return jsonify({"messages": [resposta]})

    # Android
    if "android" in mensagem or "tv box" in mensagem:
        resposta = (
            "Ótimo! Baixe o app *Xtream IPTV Player* (ícone laranja e roxo).\n"
            "Quando terminar de instalar, envie: *baixei xtream*"
        )
        return jsonify({"messages": [resposta]})

    # Philco antiga
    if "philco" in mensagem and "antiga" in mensagem:
        resposta = (
            "Para Philco antiga, você vai usar o app *Smart STB* com DNS.\n"
            "Aguarde... preparando login..."
        )
        simular_envio(resposta)
        enviar_mensagem_futura(enviar_login_manual, 5, numero, "88")
        return jsonify({"messages": ["Tudo certo. Um instante..."]})

    # Confirmou download do app
    if "baixei xcloud" in mensagem:
        resposta = "Perfeito! Gerando seu login de teste..."
        simular_envio(resposta)
        gerar_login(numero, "xcloud")
        return jsonify({"messages": ["Aguarde um momento..."]})

    if "baixei xtream" in mensagem:
        resposta = "Legal! Preparando seu acesso..."
        simular_envio(resposta)
        gerar_login(numero, "android")
        return jsonify({"messages": ["Um instante..."]})

    if "baixei smarters" in mensagem:
        resposta = "Gerando login de teste para seu dispositivo..."
        simular_envio(resposta)
        gerar_login(numero, "smarters")
        return jsonify({"messages": ["Pronto! Aguarde..."]})

    # Resposta padrão
    return jsonify({"messages": ["Me diga qual é seu aparelho ou modelo da TV para continuarmos."]})


# Envia login usando o webhook correto
def gerar_login(numero, tipo):
    if tipo == "xcloud":
        url = WEBHOOK_XCLOUD
    elif tipo == "android":
        url = WEBHOOK_ANDROID
    elif tipo == "smarters":
        url = WEBHOOK_SMARTERS
    else:
        return

    try:
        r = requests.get(url)
        if r.status_code == 200:
            dados = r.text
            simular_envio(f"Seguem seus dados de teste para IPTV:\n{dados}")
            enviar_mensagem_futura(verificar_sucesso, 1800, numero)
            enviar_mensagem_futura(mensagem_durante_teste, 3600, numero)
            enviar_mensagem_futura(mensagem_final, 10800, numero)
        else:
            simular_envio("Houve um erro ao gerar seu teste. Tente novamente mais tarde.")
    except Exception as e:
        simular_envio(f"Erro na geração do login: {e}")

# Para dispositivos que exigem mensagem com login manual
def enviar_login_manual(numero, codigo):
    simular_envio(
        "Login gerado com sucesso! Veja abaixo 👇\n"
        f"(Simulando login do número {codigo})"
    )

# Após 30 minutos, perguntar se funcionou
def verificar_sucesso(numero):
    simular_envio(
        "Passaram 30 minutos desde o envio do teste. Funcionou tudo certinho?\n"
        "Se sim, ótimo! 😄\nSe não, me envie uma *foto da tela* ou descreva o erro.\n"
        "Verifique se digitou exatamente como enviado (letras maiúsculas e minúsculas)."
    )

# Durante o teste, enviar mensagens úteis
def mensagem_durante_teste(numero):
    simular_envio(
        "Aviso importante! ➡️ Alguns canais só funcionam durante eventos ao vivo.\n"
        "Ex: Disney+, HBO Max, Premiere...\n"
        "Eles aparecem só minutos antes do evento começar. 🎥⚽🎬"
    )

# Final do teste: apresentar planos
def mensagem_final(numero):
    simular_envio(
        "O teste gratuito de 3 horas chegou ao fim! 🕒\n"
        "Se você gostou, veja nossos planos abaixo:\n\n"
        "✅ R$ 26,00 - 1 mês\n"
        "✅ R$ 47,00 - 2 meses\n"
        "✅ R$ 68,00 - 3 meses\n"
        "✅ R$ 129,00 - 6 meses\n"
        "✅ R$ 185,00 - 1 ano\n\n"
        "📌 Formas de pagamento:\n\n"
        "🔸 PIX (CNPJ): 41.638.407/0001-26\n"
        "🔸 Cartão: https://link.mercadopago.com.br/cplay\n"
        "Chave CNPJ - Axel Castelo\n\n"
        "Ficou com alguma dúvida? Estou aqui pra ajudar! 😊"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
