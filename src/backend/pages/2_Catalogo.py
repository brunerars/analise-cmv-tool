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
    contar_por_area, remover_categoria, AREAS_ATUACAO, COMPLEXIDADES,
    salvar_imagem_maquina, get_imagem_principal, remover_imagem_maquina
)

# Caminho dos dados
DATA_PATH = ROOT_DIR / "data" / "processed" / "cmv_data.csv"

# Inicializar banco
init_db()

st.title("Catálogo de Máquinas")
st.markdown("Visualize seus projetos categorizados")

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

    st.sidebar.metric("Total Categorizadas", len(os_categorizadas))

    if contagem_area:
        st.sidebar.markdown("**Por Área:**")
        for area, count in contagem_area.items():
            st.sidebar.caption(f"• {area[:20]}...: {count}")

    # Conteúdo principal
    if not os_categorizadas:
        st.info("Nenhuma OS categorizada ainda. Vá para 'Categorização' para categorizar.")

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

            # Buscar imagem da máquina
            imagem = get_imagem_principal(os_cat['numero_servico'])

            with col:
                # Card com container
                with st.container():
                    # Estilo do card - Cores ARV (preto, vermelho, branco)
                    card_style = "border: 2px solid #cc0000; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: #1a1a1a;"

                    st.markdown(f"""
                    <div style="{card_style}">
                        <h4 style="margin: 0; color: #ffffff;">OS {os_cat['numero_servico']}</h4>
                        <p style="margin: 5px 0; font-size: 0.9em; color: #cccccc;">{os_cat['area_atuacao']}</p>
                        <p style="margin: 5px 0; color: #cc0000;"><strong>{icon}</strong> {os_cat['complexidade']}</p>
                        <p style="margin: 5px 0; font-size: 1.2em; font-weight: bold; color: #ffffff;">R$ {valor_total:,.0f}</p>
                        <p style="margin: 0; font-size: 0.8em; color: #888888;">{total_itens} itens</p>
                    </div>
                    """.replace(",", "."), unsafe_allow_html=True)

                    # Mostrar thumbnail da imagem se existir
                    if imagem:
                        try:
                            st.image(imagem['caminho_arquivo'], width=150, caption="Foto da máquina")
                        except Exception:
                            pass

                    # Botões (Ver e Excluir)
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Ver", key=f"ver_{os_cat['numero_servico']}", use_container_width=True):
                            st.session_state.os_detalhada = os_cat['numero_servico']

                    with btn_col2:
                        if st.button("🗑", key=f"del_{os_cat['numero_servico']}", use_container_width=True):
                            if remover_categoria(os_cat['numero_servico']):
                                st.rerun()

        # Modal de detalhes (se uma OS foi selecionada para ver)
        if 'os_detalhada' in st.session_state and st.session_state.os_detalhada:
            st.markdown("---")
            st.subheader(f"Detalhes - OS {st.session_state.os_detalhada}")

            # Converter para int antes de buscar os detalhes
            try:
                os_num_int = int(st.session_state.os_detalhada)
            except (ValueError, TypeError):
                os_num_int = st.session_state.os_detalhada

            os_details = get_os_details(df, os_num_int)
            os_data = os_details['data']
            categoria = get_categoria(str(st.session_state.os_detalhada))

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Valor Total", f"R$ {os_data['ValorTotalComprado'].sum():,.0f}".replace(",", "."))
            with col2:
                st.metric("Itens", len(os_data))
            with col3:
                st.metric("Área", categoria['area_atuacao'][:15] + "..." if categoria else "-")
            with col4:
                st.metric("Complexidade", categoria['complexidade'] if categoria else "-")

            # ============================================================
            # Seção de Imagem da Máquina
            # ============================================================
            st.markdown("---")
            st.subheader("Foto da Máquina")

            imagem_atual = get_imagem_principal(str(st.session_state.os_detalhada))

            col_img1, col_img2 = st.columns([2, 1])

            with col_img1:
                if imagem_atual:
                    try:
                        st.image(imagem_atual['caminho_arquivo'], caption=imagem_atual.get('descricao') or 'Foto da máquina', width=400)
                    except Exception as e:
                        st.warning(f"Não foi possível carregar a imagem: {e}")

            with col_img2:
                # Upload de nova imagem
                uploaded_file = st.file_uploader(
                    "Adicionar/Substituir foto",
                    type=['png', 'jpg', 'jpeg'],
                    key=f"upload_{st.session_state.os_detalhada}"
                )

                if uploaded_file:
                    # Validar tamanho (5MB)
                    if uploaded_file.size > 5 * 1024 * 1024:
                        st.error("Arquivo muito grande. Máximo: 5MB")
                    else:
                        descricao_img = st.text_input("Descrição (opcional)", key="desc_img")
                        if st.button("Salvar Imagem", type="primary"):
                            if salvar_imagem_maquina(str(st.session_state.os_detalhada), uploaded_file, descricao_img):
                                st.success("Imagem salva com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao salvar imagem")

                # Botão para remover imagem existente
                if imagem_atual:
                    if st.button("Remover Imagem", key="remove_img"):
                        if remover_imagem_maquina(imagem_atual['id']):
                            st.success("Imagem removida!")
                            st.rerun()

            # ============================================================
            # Gráfico de Pizza - Famílias > 1%
            # ============================================================
            st.markdown("---")
            st.subheader("Distribuição por Família (>1%)")

            familia_df = os_details['familia_analysis'].reset_index()
            familia_df.columns = ['Família', 'Valor']

            if not familia_df.empty and familia_df['Valor'].sum() > 0:
                valor_total = familia_df['Valor'].sum()
                familia_df['Percentual'] = (familia_df['Valor'] / valor_total) * 100

                # Filtrar apenas >1%
                familia_significativa = familia_df[familia_df['Percentual'] > 1].copy()

                # Agrupar os <1% em "Outros"
                outros_valor = familia_df[familia_df['Percentual'] <= 1]['Valor'].sum()
                if outros_valor > 0:
                    outros_row = pd.DataFrame([{'Família': 'Outros (<1%)', 'Valor': outros_valor, 'Percentual': (outros_valor / valor_total) * 100}])
                    familia_significativa = pd.concat([familia_significativa, outros_row], ignore_index=True)

                fig = px.pie(
                    familia_significativa,
                    names='Família',
                    values='Valor',
                    title='',
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

            # ============================================================
            # Lista de Itens do Projeto
            # ============================================================
            st.markdown("---")
            st.subheader("Itens do Projeto")

            # Preparar tabela de itens
            df_itens = os_data[['Item', 'FAMILIA', 'OrdemCompra', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']].copy()
            df_itens.columns = ['Item', 'Família', 'OC', 'Fornecedor', 'Qtd', 'Valor']
            df_itens['OC'] = df_itens['OC'].fillna(0).astype(int)
            df_itens = df_itens.sort_values('Valor', ascending=False)

            # Formatar valores
            df_itens_display = df_itens.copy()
            df_itens_display['Valor'] = df_itens_display['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(
                df_itens_display,
                use_container_width=True,
                height=300
            )

            st.caption(f"Total: {len(df_itens)} itens")

            # Botões de ação
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Fechar Detalhes", use_container_width=True):
                    del st.session_state.os_detalhada
                    st.rerun()
            with col2:
                if st.button("Excluir do Catálogo", type="primary", use_container_width=True):
                    if remover_categoria(str(st.session_state.os_detalhada)):
                        del st.session_state.os_detalhada
                        st.rerun()

except FileNotFoundError:
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)
