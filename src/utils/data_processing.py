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
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='latin-1')
    df['ValorTotalComprado'] = pd.to_numeric(df['ValorTotalComprado'], errors='coerce').fillna(0)
    df['QuantidadeComprada'] = pd.to_numeric(df['QuantidadeComprada'], errors='coerce').fillna(0)
    df['Numero_servico'] = pd.to_numeric(df['Numero_servico'], errors='coerce').fillna(0).astype(int)
    return df
