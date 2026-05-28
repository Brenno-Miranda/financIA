import os
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb

from database import registrar_transacao, consultar_balanco_geral

load_dotenv()

def get_agent(session_id: str) -> Agent:
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    return Agent(
        model=Gemini(id="gemini-2.5-flash"),
        session_id=session_id,
        db=SqliteDb(db_file="memoria_chat.db"),
        add_history_to_context=True,
        tools=[registrar_transacao, consultar_balanco_geral],
        description="Você é um assistente financeiro inteligente focado em controle de fluxo de caixa.",
        instructions=[
            f"Hoje é dia {data_hoje}.",
            f"IMPORTANTE: O ID do usuário com quem você conversa é: {session_id}.",
            "Monitore o contexto da frase do usuário para discernir a natureza da transação:",
            "  - Se ele perdeu/gastou/pagou algo, use 'registrar_transacao' com tipo='despesa'.",
            "  - Se ele ganhou/recebeu/faturou/recebeu um PIX, use 'registrar_transacao' com tipo='receita'.",
            "Se o usuário perguntar por saldo, extrato, balanço ou relatórios, acione a ferramenta 'consultar_balanco_geral'.",
            "Responda de forma humanizada, natural e muito direta."
        ]
    )