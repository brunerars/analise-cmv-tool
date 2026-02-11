import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    """Carrega e processa os dados do CMV.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        DataFrame com dados processados
    """
    df = pd.read_csv(csv_path)
    df['ValorTotalComprado'] = pd.to_numeric(df['ValorTotalComprado'], errors='coerce').fillna(0)
    df['QuantidadeComprada'] = pd.to_numeric(df['QuantidadeComprada'], errors='coerce').fillna(0)
    df['Numero_servico'] = pd.to_numeric(df['Numero_servico'], errors='coerce').fillna(0).astype(int)
    return df
