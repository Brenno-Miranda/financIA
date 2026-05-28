import streamlit as st
import uuid
import pandas as pd
import database
from agent import get_agent

# Garante a criação do banco de dados corrigido
database.init_db()

st.set_page_config(page_title="Gestão Financeira IA", layout="wide")

# --- CONTROLE DE MULTI-SESSÃO ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu gerenciador de fluxo de caixa. Pode me falar sobre seus ganhos (Receitas) ou gastos (Despesas)!"}
    ]

# --- SIDEBAR DE APRESENTAÇÃO ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    st.caption(f"ID do Usuário Atual:\n{st.session_state.session_id}")
    st.markdown("---")
    if st.button("🔄 Simular Novo Usuário (Reset)"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [{"role": "assistant", "content": "Nova sessão iniciada! O que vamos registrar hoje?"}]
        st.rerun()

st.title("💸 Assistente & Dashboard Financeiro IA")
st.markdown("Gerencie suas finanças conversando e acompanhe os dados estruturados em tempo real.")

# --- CRIAÇÃO DAS ABAS ---
tab_chat, tab_dashboard = st.tabs(["💬 Conversa com o Agente", "📊 Painel & Filtros Dinâmicos"])

# --- CONTEÚDO DA ABA 1: CHAT CONVERSACIONAL ---
with tab_chat:
    
    # MUDANÇA AQUI: Criamos um container com altura fixa para as mensagens rolarem por dentro
    container_mensagens = st.container(height=500, border=False)
    
    # Renderiza histórico de conversas DENTRO do container
    with container_mensagens:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Entrada de texto do Chat (Fica solto na aba, sempre abaixo do container)
    if prompt := st.chat_input("Ex: Recebi 1200 reais de um freela de design hoje de manhã"):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Renderiza a nova mensagem do usuário DENTRO do container
        with container_mensagens:
            with st.chat_message("user"):
                st.markdown(prompt)

            # Processa e renderiza a resposta da IA DENTRO do container
            with st.chat_message("assistant"):
                with st.spinner("O agente está processando..."):
                    agente = get_agent(st.session_state.session_id)
                    resposta = agente.run(prompt)
                    texto_resposta = resposta.content
                    
                    st.markdown(texto_resposta)
                    st.session_state.messages.append({"role": "assistant", "content": texto_resposta})


# --- CONTEÚDO DA ABA 2: DASHBOARD DE CONSULTA ---
with tab_dashboard:
    st.subheader("🔍 Filtros Avançados do Banco de Dados")
    
    # Busca dados em tempo real direto do SQLite
    lista_dados = database.listar_transacoes(st.session_state.session_id)
    
    if lista_dados:
        df = pd.DataFrame(lista_dados)
        
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            filtro_tipo = st.selectbox("Tipo de Movimentação", ["Todos", "Receita", "Despesa"])
        with f_col2:
            lista_categorias = ["Todas"] + sorted(list(df["Categoria"].unique()))
            filtro_cat = st.selectbox("Categoria", lista_categorias)
        with f_col3:
            tot_rec = df[df["Tipo"] == "Receita"]["Valor (R$)"].sum()
            tot_des = df[df["Tipo"] == "Despesa"]["Valor (R$)"].sum()
            saldo_liquido = tot_rec - tot_des
            st.metric(label="Saldo Atual Líquido", value=f"R$ {saldo_liquido:.2f}", delta=f"{saldo_liquido:.2f}")

        if filtro_tipo != "Todos":
            df = df[df["Tipo"] == filtro_tipo]
        if filtro_cat != "Todas":
            df = df[df["Categoria"] == filtro_cat]

        st.dataframe(df, use_container_width=True)
        
        res_col1, res_col2 = st.columns(2)
        res_col1.success(f"📈 Total de Ganhos Filtrados: R$ {df[df['Tipo'] == 'Receita']['Valor (R$)'].sum():.2f}")
        res_col2.warning(f"📉 Total de Gastos Filtrados: R$ {df[df['Tipo'] == 'Despesa']['Valor (R$)'].sum():.2f}")
        
    else:
        st.info("Nenhum registro encontrado. Vá até a aba 'Conversa com o Agente' e registre sua primeira movimentação!")