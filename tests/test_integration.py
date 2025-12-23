from src.database.models import Session, User, Category, Transaction, init_db
from src.ai.classifier import classificar_transacao
import os

def testar_fluxo_completo():
    # 1. Garantir que o banco existe e criar uma sessão
    init_db()
    session = Session()

    try:
        # 2. Criar um usuário de teste (se não existir)
        user = session.query(User).filter_by(email="teste@email.com").first()
        if not user:
            user = User(nome="Usuário Teste", email="teste@email.com")
            session.add(user)
            session.commit()
            print(f"✅ Usuário '{user.nome}' criado.")

        # 3. Lista de gastos "sujos" para testar a IA
        gastos_sujos = [
            "PIX*D231225*RESTAURANTE SABOR E CIA LTDA 123", # Sujeira de PIX + Nome longo
            "UBER *PENDING *23/12/2025 *AMSTERDAM_AIRP",   # Localização internacional + data
            "FARMACIA_PAGUE_MENOS_FILIAL_GOIANIA_CNPJ_000", # Nome técnico de nota fiscal
            "APPLE.COM/BILL*ONE-MONTH*FAMILY-PLAN*99",     # Assinatura com muitos detalhes
            "BALADA_TOP_OPEN_BAR_NOITE_SABADO_Vip",        # Gasto de lazer disfarçado
            "PAG*Amazon*Prime*Video*Recurrent*77",         # Assinatura com códigos de pagamento
            "ESTACIONAMENTO_PARK_CENTRE_12:30_S_PAULO",    # Símbolos de hora e local
            "LOJA_CONVENIENCIA_SHELL_SELECT_SP_BR",        # Regra de posto (Transporte)
            "IFD*IFOOD*SAO_PAULO_BRA_PEDIDO_#9876",        # Pedido com hashtag e códigoss
            "SMART FIT*ACADEMIA*MES_DEZEMBRO",             # Saúde
            "BAR DO ZE - UNIDADE 2 - PIX_TRANSF",          # Lazer (Bar)
            "COMPRA_MATERIAIS_CONSTRUCAO_C_PEDRO"          # Moradia/Outros?
        ]

        print("\n🚀 Iniciando classificação e salvamento...")

        for desc in gastos_sujos:
            # Chama a Task 3 (IA)
            resultado_ia = classificar_transacao(desc)
            
            # Busca ou cria a categoria no banco
            categoria = session.query(Category).filter_by(nome=resultado_ia.categoria).first()
            if not categoria:
                categoria = Category(nome=resultado_ia.categoria, tipo="despesa")
                session.add(categoria)
                session.commit()

            # Cria a transação (Task 2)
            nova_transacao = Transaction(
                valor=50.0, # Valor fictício para o teste
                descricao_bruta=desc,
                descricao_limpa=resultado_ia.descricao_limpa,
                user_id=user.id,
                category_id=categoria.id,
                metadata_ia={"origem": "teste_integracao"} # Guardando info extra no JSON
            )
            
            session.add(nova_transacao)
            print(f"✔ Salvo: {desc} -> {resultado_ia.descricao_limpa} [{resultado_ia.categoria}]")

        session.commit()
        print("\n✨ Teste concluído com sucesso!")

    except Exception as e:
        session.rollback()
        print(f"❌ Erro no teste: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    testar_fluxo_completo()