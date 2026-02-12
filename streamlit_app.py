"""Interface Streamlit para o Banco Ágil."""
import streamlit as st
from src.graph.graph import build_graph
from langchain_core.messages import HumanMessage
import uuid

st.set_page_config(
    page_title="Banco Ágil",
    page_icon="🏦",
    layout="centered"
)

# ==========================
# CSS GLOBAL
# ==========================
st.markdown("""
<style>

/* ===== HEADER ===== */
.header-banco-agil {
    background: linear-gradient(90deg, #2563eb 0%, #1e40af 100%);
    border-radius: 16px;
    margin: 2rem 0 2.5rem 0;
    padding: 2.2rem 0.5rem 1.2rem 0.5rem;
    box-shadow: 0 2px 12px #0001;
    text-align: center;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}
            


.header-banco-agil h1 {
    color: #fff;
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.header-banco-agil .subtitle {
    color: #e0e7ef;
    font-size: 1rem;
}

/* ===== SIDEBAR FUNDO ===== */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #2563eb 0%, #1e3a8a 100%);
    border-radius: 24px;
    margin: 12px;
    padding: 1.5rem 1rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

/* Remove borda padrão */
section[data-testid="stSidebar"] {
    border-right: none !important;
}

/* Texto branco */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ===== Cards internos ===== */
.sidebar-card {
    background: rgba(255,255,255,0.08);
    padding: 1rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    backdrop-filter: blur(6px);
}

/* Botão customizado */
div.stButton > button {
    background: rgba(255,255,255,0.15);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

div.stButton > button:hover {
    background: rgba(255,255,255,0.25);
}

/* Linha divisória */
hr {
    border: 0.5px solid rgba(255,255,255,0.2);
}
            


</style>
""", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================
st.markdown("""
<div class='header-banco-agil'>
    <h1>🏦 Banco Ágil - Sistema Multi-Agente</h1>
    <div class='subtitle'>Seu banco digital inteligente</div>
</div>
""", unsafe_allow_html=True)

# ==========================
# SESSION STATE
# ==========================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.graph = build_graph()
    st.session_state.current_state = None

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# ==========================
# CHAT HISTÓRICO
# ==========================
for message in st.session_state.messages:
    role = message["role"]
    avatar = "👨‍💼" if role == "user" else "🏦"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# ==========================
# INPUT DO USUÁRIO
# ==========================
if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👨‍💼"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🏦"):
        message_placeholder = st.empty()

        try:
            if st.session_state.current_state is None:
                st.session_state.current_state = {
                    "messages": [HumanMessage(content=prompt)],
                    "is_authenticated": False,
                    "current_agent": "supervisor",
                    "supervisor_reasoning": "",
                    "client_cpf": "",
                    "client_name": "",
                    "auth_attempts": 0
                }
            else:
                st.session_state.current_state["messages"].append(
                    HumanMessage(content=prompt)
                )

            st.session_state.current_state = st.session_state.graph.invoke(
                st.session_state.current_state,
                config=config
            )

            if st.session_state.current_state["messages"]:
                response = st.session_state.current_state["messages"][-1].content
                message_placeholder.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

        except Exception as e:
            error_msg = f"❌ Erro: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )

# ==========================
# SIDEBAR PREMIUM
# ==========================



with st.sidebar:

    st.markdown("""
    <div style='font-size:1.5rem;font-weight:700;color:#fff;margin-top:0.5rem;margin-bottom:0.5rem;text-align:center;letter-spacing:1px;'>
        Banco Ágil
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-card' style='display: flex; flex-direction: column; align-items: flex-start;'>", unsafe_allow_html=True)
    
    if st.button(" Nova Conversa"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.current_state = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Card Status
    st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    if st.session_state.current_state and st.session_state.current_state.get("is_authenticated"):
        st.success("Autenticado")
        st.write(f"Nome: {st.session_state.current_state.get('client_name','')}")
    else:
        st.warning("Não autenticado")
    st.markdown("</div>", unsafe_allow_html=True)

    # Card Nova Conversa

    # Card Serviços
    st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    st.markdown("### Serviços Disponíveis")
    st.markdown("""
• 💳 Crédito  
• 📋 Entrevista  
• 💱 Câmbio  
""")
    st.markdown("</div>", unsafe_allow_html=True)
