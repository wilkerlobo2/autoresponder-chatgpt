// Webhook para AutoResponder com IA personalizada para atendimento IPTV

const express = require('express'); const bodyParser = require('body-parser'); const app = express(); const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

const listaAndroid = ['221', '225', '500', '555'];

function getRandomAndroidCode() { return listaAndroid[Math.floor(Math.random() * listaAndroid.length)]; }

const planos = `🌟 Planos disponíveis:

📅 1 mês – R$ 26,00 📅 2 meses – R$ 47,00 📅 3 meses – R$ 68,00 📅 6 meses – R$ 129,00 📅 1 ano – R$ 185,00

💳 Pagamento via: • PIX (CNPJ): 42.258.208/0001-10 • Cartão: https://pagamento.exemplo.com/cartao`;

const canaisInfo = ➡️ Alguns canais só abrem em dias de eventos: *EX: Disney+ , HBO Max, Premiere, Prime Video, Paramount...* Esses canais não têm programação diária. A transmissão geralmente só abre minutos antes do evento começar.;

const saudações = [ 'Olá! 👋 Seja bem-vindo! Que tal aproveitar um teste gratuito e conhecer o melhor do IPTV? 😎', 'Oi! 👋 Está pronto para testar o melhor do IPTV? Vamos te ajudar rapidinho!', 'Seja bem-vindo! Preparado para ver tudo o que a gente oferece? Vamos começar seu teste grátis! 📺' ];

const controleSessao = {};

app.post('/', async (req, res) => { const msg = req.body.message?.toLowerCase(); const nome = req.body.name || ''; const numero = req.body.number; const id = numero;

if (!controleSessao[id]) { controleSessao[id] = { etapa: 0, dispositivo: '', loginEnviado: false, horaLogin: null }; }

const sessao = controleSessao[id];

// Ignorar mensagens com mídia (áudio, imagem) if (req.body.message_type !== 'text') { return res.send({ reply: '📷 Recebi sua imagem ou áudio. Vou aguardar você digitar ou responder, tá bem? 😊' }); }

// Mensagem inicial (número não salvo) if (sessao.etapa === 0 && numero.startsWith('+55') && !nome) { sessao.etapa = 1; return res.send({ reply: ${saudações[Math.floor(Math.random() * saudações.length)]}\n\nPara qual dispositivo você quer testar o IPTV? 📲📺 }); }

// Espera tipo de dispositivo if (sessao.etapa === 1) { if (msg.includes('android') || msg.includes('box') || msg.includes('toshiba') || msg.includes('vizzion') || msg.includes('vidaa')) { sessao.dispositivo = 'android'; sessao.etapa = 2; return res.send({ reply: ✅ Baixe o app *Xtream IPTV Player* na sua TV.\n\nQuando terminar de instalar, me avise aqui. 😉 }); } if (msg.includes('samsung')) { sessao.dispositivo = 'samsung'; sessao.etapa = 2; return res.send({ reply: Seu modelo é antigo ou novo? }); } if (msg.includes('roku')) { sessao.dispositivo = 'roku'; sessao.etapa = 2; return res.send({ reply: 📲 Baixe primeiro o app *Xcloud* na sua Roku. Quando terminar de instalar, me avise aqui. }); } if (msg.includes('lg')) { sessao.dispositivo = 'lg'; sessao.etapa = 2; return res.send({ reply: 📲 Baixe primeiro o app *Xcloud*. Quando terminar, me avisa aqui que te dou o próximo passo. 😉 }); } if (msg.includes('philco')) { sessao.dispositivo = 'philco'; sessao.etapa = 2; return res.send({ reply: Sua Philco é modelo mais antigo ou novo? }); } if (msg.includes('aoc') || msg.includes('philips')) { sessao.dispositivo = 'aoc'; sessao.etapa = 2; return res.send({ reply: 📲 Para sua TV, baixe o app *OTT Player* ou *Duplecast*.\nQuando terminar de instalar, me avise aqui. }); } return res.send({ reply: Consegue me informar o modelo da sua TV com mais detalhes para que eu indique o app ideal? 😊 }); }

// Após instalar app if (sessao.etapa === 2 && msg.includes('baixei') || msg.includes('instalei')) { if (sessao.dispositivo === 'android') { sessao.etapa = 3; const code = getRandomAndroidCode(); sessao.loginEnviado = true; sessao.horaLogin = Date.now(); return res.send({ reply: ✅ Agora digite aqui o número *${code}* para gerar seu login de teste! }); } // Exemplo Roku, outros seguem lógica parecida if (sessao.dispositivo === 'roku') { sessao.etapa = 3; sessao.loginEnviado = true; sessao.horaLogin = Date.now(); return res.send({ reply: ✅ Agora digite o número *91* aqui para gerar seu login de teste. 😉 }); } return res.send({ reply: Ótimo! Agora me diga o número (caso tenha) ou envie o QR/MAC para eu prosseguir. 😊 }); }

// Verifica 30 min após login if (sessao.loginEnviado && Date.now() - sessao.horaLogin >= 30 * 60000 && !sessao.deuCertoPerguntado) { sessao.deuCertoPerguntado = true; return res.send({ reply: 🚀 Já se passaram 30 minutos... Deu tudo certo com o teste? }); }

if (msg.includes('não') && sessao.deuCertoPerguntado) { return res.send({ reply: 😕 Entendi... Me manda uma foto de como você digitou o login, senha e DNS.\n\n⚠️ Lembre-se: *respeite letras maiúsculas, minúsculas e espaços exatamente como foi enviado!* }); }

// Durante o período de teste, mensagens informativas if (sessao.loginEnviado && Date.now() - sessao.horaLogin < 3 * 60 * 60000) { const tempo = Math.floor((Date.now() - sessao.horaLogin) / 60000); if (tempo % 30 === 0) { return res.send({ reply: canaisInfo }); } }

// Teste terminou após 3h if (sessao.loginEnviado && Date.now() - sessao.horaLogin > 3 * 60 * 60000 && !sessao.finalizado) { sessao.finalizado = true; return res.send({ reply: 🕒 O teste gratuito foi encerrado.\n\nSe você gostou, aproveite e escolha um plano para continuar assistindo sem interrupções! 😍\n\n${planos} }); }

return res.send({ reply: 😉 Estou aqui para ajudar. Se precisar de algo, é só chamar! }); });

app.listen(PORT, () => { console.log(Servidor rodando na porta ${PORT}); });

