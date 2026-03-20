import io
import re
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


def find_data_file() -> Path:
    """Encontra o arquivo de dados (XLSX ou CSV) no diretório processed/."""
    data_dir = get_data_path() / "processed"
    # Prioridade: XLSX > CSV (XLSX não tem problemas de encoding/NULL bytes)
    for ext in ('xlsx', 'csv'):
        path = data_dir / f"cmv_data.{ext}"
        if path.exists():
            return path
    # Fallback: qualquer xlsx ou csv na pasta
    for ext in ('*.xlsx', '*.csv'):
        files = list(data_dir.glob(ext))
        if files:
            return files[0]
    raise FileNotFoundError(f"Nenhum arquivo de dados encontrado em {data_dir}")


def strip_rtf(text: str) -> str:
    """Remove marcação RTF e retorna texto limpo."""
    if not isinstance(text, str) or not text.strip().startswith('{\\rtf'):
        return text

    # Converter escapes hex RTF (\'c1 -> Á, \'d3 -> Ó, etc.)
    def hex_to_char(m):
        try:
            return bytes.fromhex(m.group(1)).decode('cp1252')
        except Exception:
            return ''

    s = text
    # Remover grupos de header que não contêm texto visível
    s = re.sub(r'\{\\fonttbl[^}]*\}', '', s)
    s = re.sub(r'\{\\colortbl[^}]*\}', '', s)
    s = re.sub(r'\{\\\*\\generator[^}]*\}', '', s)
    # Converter hex escapes antes de remover control words
    s = re.sub(r"\\\'([0-9a-fA-F]{2})", hex_to_char, s)
    # \par -> newline
    s = s.replace('\\par', '\n')
    # Remover control words (\word123 ou \word seguido de espaço)
    s = re.sub(r'\\[a-zA-Z]+\d*\s?', '', s)
    # Remover chaves
    s = s.replace('{', '').replace('}', '')
    # Limpar espaços e newlines extras
    s = re.sub(r'\n+', ' / ', s.strip())
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip().strip('/')


def load_data(file_path: str) -> pd.DataFrame:
    """Carrega e processa os dados do CMV (CSV ou XLSX).

    Args:
        file_path: Caminho para o arquivo de dados

    Returns:
        DataFrame com dados processados
    """
    path = Path(file_path)

    if path.suffix.lower() in ('.xlsx', '.xls'):
        df = pd.read_excel(file_path)
    else:
        # CSV: ler bruto, limpar NULL bytes do ERP, detectar delimitador
        for enc in ('utf-8', 'latin-1'):
            try:
                with open(file_path, 'r', encoding=enc, errors='replace') as f:
                    raw = f.read()
                break
            except UnicodeDecodeError:
                continue

        clean = raw.replace('\x00', '')
        first_line = clean.split('\n', 1)[0]
        delimiter = ';' if first_line.count(';') > first_line.count(',') else ','
        decimal = ',' if delimiter == ';' else '.'
        df = pd.read_csv(io.StringIO(clean), delimiter=delimiter, decimal=decimal)

    # Converter colunas numéricas
    COLUNAS_NUMERICAS = ['ValorTotalComprado', 'QuantidadeComprada', 'Numero_servico',
                         'ValorTotalPedenteEntrega', 'QuantidadePendenteEntrega']
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Numero_servico' in df.columns:
        df['Numero_servico'] = df['Numero_servico'].astype(int)

    # Limpar RTF de colunas de texto
    COLUNAS_TEXTO = ['Item', 'FAMILIA', 'GRUPO', 'Fornecedor']
    for col in COLUNAS_TEXTO:
        if col in df.columns:
            df[col] = df[col].apply(strip_rtf)

    return df
