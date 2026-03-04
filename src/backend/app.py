import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.utils.data_processing import load_data
from src.utils.analysis import analyze_os
from src.utils.database import init_db, listar_categorizadas

# Caminho dos dados
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

# Inicializar banco de dados
init_db()

# Configuracao da pagina
st.set_page_config(
    page_title="CMV Hub - ARV Systems",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - Cores ARV (preto, vermelho, branco)
st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .card {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 25px;
        border-left: 4px solid #cc0000;
        margin-bottom: 15px;
    }
    .card h3 {
        color: #ffffff !important;
        margin: 0 0 10px 0;
    }
    .card p {
        color: #cccccc !important;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def carregar_dados():
    return load_data(str(DATA_PATH))

@st.cache_data
def carregar_resumo_os(df):
    return analyze_os(df)

# ========== PÁGINA INICIAL ==========

st.title("CMV Hub")
st.markdown("**Sistema de Consulta de Custos** | ARV Systems")

try:
    df = carregar_dados()
    os_summary = carregar_resumo_os(df)
    os_categorizadas = listar_categorizadas()

    # Métricas principais
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de OSs", f"{len(os_summary)}")

    with col2:
        st.metric("OSs Categorizadas", f"{len(os_categorizadas)}")

    with col3:
        valor_total = df['ValorTotalComprado'].sum()
        st.metric("Valor Total", f"R$ {valor_total/1_000_000:.1f}M".replace(".", ","))

    # Cards de navegação
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>📊 Consultar OS</h3>
            <p>Visualize custos detalhados, filtre por família e fornecedor, e categorize projetos.</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Categorizacao.py", label="Abrir Consulta", icon="📊")

    with col2:
        st.markdown("""
        <div class="card">
            <h3>📁 Catálogo</h3>
            <p>Acesse máquinas categorizadas, compare projetos e exporte relatórios.</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Catalogo.py", label="Abrir Catálogo", icon="📁")

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📅 Anos OC</h3>
            <p>Associe um ano a cada número de Ordem de Compra para rastreabilidade histórica.</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Anos_OC.py", label="Abrir Anos OC", icon="📅")

    # Sidebar
    st.sidebar.caption("CMV Hub v2.0 | ARV Systems")

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
    st.info("Verifique se o arquivo cmv_data.csv está em data/processed/")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
