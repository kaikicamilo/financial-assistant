from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from src.services.transaction_service import TransactionService
from src.ai.classifier import classificar_transacao
from datetime import datetime

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    # 1. Recebe os dados do Twilio
    msg_recebida = request.values.get('Body', '').lower()
    user_phone = request.values.get('From', '')
    
    response = MessagingResponse()
    
    # 2. Lógica do Comando /gasto [valor] [descrição]
    if msg_recebida.startswith('/gasto'):
        try:
            # Parse básico: /gasto 35.00 almoco
            partes = msg_recebida.split(' ', 2)
            valor = float(partes[1].replace(',', '.'))
            desc_bruta = partes[2]
            
            # 3. Processamento Inteligente (IA + Banco)
            # Reutilizamos a Task 3 (IA)
            res_ia = classificar_transacao(desc_bruta)
            
            # Reutilizamos a Task 4 (Service)
            USER_ID = 1 # Por enquanto fixo para seus testes
            sucesso = TransactionService.save_transaction_with_ai(
                USER_ID, valor, desc_bruta, res_ia, datetime.now()
            )
            
            if sucesso:
                resposta = (f"✅ *Gasto Registrado!*\n\n"
                            f"💰 *Valor:* R$ {valor:.2f}\n"
                            f"📝 *Item:* {res_ia.descricao_limpa}\n"
                            f"📂 *Categoria:* {res_ia.categoria}")
            else:
                resposta = "❌ Erro técnico ao salvar no banco."
                
        except (IndexError, ValueError):
            resposta = "⚠️ Formato inválido! Use: `/gasto 35.00 almoco`"
    else:
        resposta = "🤖 Olá! Eu sou seu Assistente Financeiro. Use o comando `/gasto` para registrar algo."

    response.message(resposta)
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)