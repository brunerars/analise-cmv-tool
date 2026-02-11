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
    init_db, listar_categorizadas, get_categoria,
    contar_por_area, contar_por_complexidade,
    remover_categoria, AREAS_ATUACAO, COMPLEXIDADES
)
from src.utils.export import export_excel_resumo, export_excel_detalhado, export_excel_comparativo

# Caminho dos dados
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

# Inicializar banco
init_db()

st.title("Catálogo de Máquinas")
st.markdown("Visualize e compare OSs categorizadas")

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

    # Sidebar com filtros
    st.sidebar.header("Filtros")

    # Filtro por área
    areas = ['Todas'] + AREAS_ATUACAO
    filtro_area = st.sidebar.selectbox("Área de Atuação", areas)

    # Filtro por complexidade
    complexidades = ['Todas'] + COMPLEXIDADES
    filtro_complexidade = st.sidebar.selectbox("Complexidade", complexidades)

    # Buscar OSs categorizadas
    area_param = filtro_area if filtro_area != 'Todas' else None
    complexidade_param = filtro_complexidade if filtro_complexidade != 'Todas' else None

    os_categorizadas = listar_categorizadas(area_param, complexidade_param)

    # Estatísticas no sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Estatísticas")

    contagem_area = contar_por_area()
    contagem_complexidade = contar_por_complexidade()

    st.sidebar.metric("Total Categorizadas", len(os_categorizadas))

    if contagem_area:
        st.sidebar.markdown("**Por Área:**")
        for area, count in contagem_area.items():
            st.sidebar.caption(f"• {area[:20]}...: {count}")

    # Inicializar estado de seleção
    if 'os_selecionadas' not in st.session_state:
        st.session_state.os_selecionadas = []

    # Conteúdo principal
    if not os_categorizadas:
        st.info("Nenhuma OS categorizada ainda. Vá para 'Consultar OS' para categorizar.")

        # Mostrar preview das OSs disponíveis
        st.markdown("---")
        st.subheader("OSs Disponíveis para Categorização")

        preview_df = os_summary.head(10).copy()
        preview_df['Valor'] = preview_df['ValorTotal'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        st.dataframe(
            preview_df[['Numero_servico', 'Valor', 'TotalItens', 'FamiliaPrincipal']],
            use_container_width=True
        )

    else:
        # Mostrar cards
        st.markdown(f"### {len(os_categorizadas)} máquinas encontradas")

        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Selecionar Todas"):
                st.session_state.os_selecionadas = [os['numero_servico'] for os in os_categorizadas]
                st.rerun()
        with col2:
            if st.button("Limpar Seleção"):
                st.session_state.os_selecionadas = []
                st.rerun()

        st.markdown("---")

        # Grid de cards (3 colunas)
        cols = st.columns(3)

        for idx, os_cat in enumerate(os_categorizadas):
            col = cols[idx % 3]

            # Buscar dados de valor da OS (converter para int para comparação)
            try:
                os_num_int = int(os_cat['numero_servico'])
            except (ValueError, TypeError):
                os_num_int = os_cat['numero_servico']
            os_row = os_summary[os_summary['Numero_servico'] == os_num_int]
            valor_total = os_row['ValorTotal'].values[0] if len(os_row) > 0 else 0
            total_itens = os_row['TotalItens'].values[0] if len(os_row) > 0 else 0

            # Determinar ícone de complexidade
            complexidade_icons = {
                'Pequena': '●○○',
                'Média': '●●○',
                'Grande': '●●●'
            }
            icon = complexidade_icons.get(os_cat['complexidade'], '○○○')

            # Verificar se está selecionada
            is_selected = os_cat['numero_servico'] in st.session_state.os_selecionadas

            with col:
                # Card com container
                with st.container():
                    # Estilo do card - Cores ARV (preto, vermelho, branco)
                    card_style = "border: 2px solid #cc0000; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: #1a1a1a;"
                    if is_selected:
                        card_style = "border: 3px solid #00cc00; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: #1a2a1a;"

                    st.markdown(f"""
                    <div style="{card_style}">
                        <h4 style="margin: 0; color: #ffffff;">OS {os_cat['numero_servico']}</h4>
                        <p style="margin: 5px 0; font-size: 0.9em; color: #cccccc;">{os_cat['area_atuacao']}</p>
                        <p style="margin: 5px 0; color: #cc0000;"><strong>{icon}</strong> {os_cat['complexidade']}</p>
                        <p style="margin: 5px 0; font-size: 1.2em; font-weight: bold; color: #ffffff;">R$ {valor_total:,.0f}</p>
                        <p style="margin: 0; font-size: 0.8em; color: #888888;">{total_itens} itens</p>
                    </div>
                    """.replace(",", "."), unsafe_allow_html=True)

                    # Botões
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("Ver", key=f"ver_{os_cat['numero_servico']}", use_container_width=True):
                            st.session_state.os_detalhada = os_cat['numero_servico']

                    with btn_col2:
                        checkbox_label = "✓" if is_selected else "☐"
                        if st.button(checkbox_label, key=f"sel_{os_cat['numero_servico']}", use_container_width=True):
                            if is_selected:
                                st.session_state.os_selecionadas.remove(os_cat['numero_servico'])
                            else:
                                st.session_state.os_selecionadas.append(os_cat['numero_servico'])
                            st.rerun()

                    with btn_col3:
                        if st.button("🗑", key=f"del_{os_cat['numero_servico']}", use_container_width=True):
                            if remover_categoria(os_cat['numero_servico']):
                                # Remover da lista de selecionadas se estiver lá
                                if os_cat['numero_servico'] in st.session_state.os_selecionadas:
                                    st.session_state.os_selecionadas.remove(os_cat['numero_servico'])
                                st.rerun()

        # Seção de comparação (se houver selecionadas)
        if st.session_state.os_selecionadas:
            st.markdown("---")
            st.subheader(f"Comparação ({len(st.session_state.os_selecionadas)} selecionadas)")

            # Preparar dados para comparação
            dados_comparacao = {}
            for os_num in st.session_state.os_selecionadas:
                os_details = get_os_details(df, os_num)
                dados_comparacao[os_num] = os_details

            # Tabela comparativa de totais
            comparativo = []
            for os_num in st.session_state.os_selecionadas:
                os_data = dados_comparacao[os_num]['data']
                categoria = get_categoria(os_num)
                comparativo.append({
                    'OS': os_num,
                    'Área': categoria['area_atuacao'] if categoria else '-',
                    'Complexidade': categoria['complexidade'] if categoria else '-',
                    'Valor Total': os_data['ValorTotalComprado'].sum(),
                    'Itens': len(os_data),
                    'Fornecedores': os_data['Fornecedor'].nunique()
                })

            df_comp = pd.DataFrame(comparativo)
            df_comp['Valor Total'] = df_comp['Valor Total'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            st.dataframe(df_comp, use_container_width=True)

            # Gráfico comparativo por família
            st.markdown("#### Comparativo por Família")

            # Coletar todas as famílias
            all_data = []
            for os_num in st.session_state.os_selecionadas:
                for familia, valor in dados_comparacao[os_num]['familia_analysis'].items():
                    all_data.append({
                        'OS': os_num,
                        'Família': familia,
                        'Valor': valor
                    })

            df_familias = pd.DataFrame(all_data)

            if not df_familias.empty:
                fig = px.bar(
                    df_familias,
                    x='Família',
                    y='Valor',
                    color='OS',
                    barmode='group',
                    title='Custo por Família - Comparativo'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            # Exportar comparativo
            st.markdown("#### Exportar Comparativo")
            excel_comp = export_excel_comparativo(st.session_state.os_selecionadas, dados_comparacao)
            st.download_button(
                label="Exportar Comparativo (Excel)",
                data=excel_comp,
                file_name=f"CMV_Comparativo_{len(st.session_state.os_selecionadas)}_OSs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Modal de detalhes (se uma OS foi selecionada para ver)
        if 'os_detalhada' in st.session_state and st.session_state.os_detalhada:
            st.markdown("---")
            st.subheader(f"Detalhes - OS {st.session_state.os_detalhada}")

            os_details = get_os_details(df, st.session_state.os_detalhada)
            os_data = os_details['data']
            categoria = get_categoria(st.session_state.os_detalhada)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Valor Total", f"R$ {os_data['ValorTotalComprado'].sum():,.0f}".replace(",", "."))
            with col2:
                st.metric("Itens", len(os_data))
            with col3:
                st.metric("Área", categoria['area_atuacao'][:15] + "..." if categoria else "-")
            with col4:
                st.metric("Complexidade", categoria['complexidade'] if categoria else "-")

            # Gráfico de família
            familia_df = os_details['familia_analysis'].reset_index()
            familia_df.columns = ['Família', 'Valor']

            fig = px.pie(
                familia_df,
                names='Família',
                values='Valor',
                title='Distribuição por Família'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Botões de ação
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Fechar Detalhes", use_container_width=True):
                    del st.session_state.os_detalhada
                    st.rerun()
            with col2:
                if st.button("Excluir do Catálogo", type="primary", use_container_width=True):
                    if remover_categoria(st.session_state.os_detalhada):
                        if st.session_state.os_detalhada in st.session_state.os_selecionadas:
                            st.session_state.os_selecionadas.remove(st.session_state.os_detalhada)
                        del st.session_state.os_detalhada
                        st.rerun()

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
