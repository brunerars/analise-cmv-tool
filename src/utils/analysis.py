import pandas as pd
from datetime import datetime


def analyze_os(df: pd.DataFrame) -> pd.DataFrame:
    """Analisa dados agregados por OS.

    Args:
        df: DataFrame com dados do CMV

    Returns:
        DataFrame com resumo por OS
    """
    os_summary = df.groupby('Numero_servico').agg({
        'ValorTotalComprado': 'sum',
        'Item': 'count',
        'Fornecedor': 'nunique',
        'FAMILIA': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
    }).reset_index()

    os_summary.columns = ['Numero_servico', 'ValorTotal', 'TotalItens', 'NumFornecedores', 'FamiliaPrincipal']
    os_summary['NumeroServico'] = os_summary['Numero_servico']
    os_summary = os_summary.sort_values('ValorTotal', ascending=False)

    return os_summary


def get_os_details(df: pd.DataFrame, codigo_os: str) -> dict:
    """Retorna detalhes completos de uma OS específica.

    Args:
        df: DataFrame com dados do CMV
        codigo_os: Código da OS para análise

    Returns:
        Dicionário com análises detalhadas
    """
    os_data = df[df['Numero_servico'] == codigo_os].copy()

    # Análise por família
    familia_analysis = os_data.groupby('FAMILIA')['ValorTotalComprado'].sum().sort_values(ascending=False)

    # Top itens
    top_itens = os_data.nlargest(10, 'ValorTotalComprado')[['Item', 'FAMILIA', 'Fornecedor', 'QuantidadeComprada', 'ValorTotalComprado']]

    # Fornecedores
    fornecedores = os_data['Fornecedor'].value_counts()

    return {
        'data': os_data,
        'familia_analysis': familia_analysis,
        'top_itens': top_itens,
        'fornecedores': fornecedores
    }


def export_ficha_tecnica(os_details: dict, codigo_os: str) -> str:
    """Gera ficha técnica da OS para download.

    Args:
        os_details: Dicionário retornado por get_os_details
        codigo_os: Código da OS

    Returns:
        Conteúdo da ficha técnica em texto
    """
    os_data = os_details['data']
    valor_total = os_data['ValorTotalComprado'].sum()

    content = f"""
FICHA TÉCNICA - OS {codigo_os}
=====================================
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESUMO FINANCEIRO
- Valor Total: R$ {valor_total:,.2f}
- Total de Itens: {len(os_data)}
- Número de Fornecedores: {os_data['Fornecedor'].nunique()}

DISTRIBUIÇÃO POR FAMÍLIA
"""

    for familia, valor in os_details['familia_analysis'].items():
        percentual = (valor / valor_total) * 100
        content += f"- {familia}: R$ {valor:,.2f} ({percentual:.1f}%)\n"

    content += "\nTOP 10 ITENS MAIS CAROS\n"
    for i, row in os_details['top_itens'].iterrows():
        content += f"- {row['Item']}: R$ {row['ValorTotalComprado']:,.2f} ({row['Fornecedor']})\n"

    content += f"\nFORNECEDORES UTILIZADOS\n"
    for fornecedor, count in os_details['fornecedores'].items():
        content += f"- {fornecedor}: {count} itens\n"

    return content
