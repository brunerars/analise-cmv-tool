import csv
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
    # Detectar encoding (UTF-8 ou Latin-1) e delimitador (, ou ;)
    for enc in ('utf-8', 'latin-1'):
        try:
            with open(csv_path, 'r', encoding=enc) as f:
                first_line = f.readline()
            break
        except UnicodeDecodeError:
            continue

    # Detectar delimitador pelo header (mais confiável que Sniffer com dados RTF)
    delimiter = ';' if first_line.count(';') > first_line.count(',') else ','

    if delimiter == ';':
        # CSV brasileiro: ; como delimitador, , como decimal
        df = pd.read_csv(csv_path, encoding=enc, delimiter=';', decimal=',')
    else:
        df = pd.read_csv(csv_path, encoding=enc, delimiter=',')

    COLUNAS_NUMERICAS = ['ValorTotalComprado', 'QuantidadeComprada', 'Numero_servico',
                         'ValorTotalPedenteEntrega', 'QuantidadePendenteEntrega']
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Numero_servico' in df.columns:
        df['Numero_servico'] = df['Numero_servico'].astype(int)
    return df
