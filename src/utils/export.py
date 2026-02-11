import pandas as pd
from io import BytesIO
from datetime import datetime


def formatar_moeda(valor: float) -> str:
    """Formata valor para moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def export_excel_resumo(os_data: dict, numero_servico: str, categoria: dict = None) -> BytesIO:
    """
    Exporta resumo da OS para Excel (1 página).

    Args:
        os_data: Dicionário retornado por get_os_details
        numero_servico: Código da OS
        categoria: Dados de categorização (opcional)

    Returns:
        BytesIO com arquivo Excel
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#cc0000',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        money_format = workbook.add_format({'num_format': 'R$ #,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        title_format = workbook.add_format({'bold': True, 'font_size': 14})
        subtitle_format = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#f5f5f5'})

        # Criar planilha
        worksheet = workbook.add_worksheet('Resumo')

        # Título
        worksheet.write(0, 0, f"RESUMO CMV - OS {numero_servico}", title_format)
        worksheet.write(1, 0, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        row = 3

        # Informações da categoria (se existir)
        if categoria:
            worksheet.write(row, 0, "CATEGORIZAÇÃO", subtitle_format)
            worksheet.merge_range(row, 0, row, 3, "CATEGORIZAÇÃO", subtitle_format)
            row += 1
            worksheet.write(row, 0, "Área de Atuação:")
            worksheet.write(row, 1, categoria.get('area_atuacao', '-'))
            row += 1
            worksheet.write(row, 0, "Complexidade:")
            worksheet.write(row, 1, categoria.get('complexidade', '-'))
            row += 2

        # Resumo financeiro
        df = os_data['data']
        valor_total = df['ValorTotalComprado'].sum()
        total_itens = len(df)
        num_fornecedores = df['Fornecedor'].nunique()

        worksheet.write(row, 0, "RESUMO FINANCEIRO", subtitle_format)
        worksheet.merge_range(row, 0, row, 3, "RESUMO FINANCEIRO", subtitle_format)
        row += 1
        worksheet.write(row, 0, "Valor Total:")
        worksheet.write(row, 1, valor_total, money_format)
        row += 1
        worksheet.write(row, 0, "Total de Itens:")
        worksheet.write(row, 1, total_itens)
        row += 1
        worksheet.write(row, 0, "Fornecedores:")
        worksheet.write(row, 1, num_fornecedores)
        row += 2

        # Custo por família
        worksheet.write(row, 0, "CUSTO POR FAMÍLIA", subtitle_format)
        worksheet.merge_range(row, 0, row, 3, "CUSTO POR FAMÍLIA", subtitle_format)
        row += 1

        worksheet.write(row, 0, "Família", header_format)
        worksheet.write(row, 1, "Valor", header_format)
        worksheet.write(row, 2, "%", header_format)
        row += 1

        for familia, valor in os_data['familia_analysis'].items():
            percentual = (valor / valor_total) * 100
            worksheet.write(row, 0, familia, text_format)
            worksheet.write(row, 1, valor, money_format)
            worksheet.write(row, 2, f"{percentual:.1f}%", text_format)
            row += 1

        # Ajustar largura das colunas
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 18)
        worksheet.set_column(2, 2, 10)

    output.seek(0)
    return output


def export_excel_detalhado(os_data: dict, numero_servico: str, categoria: dict = None) -> BytesIO:
    """
    Exporta detalhamento completo da OS para Excel.

    Args:
        os_data: Dicionário retornado por get_os_details
        numero_servico: Código da OS
        categoria: Dados de categorização (opcional)

    Returns:
        BytesIO com arquivo Excel
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#cc0000',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        money_format = workbook.add_format({'num_format': 'R$ #,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1, 'text_wrap': True})

        # Planilha de resumo
        df = os_data['data']

        # Planilha 1: Resumo
        resumo_data = []
        valor_total = df['ValorTotalComprado'].sum()

        for familia, valor in os_data['familia_analysis'].items():
            percentual = (valor / valor_total) * 100
            resumo_data.append({
                'Família': familia,
                'Valor Total': valor,
                'Percentual': f"{percentual:.1f}%"
            })

        df_resumo = pd.DataFrame(resumo_data)
        df_resumo.to_excel(writer, sheet_name='Resumo por Família', index=False)

        worksheet_resumo = writer.sheets['Resumo por Família']
        for col_num, value in enumerate(df_resumo.columns.values):
            worksheet_resumo.write(0, col_num, value, header_format)
        worksheet_resumo.set_column(0, 0, 35)
        worksheet_resumo.set_column(1, 1, 18)
        worksheet_resumo.set_column(2, 2, 12)

        # Planilha 2: Todos os itens
        df_export = df[['Item', 'FAMILIA', 'GRUPO', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']].copy()
        df_export.columns = ['Item', 'Família', 'Grupo', 'Fornecedor', 'Quantidade', 'Valor']
        df_export = df_export.sort_values('Valor', ascending=False)
        df_export.to_excel(writer, sheet_name='Todos os Itens', index=False)

        worksheet_itens = writer.sheets['Todos os Itens']
        for col_num, value in enumerate(df_export.columns.values):
            worksheet_itens.write(0, col_num, value, header_format)
        worksheet_itens.set_column(0, 0, 50)
        worksheet_itens.set_column(1, 1, 25)
        worksheet_itens.set_column(2, 2, 20)
        worksheet_itens.set_column(3, 3, 25)
        worksheet_itens.set_column(4, 4, 12)
        worksheet_itens.set_column(5, 5, 15)

        # Planilha 3: Por fornecedor
        fornecedor_data = df.groupby('Fornecedor').agg({
            'ValorTotalComprado': 'sum',
            'Item': 'count'
        }).reset_index()
        fornecedor_data.columns = ['Fornecedor', 'Valor Total', 'Qtd Itens']
        fornecedor_data = fornecedor_data.sort_values('Valor Total', ascending=False)
        fornecedor_data.to_excel(writer, sheet_name='Por Fornecedor', index=False)

        worksheet_forn = writer.sheets['Por Fornecedor']
        for col_num, value in enumerate(fornecedor_data.columns.values):
            worksheet_forn.write(0, col_num, value, header_format)
        worksheet_forn.set_column(0, 0, 35)
        worksheet_forn.set_column(1, 1, 18)
        worksheet_forn.set_column(2, 2, 12)

    output.seek(0)
    return output


def export_excel_comparativo(lista_os: list, dados_os: dict) -> BytesIO:
    """
    Exporta comparativo entre múltiplas OSs.

    Args:
        lista_os: Lista de números de serviço para comparar
        dados_os: Dicionário {numero_servico: os_data}

    Returns:
        BytesIO com arquivo Excel
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#cc0000',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        money_format = workbook.add_format({'num_format': 'R$ #,##0.00', 'border': 1})

        # Criar comparativo de totais por família
        all_familias = set()
        for os_num in lista_os:
            if os_num in dados_os:
                all_familias.update(dados_os[os_num]['familia_analysis'].keys())

        comparativo = []
        for familia in sorted(all_familias):
            row = {'Família': familia}
            for os_num in lista_os:
                if os_num in dados_os:
                    valor = dados_os[os_num]['familia_analysis'].get(familia, 0)
                    row[f'OS {os_num}'] = valor
            comparativo.append(row)

        df_comp = pd.DataFrame(comparativo)
        df_comp.to_excel(writer, sheet_name='Comparativo', index=False)

        worksheet = writer.sheets['Comparativo']
        for col_num, value in enumerate(df_comp.columns.values):
            worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, 0, 30)
        for i in range(1, len(lista_os) + 1):
            worksheet.set_column(i, i, 18)

    output.seek(0)
    return output
