import sys
from pathlib import Path

# Adiciona o diretório raiz ao path (pages está em src/backend/pages/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.utils.data_processing import load_data, get_data_path
from src.utils.analysis import analyze_os, get_os_details
from src.utils.database import (
    init_db, categorizar_os, get_categoria,
    AREAS_ATUACAO, COMPLEXIDADES, get_todos_anos_oc
)
from src.utils.export import export_excel_resumo, export_excel_detalhado, export_excel_filtrado

# Caminho dos dados (funciona em Docker e localmente)
DATA_PATH = get_data_path() / "processed" / "cmv_data.csv"

st.set_page_config(
    page_title="Categorização | CMV Hub",
    page_icon="📊",
    layout="wide"
)

# Inicializar banco
init_db()

st.title("📊 Categorização de OS")
st.markdown("**Consulte projetos, analise custos e categorize soluções**")
st.caption("Busque OSs similares ao seu novo projeto para usar como referência de orçamento")
@st.cache_data
def carregar_dados():
    return load_data(str(DATA_PATH))

@st.cache_data
def carregar_resumo_os(df):
    return analyze_os(df)

try:
    df = carregar_dados()
    os_summary = carregar_resumo_os(df)
    anos_oc = get_todos_anos_oc()  # dict {numero_oc: ano} — sem cache, sempre fresco

    # ============================================================
    # 1. HEADER: Seletor de OS (com opção "Todos os Projetos")
    # ============================================================
    st.markdown("---")
    st.subheader("🔍 Seleção de Projeto")
    
    lista_os = os_summary['Numero_servico'].tolist()
    opcoes_os = ['Todos os Projetos'] + lista_os

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        selected_os = st.selectbox(
            "Selecione a Ordem de Serviço (OS)",
            options=opcoes_os,
            format_func=lambda x: x if x == 'Todos os Projetos' else f"OS {x} - R$ {os_summary[os_summary['Numero_servico']==x]['ValorTotal'].values[0]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            help="Escolha uma OS específica para análise detalhada ou 'Todos os Projetos' para explorar toda a base"
        )

    # Verificar se é "Todos os Projetos" ou uma OS específica
    is_todos_projetos = selected_os == 'Todos os Projetos'

    # Verificar se já está categorizada (só para OS específica)
    categoria_atual = None
    if not is_todos_projetos:
        categoria_atual = get_categoria(str(selected_os))

    with col2:
        if is_todos_projetos:
            st.info("💡 Modo exploração")
        elif categoria_atual:
            st.success(f"✅ {categoria_atual['area_atuacao'][:18]}...")
        else:
            st.warning("⚠️ Não categorizada")
    
    with col3:
        if not is_todos_projetos and categoria_atual:
            st.metric("Complexidade", categoria_atual['complexidade'])

    # Determinar dados a usar
    if is_todos_projetos:
        os_data = df.copy()
        valor_total = df['ValorTotalComprado'].sum()
    else:
        os_details = get_os_details(df, selected_os)
        os_data = os_details['data']
        valor_total = os_data['ValorTotalComprado'].sum()

    # ============================================================
    # 2. SUBHEADER: Métricas de Resumo
    # ============================================================
    st.markdown("---")
    st.subheader("📈 Resumo Financeiro")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Valor Total", 
            f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            help="Soma de todos os valores de compra dos itens"
        )
    with col2:
        st.metric(
            "Total de Itens", 
            f"{len(os_data):,}".replace(",", "."),
            help="Quantidade de linhas de itens comprados"
        )
    with col3:
        st.metric(
            "Fornecedores", 
            f"{os_data['Fornecedor'].nunique()}",
            help="Número de fornecedores diferentes utilizados"
        )
    with col4:
        st.metric(
            "Famílias", 
            f"{os_data['FAMILIA'].nunique()}",
            help="Número de famílias de produtos diferentes (ex: Pneumática, Sensores)"
        )
    with col5:
        st.metric(
            "Ordens de Compra", 
            f"{os_data['OrdemCompra'].nunique()}",
            help="Número de OCs (Ordens de Compra) utilizadas no projeto"
        )

    # ============================================================
    # 3. FILTROS: Busca de Item + OC + Família + Grupo + Fornecedor
    # ============================================================
    st.markdown("---")
    st.subheader("🔎 Filtros de Busca")
    st.caption("Use os filtros para encontrar componentes específicos ou analisar custos por categoria")

    # Linha 1: Busca de Item
    busca_item = st.text_input(
        "🔍 Buscar por nome do item",
        placeholder="Ex: sensor, válvula, motor, cabo...",
        key="busca_item",
        help="Digite qualquer palavra que apareça no nome do item"
    )

    # Linha 2: Filtros por seleção
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ordens_compra = ['Todas'] + sorted([str(int(x)) for x in os_data['OrdemCompra'].dropna().unique()])
        filtro_oc = st.selectbox(
            "📋 Ordem de Compra (OC)", 
            ordens_compra, 
            key="filtro_oc",
            help="Filtre itens de uma OC específica"
        )

    with col2:
        familias = ['Todas'] + sorted(os_data['FAMILIA'].dropna().unique().tolist())
        filtro_familia = st.selectbox(
            "📦 Família de Produtos", 
            familias, 
            key="filtro_familia",
            help="Ex: Pneumática, Sensores, Material Elétrico"
        )

    with col3:
        if filtro_familia != 'Todas':
            grupos = ['Todos'] + sorted(os_data[os_data['FAMILIA'] == filtro_familia]['GRUPO'].dropna().unique().tolist())
        else:
            grupos = ['Todos'] + sorted(os_data['GRUPO'].dropna().unique().tolist())
        filtro_grupo = st.selectbox(
            "🏷️ Grupo (Subcategoria)", 
            grupos, 
            key="filtro_grupo",
            help="Subcategoria dentro da família selecionada"
        )

    with col4:
        fornecedores = ['Todos'] + sorted(os_data['Fornecedor'].dropna().unique().tolist())
        filtro_fornecedor = st.selectbox(
            "🏭 Fornecedor", 
            fornecedores, 
            key="filtro_fornecedor",
            help="Filtre itens de um fornecedor específico"
        )

    with col5:
        ocs_presentes = set(os_data['OrdemCompra'].dropna().astype(int).unique())
        anos_presentes = sorted({v for k, v in anos_oc.items() if k in ocs_presentes})
        opcoes_ano = ['Todos'] + [str(a) for a in anos_presentes]
        filtro_ano = st.selectbox("Filtrar por Ano", opcoes_ano, key="filtro_ano")

    # Aplicar filtros
    df_filtrado = os_data.copy()

    if busca_item:
        df_filtrado = df_filtrado[df_filtrado['Item'].str.contains(busca_item, case=False, na=False)]

    if filtro_oc != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['OrdemCompra'].astype(str).astype(float).astype(int).astype(str) == filtro_oc]

    if filtro_familia != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['FAMILIA'] == filtro_familia]

    if filtro_grupo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['GRUPO'] == filtro_grupo]

    if filtro_fornecedor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == filtro_fornecedor]

    if filtro_ano != 'Todos':
        df_filtrado = df_filtrado[
            df_filtrado['OrdemCompra'].fillna(0).astype(int).map(anos_oc) == int(filtro_ano)
        ]

    # ============================================================
    # 4. TABELA: Detalhamento de Itens (com coluna OC)
    # ============================================================
    st.markdown("---")
    st.subheader("📋 Detalhamento de Itens")

    # Exibir tabela
    df_display = df_filtrado[['Item', 'FAMILIA', 'GRUPO', 'OrdemCompra', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']].copy()
    df_display.columns = ['Item', 'Família', 'Grupo', 'OC', 'Fornecedor', 'Qtd', 'Valor']
    df_display['OC'] = df_display['OC'].fillna(0).astype(int)
    df_display['Ano'] = df_display['OC'].map(anos_oc).apply(
        lambda x: str(int(x)) if pd.notna(x) else '-'
    )
    df_display = df_display[['Item', 'Família', 'Grupo', 'OC', 'Ano', 'Fornecedor', 'Qtd', 'Valor']]
    df_display = df_display.sort_values('Valor', ascending=False)

    # Formatar valores para exibição
    df_display_formatted = df_display.copy()
    df_display_formatted['Valor'] = df_display_formatted['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(
        df_display_formatted,
        use_container_width=True,
        height=600,
        column_config={
            "Item": st.column_config.TextColumn("Item", help="Descrição do produto/serviço", width="large"),
            "Família": st.column_config.TextColumn("Família", help="Categoria principal", width="medium"),
            "Grupo": st.column_config.TextColumn("Grupo", help="Subcategoria", width="medium"),
            "OC": st.column_config.NumberColumn("OC", help="Ordem de Compra", width="small"),
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
            "Qtd": st.column_config.NumberColumn("Qtd", help="Quantidade comprada", width="small"),
            "Valor": st.column_config.TextColumn("Valor", help="Valor total do item", width="small")
        }
    )

    # Total filtrado
    total_filtrado = df_filtrado['ValorTotalComprado'].sum()
    percentual_filtrado = (total_filtrado / valor_total * 100) if valor_total > 0 else 0
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**💰 Total filtrado:** R$ {total_filtrado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({len(df_filtrado)} itens)")
    with col_info2:
        st.info(f"**📊 Representatividade:** {percentual_filtrado:.1f}% do valor total do projeto".replace(".", ","))

    # ============================================================
    # 5. GRÁFICO: Barras VERTICAIS (apenas para OS específica)
    # ============================================================
    if not is_todos_projetos:
        st.markdown("---")
        st.subheader("📊 Distribuição de Custos por Família")
        st.caption("Visualize onde está concentrado o maior custo do projeto")

        familia_df = os_details['familia_analysis'].reset_index()
        familia_df.columns = ['Família', 'Valor']
        familia_df['Percentual'] = (familia_df['Valor'] / valor_total * 100).round(1)

        # Filtrar apenas >1% e agrupar resto em "Outros"
        familia_significativa = familia_df[familia_df['Percentual'] > 1].copy()
        outros_valor = familia_df[familia_df['Percentual'] <= 1]['Valor'].sum()
        if outros_valor > 0:
            outros_percentual = (outros_valor / valor_total * 100).round(1)
            outros_row = pd.DataFrame([{'Família': 'Outros (<1%)', 'Valor': outros_valor, 'Percentual': outros_percentual}])
            familia_significativa = pd.concat([familia_significativa, outros_row], ignore_index=True)

        familia_significativa = familia_significativa.sort_values('Valor', ascending=False)

        fig = px.bar(
            familia_significativa,
            x='Família',
            y='Valor',
            orientation='v',
            text=familia_significativa.apply(lambda x: f"R$ {x['Valor']:,.0f}\n({x['Percentual']}%)".replace(",", "."), axis=1),
            color='Valor',
            color_continuous_scale='Reds'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Valor (R$)",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # 6. EXPORTS: Dados do projeto + Tabela filtrada
    # ============================================================
    st.markdown("---")
    st.subheader("📥 Exportar Dados")
    st.caption("Gere relatórios Excel para usar como referência em novos orçamentos")

    if is_todos_projetos:
        # Apenas export da tabela filtrada quando é "Todos os Projetos"
        excel_filtrado = export_excel_filtrado(df_filtrado, "Todos_Projetos")
        st.download_button(
            label="Exportar Tabela Filtrada (Excel)",
            data=excel_filtrado,
            file_name="CMV_Filtrado_Todos_Projetos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        col1, col2, col3 = st.columns(3)

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

        with col3:
            excel_filtrado = export_excel_filtrado(df_filtrado, selected_os)
            st.download_button(
                label="Exportar Filtrado (Excel)",
                data=excel_filtrado,
                file_name=f"CMV_Filtrado_OS_{str(selected_os).replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ============================================================
    # 7. CATEGORIZAÇÃO: Formulário (apenas para OS específica)
    # ============================================================
    if not is_todos_projetos:
        st.markdown("---")
        with st.expander("🏷️ Categorizar esta OS", expanded=not categoria_atual):
            st.caption("Categorize este projeto para facilitar buscas futuras e formar seu catálogo de soluções")
            
            col1, col2 = st.columns(2)

            with col1:
                area_selecionada = st.selectbox(
                    "Área de Atuação / Tipo de Solução",
                    options=AREAS_ATUACAO,
                    index=AREAS_ATUACAO.index(categoria_atual['area_atuacao']) if categoria_atual else 0,
                    help="Selecione o tipo de solução que melhor descreve este projeto"
                )

            with col2:
                complexidade_selecionada = st.selectbox(
                    "Complexidade / Porte do Projeto",
                    options=COMPLEXIDADES,
                    index=COMPLEXIDADES.index(categoria_atual['complexidade']) if categoria_atual else 1,
                    help="Pequena: até R$50k | Média: R$50k-200k | Grande: acima de R$200k"
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salvar Categorização", type="primary", use_container_width=True):
                    if categorizar_os(str(selected_os), area_selecionada, complexidade_selecionada):
                        st.success("✅ Categorização salva com sucesso!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar categorização")

            with col2:
                if categoria_atual:
                    st.caption(f"📅 Última atualização: {categoria_atual.get('data_categorizacao', '-')}")

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
