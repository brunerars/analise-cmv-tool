# 🚀 Quick Start - CMV Hub

Guia rápido para começar a usar o sistema.

---

## 💻 Desenvolvimento Local (5 minutos)

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar Aplicação

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
streamlit run src/backend/app.py
```

### 3. Acessar

Abra o navegador em: **http://localhost:8501**

---

## 🐳 Deploy em Produção (15 minutos)

### Pré-requisitos

- Docker e Docker Swarm configurados
- Traefik rodando como reverse proxy
- Network `network_public` criada
- DNS apontando para o servidor

### Deploy Rápido

```bash
# 1. Criar volume
docker volume create data_cmv_analise

# 2. Popular volume com dados
docker run --rm -v data_cmv_analise:/data -v $(pwd)/data:/source alpine cp -r /source/* /data/

# 3. Deploy automático
chmod +x deploy.sh
./deploy.sh
```

**Pronto!** Acesse: https://analise-cmv.arvsystems.cloud

### Deploy Manual

```bash
# 1. Build
docker build -t analise-cmv:latest .

# 2. Deploy
docker stack deploy -c docker-compose.yml analise-cmv

# 3. Verificar
docker service logs -f analise-cmv_analise_cmv
```

---

## 📖 Como Usar

### 1. Página Inicial
- Veja estatísticas gerais da base
- Navegue entre Categorização e Catálogo

### 2. Categorização
- **Selecione uma OS** para ver detalhes
- **Use filtros** para encontrar componentes específicos
- **Exporte para Excel** para usar em orçamentos
- **Categorize o projeto** por área e complexidade

### 3. Catálogo
- **Filtre por área** de atuação ou complexidade
- **Visualize projetos** categorizados
- **Adicione fotos** das máquinas
- **Compare projetos** similares

---

## 🔧 Comandos Úteis

### Ver Logs
```bash
docker service logs -f analise-cmv_analise_cmv
```

### Atualizar Aplicação
```bash
git pull
docker build -t analise-cmv:latest .
docker service update --image analise-cmv:latest analise-cmv_analise_cmv
```

### Backup de Dados
```bash
docker run --rm -v data_cmv_analise:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/backup_$(date +%Y%m%d).tar.gz -C /data .
```

### Atualizar CSV
```bash
docker run --rm -v data_cmv_analise:/data -v $(pwd):/source \
  alpine cp /source/cmv_data.csv /data/processed/
  
docker service update --force analise-cmv_analise_cmv
```

---

## 🆘 Problemas Comuns

### Dashboard não carrega dados
```bash
# Verificar se CSV está no volume
docker exec <container_id> ls -lh /app/data/processed/
```

### Erro ao salvar categorização
```bash
# Verificar permissões do banco
docker exec <container_id> ls -lh /app/data/
```

### Container reiniciando
```bash
# Ver logs detalhados
docker service logs --tail 200 analise-cmv_analise_cmv
```

---

## 📚 Mais Informações

- **README.md**: Documentação completa
- **DEPLOY_CHECKLIST.md**: Checklist passo a passo
- **docs/CLAUDE.md**: Documentação técnica

---

## 🎯 Fluxo de Trabalho Recomendado

1. **Consultar** projetos similares na Categorização
2. **Filtrar** por família/fornecedor específico
3. **Exportar** listas para usar como referência
4. **Categorizar** o projeto por tipo de solução
5. **Adicionar foto** no Catálogo para referência visual
6. **Comparar** com outros projetos similares

---

**Desenvolvido por:** Bruno - Head of Industrial Systems | ARV Systems  
**Versão:** 2.0  
**Data:** Fevereiro 2026
