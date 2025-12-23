from src.services.transaction_service import TransactionService

# Testando o Saldo e a Previsão
user_id = 1 # ID do usuário de teste que criamos antes
saldo = TransactionService.get_total_balance(user_id)
previsao = TransactionService.get_spending_forecast(user_id)

print(f"💰 Saldo Atual: R$ {saldo:.2f}")
print(f"🔮 Previsão de Gastos (Fim do Mês): R$ {previsao:.2f}")