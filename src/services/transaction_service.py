from src.database.models import Session, Transaction, Category, User
from sqlalchemy import func
from datetime import datetime, timedelta

class TransactionService:
    @staticmethod
    def create_transaction(user_id, valor, desc_bruta, desc_limpa, category_id, metadata=None):
        """Cria uma nova transação no banco (Create)."""
        session = Session()
        try:
            nova_transacao = Transaction(
                valor=valor,
                descricao_bruta=desc_bruta,
                descricao_limpa=desc_limpa,
                user_id=user_id,
                category_id=category_id,
                metadata_ia=metadata
            )
            session.add(nova_transacao)
            session.commit()
            return nova_transacao
        finally:
            session.close()

    @staticmethod
    def get_user_transactions(user_id):
        """Lista todas as transações de um usuário (Read)."""
        session = Session()
        try:
            return session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.data.desc()).all()
        finally:
            session.close()

    @staticmethod
    def get_total_balance(user_id):
        """Calcula o Saldo Atual (Receitas - Despesas)."""
        session = Session()
        try:
            # Soma despesas e receitas separadamente baseado no tipo da categoria
            # Assumindo que você cadastrou 'receita' e 'despesa' no banco
            total = session.query(func.sum(Transaction.valor)).filter_by(user_id=user_id).scalar()
            return total if total else 0.0
        finally:
            session.close()

    @staticmethod
    def get_spending_forecast(user_id):
        """
        Implementa uma lógica simples de Previsão de Gastos.
        Baseia-se na média de gastos diários do mês atual para prever o final do mês.
        """
        session = Session()
        try:
            hoje = datetime.now()
            primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0)
            
            # Gastos do mês atual
            gastos_mes = session.query(func.sum(Transaction.valor)).filter(
                Transaction.user_id == user_id,
                Transaction.data >= primeiro_dia_mes
            ).scalar() or 0.0
            
            dias_passados = hoje.day
            media_diaria = gastos_mes / dias_passados
            
            # Previsão para 30 dias
            previsao_final_mes = media_diaria * 30
            return previsao_final_mes
        finally:
            session.close()