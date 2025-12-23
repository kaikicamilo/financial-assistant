import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.services.transaction_service import TransactionService
from src.ai.classifier import classificar_transacao

# Configuração da página
st.set_page_config(page_title="AI Financial Assistant", layout="wide")

# Estilo para os cartões de métricas
st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

USER_ID = 1
USER_EMAIL = "teste@email.com"

# --- SIDEBAR ---
st.sidebar.title("🎮 Menu Principal")
aba = st.sidebar.radio("Ir para:", ["Dashboard", "Lançar Gasto", "Histórico"])

# --- ABA 1: DASHBOARD ---
if aba == "Dashboard":
    st.title("📊 Dashboard Financeiro")
    
    total_gasto = TransactionService.get_total_balance(USER_ID)
    previsao = TransactionService.get_spending_forecast(USER_ID)
    resumo_categorias = TransactionService.get_user_summary(USER_EMAIL)

    c1, c2, c3 = st.columns(3)
    c1.metric("Gasto Total", f"R$ {total_gasto:.2f}")
    c2.metric("Previsão (Fim do Mês)", f"R$ {previsao:.2f}")
    c3.metric("Média Diária", f"R$ {total_gasto/datetime.now().day:.2f}")

    st.markdown("---")
    
    if resumo_categorias:
        df_cat = pd.DataFrame(resumo_categorias)
        fig = px.pie(df_cat, values='total', names='categoria', hole=0.4, 
                     title="Distribuição por Categoria",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Lance um gasto para visualizar o gráfico.")

# --- ABA 2: LANÇAR GASTO ---
elif aba == "Lançar Gasto":
    st.title("💸 Novo Lançamento")
    
    with st.form("form_gasto", clear_on_submit=True):
        desc_bruta = st.text_input("Descrição da Compra", placeholder="Ex: iFood pedido #123")
        
        # Experiência natural: campo numérico que aceita decimais direto
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.01)
        
        # Seleção da Data
        data_selecionada = st.date_input("Data da Compra", datetime.now())
        
        submit = st.form_submit_button("Classificar e Salvar")

        if submit:
            if desc_bruta and valor > 0:
                with st.spinner("IA classificando..."):
                    resultado_ia = classificar_transacao(desc_bruta)
                    
                    # Salva no banco incluindo a data selecionada
                    sucesso = TransactionService.save_transaction_with_ai(
                        USER_ID, valor, desc_bruta, resultado_ia, data_selecionada
                    )
                    
                    if sucesso:
                        st.success(f"✅ Salvo: {resultado_ia.descricao_limpa} em {resultado_ia.categoria}")
                        st.balloons()
                    else:
                        st.error("Erro ao salvar no banco.")
            else:
                st.error("Preencha a descrição e o valor.")

# --- ABA 3: HISTÓRICO ---
elif aba == "Histórico":
    st.title("📜 Histórico de Transações")
    transacoes = TransactionService.get_all_transactions(USER_EMAIL)
    
    if transacoes:
        df = pd.DataFrame(transacoes)
        st.markdown("### Filtros")
        col_f, _ = st.columns([1, 1])
        categoria_filtro = col_f.multiselect("Filtrar por Categoria", df['Categoria'].unique())
        
        if categoria_filtro:
            df = df[df['Categoria'].isin(categoria_filtro)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhuma transação encontrada.")