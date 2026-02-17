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
    page_title="CMV Hub | ARV Systems",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Sistema de Análise de CMV | ARV Systems - Automação Industrial"
    }
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

st.title("📊 CMV Hub")
st.markdown("**Sistema de Análise de Custos para Orçamentistas** | ARV Systems")
st.caption("Consulte, categorize e exporte dados de projetos anteriores para acelerar novos orçamentos")

try:
    df = carregar_dados()
    os_summary = carregar_resumo_os(df)
    os_categorizadas = listar_categorizadas()

    # Métricas principais
    st.markdown("---")
    st.subheader("📈 Resumo Geral")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de OSs", 
            f"{len(os_summary):,}".replace(",", "."),
            help="Número total de Ordens de Serviço (projetos) na base de dados"
        )

    with col2:
        st.metric(
            "OSs Categorizadas", 
            f"{len(os_categorizadas):,}".replace(",", "."),
            help="Projetos já categorizados por tipo de solução e complexidade"
        )

    with col3:
        valor_total = df['ValorTotalComprado'].sum()
        st.metric(
            "Valor Total", 
            f"R$ {valor_total/1_000_000:.1f}M".replace(".", ","),
            help="Valor total de todas as compras registradas"
        )
    
    with col4:
        percentual_cat = (len(os_categorizadas) / len(os_summary) * 100) if len(os_summary) > 0 else 0
        st.metric(
            "Progresso", 
            f"{percentual_cat:.1f}%".replace(".", ","),
            help="Percentual de OSs categorizadas em relação ao total"
        )

    # Cards de navegação
    st.markdown("---")
    st.subheader("🎯 Funcionalidades Principais")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>📊 Consultar e Categorizar OS</h3>
            <p><strong>Para Orçamentistas:</strong> Busque projetos similares, analise composição de custos por família de produtos, filtre por fornecedores e categorize soluções.</p>
            <p style="margin-top: 10px; color: #cc0000;"><strong>• Filtros avançados</strong><br/>
            <strong>• Exportação Excel</strong><br/>
            <strong>• Análise detalhada</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Categorizacao.py", label="📊 Abrir Categorização", icon="📊", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>📁 Catálogo de Máquinas</h3>
            <p><strong>Para Gestão:</strong> Acesse o catálogo de projetos categorizados, compare soluções similares, visualize fotos das máquinas e exporte relatórios consolidados.</p>
            <p style="margin-top: 10px; color: #cc0000;"><strong>• Galeria visual</strong><br/>
            <strong>• Filtros por área</strong><br/>
            <strong>• Comparação de projetos</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Catalogo.py", label="📁 Abrir Catálogo", icon="📁", use_container_width=True)
    
    # Informações adicionais
    st.markdown("---")
    with st.expander("ℹ️ Como usar o sistema", expanded=False):
        st.markdown("""
        ### Fluxo de trabalho recomendado:
        
        1. **Consultar OS**: Explore projetos passados, use filtros para encontrar soluções similares ao seu novo orçamento
        2. **Categorizar**: Ao encontrar uma OS relevante, categorize-a por área de atuação e complexidade
        3. **Catálogo**: Acesse o catálogo para visualizar todas as máquinas categorizadas e fazer comparações
        4. **Exportar**: Gere relatórios Excel para usar como referência no seu orçamento
        
        ### Dicas:
        - Use os filtros por **Família** para encontrar componentes específicos (ex: Pneumática, Sensores)
        - A **Ordem de Compra (OC)** agrupa itens comprados juntos
        - Exporte relatórios **Filtrados** para criar listas específicas de componentes
        """)
    
    st.markdown("---")
    st.caption("💡 **Dica**: Categorizar projetos anteriores acelera orçamentos futuros em até 50%")

    # Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Informações")
    st.sidebar.info(f"""
    **Base de Dados:**
    - {len(df):,} itens registrados
    - {len(os_summary):,} projetos únicos
    - R$ {df['ValorTotalComprado'].sum()/1_000_000:.1f}M em valor total
    """.replace(",", "."))
    
    st.sidebar.markdown("---")
    st.sidebar.caption("**CMV Hub v2.0**")
    st.sidebar.caption("ARV Systems - Automação Industrial")
    st.sidebar.caption("© 2026 Todos os direitos reservados")

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
    st.info("Verifique se o arquivo cmv_data.csv está em data/processed/")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
