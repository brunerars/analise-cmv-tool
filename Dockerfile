FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar estrutura de diretórios para volumes
# IMPORTANTE: A pasta /app/data será sobrescrita pelo volume Docker
# O volume externo 'data_cmv_analise' deve ser montado em /app/data
# 
# Estrutura de dados persistidos:
# /app/data/
# ├── processed/
# │   └── cmv_data.csv          (CSV principal - deve ser copiado antes do deploy)
# ├── cmv_catalog.db            (SQLite - criado automaticamente pela aplicação)
# └── images/                   (Fotos - criadas automaticamente pelo upload)
#
# O banco SQLite é criado automaticamente na primeira execução
# e armazena todas as categorizações feitas pelos usuários
RUN mkdir -p /app/data/processed /app/data/images

# Expor porta padrão do Streamlit
EXPOSE 8501

# Healthcheck para monitoramento
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)" || exit 1

# Comando de inicialização do Streamlit
CMD ["streamlit", "run", "src/backend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true"]
