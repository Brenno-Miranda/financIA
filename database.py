import sqlite3

DB_NAME = "gastos.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Criamos a tabela de transações genérica (fluxo de caixa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'receita' para entradas, 'despesa' para saídas
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ---- FERRAMENTAS QUE O AGENTE IA VAI USAR ----

def registrar_transacao(usuario_id: str, descricao: str, valor: float, categoria: str, tipo: str, data: str) -> str:
    """Usa esta ferramenta para salvar uma movimentação financeira (ganho ou gasto).
    Args:
        usuario_id: O ID do usuário recebido no contexto.
        descricao: Descrição do que aconteceu.
        valor: Valor numérico positivo.
        categoria: Ex: Salário, Investimentos, Alimentação, Transporte, Lazer, Outros.
        tipo: Deve ser EXATAMENTE 'receita' (ganhos) ou 'despesa' (gastos).
        data: Data no formato YYYY-MM-DD.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacoes (usuario_id, descricao, valor, categoria, tipo, data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (usuario_id, descricao, valor, categoria, tipo.lower(), data))
    conn.commit()
    conn.close()
    return f"Sucesso! {tipo.capitalize()} de R$ {valor} em '{categoria}' foi registrada."

def consultar_balanco_geral(usuario_id: str) -> str:
    """Usa esta ferramenta para calcular o saldo atual (Receitas - Despesas) e o resumo do balanço."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario_id = ? AND tipo = 'receita'", (usuario_id,))
    receitas = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario_id = ? AND tipo = 'despesa'", (usuario_id,))
    despesas = cursor.fetchone()[0] or 0.0
    
    saldo = receitas - despesas
    conn.close()
    
    return f"Balanço Geral:\nTotal de Entradas: R$ {receitas:.2f}\nTotal de Saídas: R$ {despesas:.2f}\nSaldo Atual: R$ {saldo:.2f}"


# ---- FUNÇÃO AUXILIAR PARA O DASHBOARD DO STREAMLIT ----

def listar_transacoes(usuario_id: str):
    """Busca todas as transações cadastradas do usuário para renderizar no DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tipo, descricao, valor, categoria, data 
        FROM transacoes 
        WHERE usuario_id = ? 
        ORDER BY id DESC
    ''', (usuario_id,))
    linhas = cursor.fetchall()
    conn.close()
    
    return [{"Tipo": l[0].capitalize(), "Descrição": l[1], "Valor (R$)": l[2], "Categoria": l[3], "Data": l[4]} for l in linhas]