from src.database.models import Session, Transaction, Category, User
from sqlalchemy import func
from datetime import datetime

class TransactionService:
    @staticmethod
    def get_total_balance(user_id):
        """Soma o valor de todas as transações de um usuário."""
        session = Session()
        try:
            total = session.query(func.sum(Transaction.valor)).filter_by(user_id=user_id).scalar()
            return total if total else 0.0
        finally:
            session.close()

    @staticmethod
    def get_spending_forecast(user_id):
        """Calcula previsão de gastos baseada na média diária atual."""
        session = Session()
        try:
            hoje = datetime.now()
            primeiro_dia = hoje.replace(day=1, hour=0, minute=0, second=0)
            gastos_mes = session.query(func.sum(Transaction.valor)).filter(
                Transaction.user_id == user_id,
                Transaction.data >= primeiro_dia
            ).scalar() or 0.0
            
            dias_passados = hoje.day
            # Projeta o gasto para 30 dias: (gasto_atual / dias_corridos) * 30
            return (gastos_mes / dias_passados) * 30
        finally:
            session.close()

    @staticmethod
    def get_user_summary(user_email):
        """Retorna o total por categoria para o gráfico de pizza."""
        session = Session()
        try:
            user = session.query(User).filter_by(email=user_email).first()
            if not user: return []
            
            results = session.query(
                Category.nome,
                func.sum(Transaction.valor).label('total')
            ).join(Transaction).filter(Transaction.user_id == user.id).group_by(Category.nome).all()
            
            return [{"categoria": r[0], "total": r[1]} for r in results]
        finally:
            session.close()

    @staticmethod
    def get_all_transactions(user_email):
        """Retorna a lista de transações formatada para a tabela de histórico."""
        session = Session()
        try:
            user = session.query(User).filter_by(email=user_email).first()
            if not user: return []
            
            transactions = session.query(Transaction).filter_by(user_id=user.id).order_by(Transaction.data.desc()).all()
            
            return [
                {
                    "Data": t.data.strftime("%d/%m/%Y"),
                    "Descrição": t.descricao_limpa,
                    "Categoria": t.category.nome if t.category else "Sem Categoria",
                    "Valor": f"R$ {t.valor:.2f}"
                } for t in transactions
            ]
        finally:
            session.close()

    @staticmethod
    def save_transaction_with_ai(user_id, valor, desc_bruta, resultado_ia, data_compra):
        """Busca/Cria categoria e salva a transação com a data escolhida."""
        session = Session()
        try:
            categoria = session.query(Category).filter_by(nome=resultado_ia.categoria).first()
            if not categoria:
                categoria = Category(nome=resultado_ia.categoria, tipo="despesa")
                session.add(categoria)
                session.flush()

            nova_transacao = Transaction(
                valor=valor,
                descricao_bruta=desc_bruta,
                descricao_limpa=resultado_ia.descricao_limpa,
                user_id=user_id,
                category_id=categoria.id,
                data=data_compra # <--- Usa a data vinda do formulário
            )
            session.add(nova_transacao)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()