# 💾 Persistência de Dados - CMV Hub

Explicação detalhada sobre como os dados são armazenados e persistidos no sistema.

---

## 📂 Estrutura de Dados

O sistema utiliza **3 tipos de armazenamento persistente**:

### 1. CSV Principal (Leitura)
- **Arquivo**: `data/processed/cmv_data.csv`
- **Tamanho**: 3.8 MB
- **Linhas**: 24.277 registros de compras
- **Uso**: Base de dados principal (somente leitura)
- **Atualização**: Manual (substituir arquivo)

### 2. Banco SQLite (Leitura/Escrita)
- **Arquivo**: `data/cmv_catalog.db`
- **Tecnologia**: SQLite 3
- **Uso**: Armazenar categorizações e metadados
- **Criação**: Automática na primeira execução
- **Tabelas**:
  - `os_categorias` - Categorizações das OS
  - `maquinas_imagens` - Metadados das fotos

### 3. Arquivos de Imagem (Escrita)
- **Pasta**: `data/images/`
- **Formatos**: JPG, JPEG, PNG
- **Tamanho máximo**: 5 MB por imagem
- **Uso**: Fotos das máquinas enviadas pelos usuários

---

## 🐳 Persistência no Docker

### Volume Docker

Todo o diretório `/app/data` é montado como volume externo:

```yaml
volumes:
  - data_cmv_analise:/app/data
```

**Isso garante que todos os dados persistem**, incluindo:
- ✅ CSV de dados
- ✅ Banco SQLite (`cmv_catalog.db`)
- ✅ Imagens das máquinas

### Estrutura no Container

```
/app/data/                           (montado do volume 'data_cmv_analise')
├── processed/
│   └── cmv_data.csv                 (3.8 MB - Base principal)
├── cmv_catalog.db                   (SQLite - Categorizações)
└── images/
    ├── OS_1058_20260217123045.jpeg
    ├── OS_1128_20260217140822.png
    └── ...
```

---

## 🔄 Ciclo de Vida dos Dados

### Primeira Execução

1. **Volume criado**:
   ```bash
   docker volume create data_cmv_analise
   ```

2. **CSV copiado para o volume**:
   ```bash
   docker run --rm \
     -v data_cmv_analise:/data \
     -v $(pwd)/data:/source \
     alpine cp -r /source/* /data/
   ```

3. **Container inicia**:
   - Lê `cmv_data.csv`
   - Detecta ausência de `cmv_catalog.db`
   - **Cria automaticamente** o banco SQLite
   - Cria tabelas `os_categorias` e `maquinas_imagens`

4. **Usuário categoriza primeira OS**:
   - Dados salvos em `cmv_catalog.db`
   - Persistidos no volume Docker

5. **Usuário faz upload de foto**:
   - Arquivo salvo em `data/images/`
   - Metadados salvos em `cmv_catalog.db`

### Atualizações e Restarts

```bash
# Restart do serviço
docker service update --force analise-cmv_analise_cmv
```

**O que acontece:**
- ✅ Container reinicia
- ✅ Volume permanece intacto
- ✅ `cmv_catalog.db` mantém todas as categorizações
- ✅ Fotos continuam disponíveis
- ✅ Usuário vê exatamente o mesmo estado anterior

### Atualização da Aplicação

```bash
# Build nova versão
docker build -t analise-cmv:latest .

# Rolling update
docker service update --image analise-cmv:latest analise-cmv_analise_cmv
```

**O que acontece:**
- ✅ Novo container criado
- ✅ Volume montado no novo container
- ✅ **Todos os dados preservados**
- ✅ Zero downtime (rolling update)

---

## 🔍 Verificar Dados Persistidos

### Listar conteúdo do volume

```bash
# Ver estrutura completa
docker run --rm -v data_cmv_analise:/data alpine ls -lhR /data

# Ver apenas arquivos principais
docker run --rm -v data_cmv_analise:/data alpine ls -lh /data
```

### Verificar banco SQLite

```bash
# Entrar no container
docker exec -it $(docker ps -q -f name=analise-cmv) /bin/sh

# Dentro do container
ls -lh /app/data/cmv_catalog.db
du -h /app/data/cmv_catalog.db

# Ver tabelas SQLite
sqlite3 /app/data/cmv_catalog.db "SELECT name FROM sqlite_master WHERE type='table';"

# Contar registros
sqlite3 /app/data/cmv_catalog.db "SELECT COUNT(*) FROM os_categorias;"
```

### Verificar imagens

```bash
# Contar imagens
docker run --rm -v data_cmv_analise:/data alpine sh -c "ls -1 /data/images/*.{jpg,jpeg,png} 2>/dev/null | wc -l"

# Listar imagens com tamanhos
docker run --rm -v data_cmv_analise:/data alpine ls -lh /data/images/
```

---

## 💾 Backup e Restore

### Backup Completo

```bash
# Backup do volume inteiro (recomendado)
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/cmv_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Resultado: backup/cmv_backup_20260217_143022.tar.gz
```

### Backup Apenas SQLite

```bash
# Backup só do banco de categorizações
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/backup:/backup \
  alpine cp /data/cmv_catalog.db /backup/cmv_catalog_$(date +%Y%m%d).db
```

### Restore de Backup

```bash
# Restaurar volume completo
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/cmv_backup_20260217_143022.tar.gz -C /data

# Restart para aplicar
docker service update --force analise-cmv_analise_cmv
```

---

## 🚨 Cenários de Perda de Dados

### ⚠️ PERDA DE DADOS - O que NÃO fazer

```bash
# ❌ NUNCA faça isso (apaga o volume!)
docker volume rm data_cmv_analise

# ❌ NUNCA faça isso (remove stack E volume se não for externo)
docker stack rm analise-cmv
docker volume prune -f
```

### ✅ SEGURANÇA - Como proteger

1. **Volume externo** (já configurado):
   ```yaml
   volumes:
     data_cmv_analise:
       external: true  # ✅ Protege contra remoção acidental
   ```

2. **Backups regulares**:
   ```bash
   # Agendar backup diário (crontab)
   0 2 * * * /caminho/do/script/backup.sh
   ```

3. **Replicação** (opcional):
   ```bash
   # Copiar para outro servidor
   rsync -avz backup/ user@backup-server:/backups/cmv/
   ```

---

## 📊 Monitoramento de Dados

### Tamanho do Volume

```bash
# Ver uso do volume
docker system df -v | grep data_cmv_analise

# Detalhado
docker run --rm -v data_cmv_analise:/data alpine du -sh /data/*
```

### Crescimento ao Longo do Tempo

| Componente | Tamanho Inicial | Crescimento Esperado |
|------------|----------------|---------------------|
| `cmv_data.csv` | 3.8 MB | Estável (só atualizado manualmente) |
| `cmv_catalog.db` | ~20 KB | +5-10 KB por 100 OSs categorizadas |
| `images/` | 0 MB | +50-200 KB por foto (média 100 KB) |

**Exemplo após 1 ano de uso:**
- CSV: 3.8 MB (mesmo)
- SQLite: ~500 KB (assumindo 500 OSs categorizadas)
- Imagens: ~50 MB (assumindo 500 fotos)
- **Total: ~55 MB**

---

## 🔧 Manutenção

### Atualizar CSV de Dados

```bash
# 1. Fazer backup
docker run --rm -v data_cmv_analise:/data -v $(pwd)/backup:/backup \
  alpine cp /data/processed/cmv_data.csv /backup/cmv_data_old.csv

# 2. Copiar novo CSV
docker run --rm -v data_cmv_analise:/data -v $(pwd):/source \
  alpine cp /source/novo_cmv_data.csv /data/processed/cmv_data.csv

# 3. Restart para recarregar cache
docker service update --force analise-cmv_analise_cmv
```

### Limpar Banco SQLite (CUIDADO!)

```bash
# ⚠️ Isso apaga TODAS as categorizações!
# Fazer backup antes!

# 1. Backup
docker run --rm -v data_cmv_analise:/data -v $(pwd)/backup:/backup \
  alpine cp /data/cmv_catalog.db /backup/cmv_catalog_backup.db

# 2. Remover banco
docker run --rm -v data_cmv_analise:/data alpine rm /data/cmv_catalog.db

# 3. Restart (vai criar banco vazio)
docker service update --force analise-cmv_analise_cmv
```

### Limpar Imagens Órfãs

```bash
# Entrar no container
docker exec -it $(docker ps -q -f name=analise-cmv) python3 << 'EOF'
import sqlite3
from pathlib import Path

# Conectar ao banco
conn = sqlite3.connect('/app/data/cmv_catalog.db')
cursor = conn.cursor()

# Buscar imagens no banco
cursor.execute("SELECT caminho_arquivo FROM maquinas_imagens")
imagens_db = {row[0] for row in cursor.fetchall()}

# Buscar imagens no filesystem
imagens_fs = set(Path('/app/data/images').glob('*.{jpg,jpeg,png}'))

# Encontrar órfãs (no filesystem mas não no banco)
orfas = imagens_fs - {Path(img) for img in imagens_db}

print(f"Imagens órfãs encontradas: {len(orfas)}")
for img in orfas:
    print(f"  - {img}")
    # img.unlink()  # Descomentar para deletar
EOF
```

---

## 📝 Resumo

### ✅ O que está protegido

- **CSV de dados**: Persistido no volume
- **Banco SQLite**: Persistido no volume
- **Fotos**: Persistidas no volume
- **Categorizações**: Salvas no SQLite (persistido)
- **Configurações**: Parte da imagem Docker

### ⚡ Operações Seguras (não perdem dados)

- Restart do container
- Atualização da aplicação
- Redeploy da stack
- Remoção da stack (se volume é externo)

### ⚠️ Operações que Podem Perder Dados

- `docker volume rm data_cmv_analise` (remove tudo!)
- Substituir `cmv_catalog.db` sem backup
- Limpar pasta `images/` sem backup

### 🎯 Boas Práticas

1. ✅ Sempre criar volume como `external: true`
2. ✅ Fazer backup antes de operações destrutivas
3. ✅ Testar restore de backup periodicamente
4. ✅ Monitorar crescimento do volume
5. ✅ Documentar procedimentos de backup

---

**💡 Dica**: Configure backups automáticos diários para garantir que nenhuma categorização seja perdida!
