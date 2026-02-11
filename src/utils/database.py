import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional


# Caminho do banco de dados
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "cmv_catalog.db"

# Áreas de atuação disponíveis
AREAS_ATUACAO = [
    "Linhas de Montagem",
    "Máquinas Especiais",
    "Controle de Qualidade",
    "Soluções Robóticas",
    "Soluções para Embalagem",
    "Soluções para Logística Interna"
]

# Níveis de complexidade
COMPLEXIDADES = ["Pequena", "Média", "Grande"]


def get_connection():
    """Retorna conexão com o banco SQLite."""
    return sqlite3.connect(str(DB_PATH))


def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS os_categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_servico TEXT UNIQUE NOT NULL,
            area_atuacao TEXT NOT NULL,
            complexidade TEXT NOT NULL,
            data_categorizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario TEXT
        )
    """)

    conn.commit()
    conn.close()


def categorizar_os(numero_servico: str, area_atuacao: str, complexidade: str, usuario: str = None) -> bool:
    """
    Categoriza uma OS com área de atuação e complexidade.

    Args:
        numero_servico: Código da OS
        area_atuacao: Área de atuação da máquina
        complexidade: Nível de complexidade (Pequena, Média, Grande)
        usuario: Nome do usuário que categorizou

    Returns:
        True se sucesso, False se erro
    """
    if area_atuacao not in AREAS_ATUACAO:
        raise ValueError(f"Área de atuação inválida: {area_atuacao}")
    if complexidade not in COMPLEXIDADES:
        raise ValueError(f"Complexidade inválida: {complexidade}")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO os_categorias (numero_servico, area_atuacao, complexidade, usuario, data_categorizacao)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(numero_servico) DO UPDATE SET
                area_atuacao = excluded.area_atuacao,
                complexidade = excluded.complexidade,
                usuario = excluded.usuario,
                data_categorizacao = excluded.data_categorizacao
        """, (numero_servico, area_atuacao, complexidade, usuario, datetime.now()))

        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao categorizar OS: {e}")
        return False
    finally:
        conn.close()


def get_categoria(numero_servico: str) -> Optional[dict]:
    """
    Retorna a categoria de uma OS específica.

    Args:
        numero_servico: Código da OS

    Returns:
        Dicionário com dados da categoria ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT numero_servico, area_atuacao, complexidade, data_categorizacao, usuario
        FROM os_categorias
        WHERE numero_servico = ?
    """, (numero_servico,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "numero_servico": row[0],
            "area_atuacao": row[1],
            "complexidade": row[2],
            "data_categorizacao": row[3],
            "usuario": row[4]
        }
    return None


def listar_categorizadas(area_atuacao: str = None, complexidade: str = None) -> list:
    """
    Lista todas as OSs categorizadas com filtros opcionais.

    Args:
        area_atuacao: Filtrar por área de atuação
        complexidade: Filtrar por complexidade

    Returns:
        Lista de dicionários com dados das OSs categorizadas
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT numero_servico, area_atuacao, complexidade, data_categorizacao, usuario FROM os_categorias WHERE 1=1"
    params = []

    if area_atuacao:
        query += " AND area_atuacao = ?"
        params.append(area_atuacao)

    if complexidade:
        query += " AND complexidade = ?"
        params.append(complexidade)

    query += " ORDER BY data_categorizacao DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "numero_servico": row[0],
            "area_atuacao": row[1],
            "complexidade": row[2],
            "data_categorizacao": row[3],
            "usuario": row[4]
        }
        for row in rows
    ]


def remover_categoria(numero_servico: str) -> bool:
    """
    Remove a categorização de uma OS.

    Args:
        numero_servico: Código da OS

    Returns:
        True se removido, False se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM os_categorias WHERE numero_servico = ?", (numero_servico,))
    rows_affected = cursor.rowcount

    conn.commit()
    conn.close()

    return rows_affected > 0


def contar_por_area() -> dict:
    """Retorna contagem de OSs por área de atuação."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT area_atuacao, COUNT(*) as total
        FROM os_categorias
        GROUP BY area_atuacao
        ORDER BY total DESC
    """)

    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    return result


def contar_por_complexidade() -> dict:
    """Retorna contagem de OSs por complexidade."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT complexidade, COUNT(*) as total
        FROM os_categorias
        GROUP BY complexidade
        ORDER BY
            CASE complexidade
                WHEN 'Pequena' THEN 1
                WHEN 'Média' THEN 2
                WHEN 'Grande' THEN 3
            END
    """)

    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    return result
