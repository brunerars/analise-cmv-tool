import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos utils
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.utils.data_processing import load_data
from src.utils.analysis import analyze_os, get_os_details, export_ficha_tecnica

# Caminho do arquivo de dados
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

# Configuracao da pagina
st.set_page_config(
    page_title="Dashboard CMV - ARV Systems",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cached_load_data():
    """Wrapper com cache do Streamlit para load_data"""
    return load_data(str(DATA_PATH))


@st.cache_data
def cached_analyze_os(df):
    """Wrapper com cache do Streamlit para analyze_os"""
    return analyze_os(df)


# ========== MAIN APP ==========

st.title("📊 Dashboard CMV - Análise por OS")
st.markdown("### Mapeamento de custos para catalogação de soluções B2B | ARV Systems")

# Carregar dados
try:
    df = cached_load_data()
    os_summary = cached_analyze_os(df)

    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Valor Total",
            f"R$ {df['ValorTotalComprado'].sum() / 1_000_000:.2f}M",
            delta=f"{len(df):,} itens"
        )

    with col2:
        st.metric(
            "🏭 Total de OSs",
            f"{os_summary['Numero_servico'].nunique():,}",
            delta="Projetos únicos"
        )

    with col3:
        st.metric(
            "📈 Ticket Médio/OS",
            f"R$ {os_summary['ValorTotal'].mean() / 1_000:.1f}k",
            delta="Por projeto"
        )

    with col4:
        st.metric(
            "📦 Famílias",
            f"{df['FAMILIA'].nunique()}",
            delta="Categorias"
        )

    st.markdown("---")

    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")

    # Filtro por família
    familias_disponiveis = ['TODAS'] + sorted(df['FAMILIA'].dropna().unique().tolist())
    familia_filter = st.sidebar.selectbox("Filtrar por Família", familias_disponiveis)

    # Filtro de busca
    search_term = st.sidebar.text_input("Buscar OS", "")

    # Ordenação
    sort_by = st.sidebar.selectbox(
        "Ordenar por",
        ["Maior Valor", "Mais Itens", "Código OS"]
    )

    # Aplicar filtros
    filtered_os = os_summary.copy()

    if search_term:
        filtered_os = filtered_os[
            filtered_os['Numero_servico'].str.contains(search_term, case=False, na=False) |
            filtered_os['NumeroServico'].astype(str).str.contains(search_term, na=False)
        ]

    if familia_filter != 'TODAS':
        os_com_familia = df[df['FAMILIA'] == familia_filter]['Numero_servico'].unique()
        filtered_os = filtered_os[filtered_os['Numero_servico'].isin(os_com_familia)]

    if sort_by == "Mais Itens":
        filtered_os = filtered_os.sort_values('TotalItens', ascending=False)
    elif sort_by == "Código OS":
        filtered_os = filtered_os.sort_values('Numero_servico')

    # Top 10 OSs
    st.header(f"🏆 Top OSs ({len(filtered_os)} projetos)")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Gráfico de barras horizontal
        fig_top = px.bar(
            filtered_os.head(15),
            x='ValorTotal',
            y='Numero_servico',
            orientation='h',
            title='Top 15 OSs por Valor',
            labels={'ValorTotal': 'Valor Total (R$)', 'Numero_servico': 'OS'},
            color='ValorTotal',
            color_continuous_scale='Purples'
        )
        fig_top.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        # Métricas das top 5
        st.subheader("Top 5 OSs")
        for i, row in filtered_os.head(5).iterrows():
            with st.expander(f"**{row['Numero_servico']}** - R$ {row['ValorTotal']/1000:.1f}k"):
                st.write(f"**Itens:** {row['TotalItens']}")
                st.write(f"**Fornecedores:** {row['NumFornecedores']}")
                st.write(f"**Família Principal:** {row['FamiliaPrincipal']}")

    st.markdown("---")

    # Análise por Família
    st.header("📦 Distribuição por Família")

    familia_totals = df.groupby('FAMILIA')['ValorTotalComprado'].sum().sort_values(ascending=False).head(10)

    col1, col2 = st.columns(2)

    with col1:
        fig_familia_pie = px.pie(
            values=familia_totals.values,
            names=familia_totals.index,
            title='Top 10 Famílias - Distribuição de Valor',
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        st.plotly_chart(fig_familia_pie, use_container_width=True)

    with col2:
        fig_familia_bar = px.bar(
            x=familia_totals.values,
            y=familia_totals.index,
            orientation='h',
            title='Top 10 Famílias - Valor Total',
            labels={'x': 'Valor Total (R$)', 'y': 'Família'},
            color=familia_totals.values,
            color_continuous_scale='Purples'
        )
        fig_familia_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_familia_bar, use_container_width=True)

    st.markdown("---")

    # Detalhes de OS específica
    st.header("🔬 Análise Detalhada de OS")

    selected_os = st.selectbox(
        "Selecione uma OS para análise detalhada",
        options=['Selecione...'] + filtered_os['Numero_servico'].tolist()
    )

    if selected_os != 'Selecione...':
        os_details = get_os_details(df, selected_os)

        # Resumo da OS
        st.subheader(f"📋 OS {selected_os}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Valor Total",
                f"R$ {os_details['data']['ValorTotalComprado'].sum():,.2f}"
            )

        with col2:
            st.metric(
                "Total de Itens",
                f"{len(os_details['data'])}"
            )

        with col3:
            st.metric(
                "Fornecedores",
                f"{os_details['data']['Fornecedor'].nunique()}"
            )

        # Gráficos da OS
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuição por Família")
            fig_os_familia = px.pie(
                values=os_details['familia_analysis'].values,
                names=os_details['familia_analysis'].index,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            st.plotly_chart(fig_os_familia, use_container_width=True)

        with col2:
            st.subheader("Top 10 Itens Mais Caros")
            fig_os_top = px.bar(
                os_details['top_itens'],
                x='ValorTotalComprado',
                y='Item',
                orientation='h',
                color='FAMILIA',
                labels={'ValorTotalComprado': 'Valor (R$)'}
            )
            st.plotly_chart(fig_os_top, use_container_width=True)

        # Tabela de itens
        st.subheader("Lista Completa de Itens")
        st.dataframe(
            os_details['data'][['Item', 'FAMILIA', 'GRUPO', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']]
            .sort_values('ValorTotalComprado', ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
            height=400
        )

        # Botão de exportar
        ficha_content = export_ficha_tecnica(os_details, selected_os)
        st.download_button(
            label="📥 Baixar Ficha Técnica",
            data=ficha_content,
            file_name=f"Ficha_Tecnica_OS_{selected_os.replace('/', '_')}.txt",
            mime="text/plain"
        )

    # Tabela geral de OSs
    st.markdown("---")
    st.header("📊 Tabela Geral de OSs")

    st.dataframe(
        filtered_os.style.format({
            'ValorTotal': 'R$ {:,.2f}',
            'TotalItens': '{:,}',
            'NumFornecedores': '{:,}'
        }),
        use_container_width=True,
        height=400
    )

except FileNotFoundError:
    st.error(f"Arquivo '{DATA_PATH}' não encontrado!")
    st.info("Verifique se o arquivo cmv_data.csv está em data/processed/")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
