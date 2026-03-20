import io
import pandas as pd
import os
from pathlib import Path


def get_data_path() -> Path:
    """
    Retorna o caminho correto para os dados, considerando ambiente Docker ou local.
    
    - No Docker: /app/data (volume montado)
    - Local: <ROOT_DIR>/data (calculado a partir do arquivo)
    
    Returns:
        Path para o diretório data/
    """
    # Verificar se está rodando no Docker (verifica se /app existe e está em /app)
    if os.path.exists('/app') and str(Path(__file__).resolve()).startswith('/app'):
        # Ambiente Docker
        return Path('/app/data')
    else:
        # Ambiente local - calcular ROOT_DIR a partir deste arquivo
        # data_processing.py está em: src/utils/
        # ROOT_DIR é 2 níveis acima: src/utils/ -> src/ -> ROOT_DIR/
        return Path(__file__).resolve().parent.parent.parent / 'data'


def load_data(csv_path: str) -> pd.DataFrame:
    """Carrega e processa os dados do CMV.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        DataFrame com dados processados
    """
    # Ler arquivo bruto, detectar encoding e limpar bytes NULL (0x00)
    # O ERP injeta NULL bytes dentro de campos RTF multiline
    for enc in ('utf-8', 'latin-1'):
        try:
            with open(csv_path, 'r', encoding=enc, errors='replace') as f:
                raw = f.read()
            break
        except UnicodeDecodeError:
            continue

    clean = raw.replace('\x00', '')

    first_line = clean.split('\n', 1)[0]
    delimiter = ';' if first_line.count(';') > first_line.count(',') else ','
    decimal = ',' if delimiter == ';' else '.'

    df = pd.read_csv(io.StringIO(clean), delimiter=delimiter, decimal=decimal)

    COLUNAS_NUMERICAS = ['ValorTotalComprado', 'QuantidadeComprada', 'Numero_servico',
                         'ValorTotalPedenteEntrega', 'QuantidadePendenteEntrega']
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Numero_servico' in df.columns:
        df['Numero_servico'] = df['Numero_servico'].astype(int)
    return df
