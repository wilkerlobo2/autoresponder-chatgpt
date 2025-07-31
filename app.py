from flask import Flask, request, jsonify import random import time

app = Flask(name)

Simula armazenamento de estado temporário

user_states = {}

Planos formatados com emoji

planos = ( "\n🌟 Planos disponíveis:\n" "1 mês – R$ 26,00\n" "2 meses – R$ 47,00\n" "3 meses – R$ 68,00\n" "6 meses – R$ 129,00\n" "1 ano – R$ 185,00\n\n" "💳 Pagamento via cartão: [LINK_AQUI]\n" "📲 PIX (CNPJ): 00.000.000/0000-00" )

Sorteia um número de login

numeros_login = ['221', '225', '500', '555']

Detecta se o contato é novo

def cliente_novo(nome): return nome.startswith('+55')

Aguarda app baixado antes de mandar número

def app_instalado_confirmado(usuario): return user_states.get(usuario, {}).get("app_baixado", False)

Marca que o app foi baixado

def registrar_download(usuario): user_states.setdefault(usuario, {})["app_baixado"] = True

Registra hora do envio do login

def registrar_envio_login(usuario): user_states.setdefault(usuario, {})["hora_login"] = time.time()

Verifica se passaram 30 minutos

def passou_30_minutos(usuario): hora = user_states.get(usuario, {}).get("hora_login") return hora and time.time() - hora > 1800

Verifica se passou 3 horas

def passou_3_horas(usuario): hora = user_states.get(usuario, {}).get("hora_login") return hora and time.time() - hora > 10800

@app.route('/', methods=['POST']) def responder(): dados = request.json nome = dados.get("name", "") mensagem = dados.get("message", "").lower() usuario = dados.get("id", "")

# Mensagem com foto/áudio? Deixa para atendimento manual
if dados.get("hasMedia"):
    return jsonify({"reply": None})

# Cliente novo
if cliente_novo(nome):
    return jsonify({"reply": (
        "👋 Olá! Seja bem-vindo! Que tal testar nosso serviço de IPTV com qualidade profissional?\n"
        "Me diz qual dispositivo você quer usar pra assistir, que te mando o app ideal."
    )})

# Pergunta sobre modelo
if any(p in mensagem for p in ["samsung", "philco", "lg", "philips", "aoc", "roku", "fire", "ios", "android", "pc", "computador"]):
    if "samsung" in mensagem:
        return jsonify({"reply": "Seu modelo é antigo ou

