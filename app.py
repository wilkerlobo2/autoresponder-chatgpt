from flask import Flask, request, jsonify from openai import OpenAI import os import re import requests

app = Flask(name) client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558" WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

Armazenamento temporário de conversas por número (em memória RAM)

historico_conversas = {}

def gerar_boas_vindas(nome): if nome.startswith("+55"): return ( "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a canais de TV, filmes e séries. 📺🍿\n" "Vamos começar seu teste gratuito?\n\n" "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)." ) return None

def gerar_login(webhook): try: r = requests.get(webhook, timeout=10) if r.status_code == 200: data = r.json() username = data.get("username", "") password = data.get("password", "") dns = data.get("dns", "") msg = f"Usuário: {username}\nSenha: {password}" if dns: msg += f"\nDNS: {dns}"

aviso = ""
        if re.search(r"[IlO0]", username):
            aviso += "\n\n⚠️ *Atenção com o login:*\n"
            if "I" in username:
                aviso += "✅ Letra *I* de *Índia*\n"
            if "l" in username:
                aviso += "✅ Letra *l* minúscula de *lápis*\n"
            if "O" in username:
                aviso += "✅ Letra *O* de *Ovo*\n"
            if "0" in username:
                aviso += "✅ Número *0* (zero)\n"
            aviso += "Digite exatamente como enviado, respeitando maiúsculas e minúsculas."

        return msg + "\n\n⏳ *Seu teste dura 3 horas.*" + aviso
    else:
        return "❌ Erro ao gerar o login. Tente novamente em instantes."
except:
    return "⚠️ Erro ao conectar com o servidor de testes."

@app.route("/", methods=["POST"]) def responder(): data = request.get_json() nome = data.get("name", "") numero = nome.strip() mensagem = data.get("message", "").lower() resposta = []

# Salvar mensagem no histórico do número
if numero not in historico_conversas:
    historico_conversas[numero] = []
historico_conversas[numero].append(f"Cliente: {mensagem}")

# Boas-vindas para novos contatos
boasvindas = gerar_boas_vindas(numero)
if boasvindas:
    historico_conversas[numero].append(f"IA: {boasvindas}")
    resposta.append({"message": boasvindas})
    return jsonify({"replies": resposta})

# Prompt com memória
contexto = "\n".join(historico_conversas[numero][-8:])  # Limita as 8 últimas mensagens para não pesar

prompt = (
    f"Histórico recente com o cliente:\n{contexto}\n\n"
    f"Mensagem mais recente: '{mensagem}'\n\n"
    "Interprete com inteligência e responda conforme as regras abaixo:\n\n"
    "1. Convide para teste grátis e pergunte o aparelho.\n"
    "2. Se mencionar Roku, LG, Samsung, Philco: indicar *Xcloud*.\n"
    "3. Android, TV Box, Celular, Fire Stick: indicar *Xtream IPTV Player*.\n"
    "4. iPhone/iOS ou computador: indicar *Smarters Player Lite*.\n"
    "5. AOC/Philips: indicar *OTT Player* ou *Duplecast* (pedir QR).\n"
    "6. Se usar SmartOne, pedir MAC.\n"
    "7. Se disser que já instalou (ex: 'instalei', 'baixei'), gerar login.\n"
    f"   - Use {WEBHOOK_XCLOUD} se for Xcloud.\n"
    f"   - Use {WEBHOOK_GERAL} para os demais.\n"
    "8. Sempre seja criativo e claro.\n"
    "9. Não diga 'colar o login'. Use 'digitar o login'.\n"
    "10. Se disser que terminou o teste, envie planos.\n"
    "11. Se der erro, oriente a reenviar ou mandar print.\n"
    "12. Explique o que é IPTV se perguntar.\n\n"
    "Apenas responda com o texto exato que a IA deve enviar no WhatsApp."
)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    texto = response.choices[0].message.content
    historico_conversas[numero].append(f"IA: {texto}")

    # Se cliente disse que instalou
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
        if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
            login = gerar_login(WEBHOOK_XCLOUD)
        else:
            login = gerar_login(WEBHOOK_GERAL)

        resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
    else:
        resposta.append({"message": texto})

except Exception as e:
    resposta.append({"message": f"⚠️ Ocorreu um erro: {str(e)}"})

return jsonify({"replies": resposta})

if name == "main": app.run(host="0.0.0.0", port=10000)

