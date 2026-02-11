import sys
from pathlib import Path

# Adiciona o diretório raiz ao path (pages está em src/backend/pages/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.utils.data_processing import load_data
from src.utils.analysis import analyze_os, get_os_details
from src.utils.database import (
    init_db, categorizar_os, get_categoria,
    AREAS_ATUACAO, COMPLEXIDADES
)
from src.utils.export import export_excel_resumo, export_excel_detalhado

# Caminho dos dados
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

# Inicializar banco
init_db()

st.title("Consultar OS")
st.markdown("Selecione uma OS para visualizar custos detalhados")

# Carregar dados
@st.cache_data
def carregar_dados():
    return load_data(str(DATA_PATH))

@st.cache_data
def carregar_resumo_os(df):
    return analyze_os(df)

try:
    df = carregar_dados()
    os_summary = carregar_resumo_os(df)

    # Dropdown de OSs
    lista_os = os_summary['Numero_servico'].tolist()

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_os = st.selectbox(
            "Selecione a OS",
            options=lista_os,
            format_func=lambda x: f"OS {x} - R$ {os_summary[os_summary['Numero_servico']==x]['ValorTotal'].values[0]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    # Verificar se já está categorizada
    categoria_atual = get_categoria(str(selected_os)) if selected_os else None

    with col2:
        if categoria_atual:
            st.success(f"{categoria_atual['area_atuacao'][:15]}... | {categoria_atual['complexidade']}")
        else:
            st.warning("Não categorizada")

    if selected_os:
        os_details = get_os_details(df, selected_os)
        os_data = os_details['data']
        valor_total = os_data['ValorTotalComprado'].sum()

        # Métricas
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col2:
            st.metric("Total de Itens", f"{len(os_data):,}")
        with col3:
            st.metric("Fornecedores", f"{os_data['Fornecedor'].nunique()}")
        with col4:
            st.metric("Famílias", f"{os_data['FAMILIA'].nunique()}")

        # Gráfico de barras por família
        st.markdown("---")
        st.subheader("Custo por Família")

        familia_df = os_details['familia_analysis'].reset_index()
        familia_df.columns = ['Família', 'Valor']
        familia_df['Percentual'] = (familia_df['Valor'] / valor_total * 100).round(1)
        familia_df = familia_df.sort_values('Valor', ascending=True)

        fig = px.bar(
            familia_df,
            x='Valor',
            y='Família',
            orientation='h',
            text=familia_df.apply(lambda x: f"R$ {x['Valor']:,.0f} ({x['Percentual']}%)".replace(",", "."), axis=1),
            color='Valor',
            color_continuous_scale='Reds'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=max(400, len(familia_df) * 35),
            showlegend=False,
            xaxis_title="Valor (R$)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabela filtrável
        st.markdown("---")
        st.subheader("Detalhamento de Itens")

        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            familias = ['Todas'] + sorted(os_data['FAMILIA'].dropna().unique().tolist())
            filtro_familia = st.selectbox("Filtrar por Família", familias, key="filtro_familia")

        with col2:
            if filtro_familia != 'Todas':
                grupos = ['Todos'] + sorted(os_data[os_data['FAMILIA'] == filtro_familia]['GRUPO'].dropna().unique().tolist())
            else:
                grupos = ['Todos'] + sorted(os_data['GRUPO'].dropna().unique().tolist())
            filtro_grupo = st.selectbox("Filtrar por Grupo", grupos, key="filtro_grupo")

        with col3:
            fornecedores = ['Todos'] + sorted(os_data['Fornecedor'].dropna().unique().tolist())
            filtro_fornecedor = st.selectbox("Filtrar por Fornecedor", fornecedores, key="filtro_fornecedor")

        # Aplicar filtros
        df_filtrado = os_data.copy()

        if filtro_familia != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['FAMILIA'] == filtro_familia]

        if filtro_grupo != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['GRUPO'] == filtro_grupo]

        if filtro_fornecedor != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == filtro_fornecedor]

        # Exibir tabela
        df_display = df_filtrado[['Item', 'FAMILIA', 'GRUPO', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']].copy()
        df_display.columns = ['Item', 'Família', 'Grupo', 'Fornecedor', 'Qtd', 'Valor']
        df_display = df_display.sort_values('Valor', ascending=False)

        # Formatar valores
        df_display['Valor'] = df_display['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )

        # Total filtrado
        total_filtrado = df_filtrado['ValorTotalComprado'].sum()
        st.info(f"**Total filtrado:** R$ {total_filtrado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({len(df_filtrado)} itens)")

        # Seção de categorização
        st.markdown("---")
        with st.expander("Categorizar esta OS", expanded=not categoria_atual):
            col1, col2 = st.columns(2)

            with col1:
                area_selecionada = st.selectbox(
                    "Área de Atuação",
                    options=AREAS_ATUACAO,
                    index=AREAS_ATUACAO.index(categoria_atual['area_atuacao']) if categoria_atual else 0
                )

            with col2:
                complexidade_selecionada = st.selectbox(
                    "Complexidade",
                    options=COMPLEXIDADES,
                    index=COMPLEXIDADES.index(categoria_atual['complexidade']) if categoria_atual else 1
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Salvar Categorização", type="primary", use_container_width=True):
                    if categorizar_os(str(selected_os), area_selecionada, complexidade_selecionada):
                        st.success("Categorização salva com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar categorização")

            with col2:
                if categoria_atual:
                    st.caption(f"Última atualização: {categoria_atual.get('data_categorizacao', '-')}")

        # Exportar
        st.markdown("---")
        st.subheader("Exportar Dados")

        col1, col2 = st.columns(2)

        with col1:
            excel_resumo = export_excel_resumo(os_details, selected_os, categoria_atual)
            st.download_button(
                label="Exportar Resumo (Excel)",
                data=excel_resumo,
                file_name=f"CMV_Resumo_OS_{str(selected_os).replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            excel_detalhado = export_excel_detalhado(os_details, selected_os, categoria_atual)
            st.download_button(
                label="Exportar Detalhado (Excel)",
                data=excel_detalhado,
                file_name=f"CMV_Detalhado_OS_{str(selected_os).replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
