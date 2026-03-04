import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.utils.database import init_db, salvar_ano_oc, get_todos_anos_oc, remover_ano_oc
from src.utils.data_processing import load_data

init_db()

st.set_page_config(
    page_title="Anos OC | CMV Hub",
    page_icon="📅",
    layout="wide",
)

st.markdown("""
<style>
    .card {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 25px;
        border-left: 4px solid #cc0000;
        margin-bottom: 15px;
    }
    .card h3 { color: #ffffff !important; margin: 0 0 10px 0; }
    .card p  { color: #cccccc !important; margin: 0; }
</style>
""", unsafe_allow_html=True)

st.title("📅 Anos OC")
st.markdown("Associe um **ano** a cada número de Ordem de Compra.")
st.markdown("---")

# Carregar lista de OCs disponíveis no CSV
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

@st.cache_data
def carregar_ocs():
    df = load_data(str(DATA_PATH))
    return sorted(df['OrdemCompra'].dropna().astype(int).unique().tolist())

try:
    ocs_disponiveis = carregar_ocs()
except Exception:
    ocs_disponiveis = []

dados = get_todos_anos_oc()

# ── Bloco 1: Adicionar / Editar ──────────────────────────────────────────────
st.subheader("Adicionar / Editar")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    if ocs_disponiveis:
        numero_oc = st.selectbox(
            "Número da OC",
            options=ocs_disponiveis,
            format_func=lambda x: str(x),
            key="input_numero_oc",
        )
    else:
        numero_oc = st.number_input(
            "Número da OC",
            min_value=1,
            step=1,
            format="%d",
            key="input_numero_oc",
        )

with col2:
    ano = st.number_input(
        "Ano",
        min_value=1900,
        max_value=2100,
        value=2024,
        step=1,
        format="%d",
        key="input_ano",
    )

with col3:
    st.write("")  # alinhamento vertical
    st.write("")
    salvar = st.button("💾 Salvar", use_container_width=True)

if salvar:
    try:
        salvar_ano_oc(int(numero_oc), int(ano))
        st.success(f"OC {int(numero_oc)} → Ano {int(ano)} salvo com sucesso.")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

st.markdown("---")

# ── Bloco 2: Tabela de OCs cadastradas ───────────────────────────────────────
st.subheader("OCs Cadastradas")

if dados:
    df = pd.DataFrame(
        [{"OC": oc, "Ano": ano} for oc, ano in dados.items()]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma OC cadastrada ainda.")

st.markdown("---")

# ── Bloco 3: Remover ─────────────────────────────────────────────────────────
st.subheader("Remover OC")

if dados:
    col_rm1, col_rm2 = st.columns([3, 1])

    with col_rm1:
        oc_remover = st.selectbox(
            "Número da OC para remover",
            options=sorted(dados.keys()),
            format_func=lambda x: str(x),
            key="input_oc_remover",
        )

    with col_rm2:
        st.write("")
        st.write("")
        remover = st.button("🗑️ Remover", use_container_width=True)

    if remover:
        if remover_ano_oc(int(oc_remover)):
            st.success(f"OC {int(oc_remover)} removida.")
            st.rerun()
        else:
            st.warning(f"OC {int(oc_remover)} não encontrada.")
else:
    st.info("Nenhuma OC cadastrada para remover.")

st.sidebar.caption("CMV Hub v2.0 | ARV Systems")
