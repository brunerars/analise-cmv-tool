# 📊 Dashboard CMV - Análise por OS | ARV Systems

## 🎯 Objetivo

Sistema de análise de Custo de Mercadoria Vendida (CMV) para mapear custos por OS (Ordem de Serviço), permitindo:

1. **Categorização de Soluções**: Identificar padrões de custo por tipo de projeto
2. **Formação de Catálogo**: Criar referências de preço para soluções B2B customizadas
3. **Tomada de Decisão**: Fornecer "raio-x" financeiro para precificação futura

---

## 📈 Resumo Executivo dos Dados

### Dimensão da Base
- **24.277 linhas** de compras registradas
- **6.842 OSs únicas** (projetos individuais)
- **51 famílias** de produtos diferentes
- **R$ 19.881.536,75** em valor total de compras

### Top 5 OSs por Valor
1. **OS 1128/002**: R$ 1.247.647,77 (145 itens)
2. **OS 1058/004**: R$ 999.324,44 (294 itens)
3. **OS 1128/003**: R$ 763.088,29 (145 itens)
4. **OS 1058/003**: R$ 761.975,20 (134 itens)
5. **OS 1058/001**: R$ 675.144,92 (431 itens)

### Top 5 OSs por Quantidade de Itens
1. **OS 315/002**: 749 itens
2. **OS 1058/001**: 431 itens
3. **OS 1058/004**: 294 itens
4. **OS 1122/002**: 247 itens
5. **OS 315/001**: 227 itens

### Distribuição por Família (Top 5)
1. **MATERIAL ESPECÍFICO**: 3.980 itens (16.4%)
2. **MATERIAIS ELETROELETRÔNICOS**: 3.691 itens (15.2%)
3. **FERRAGENS**: 3.610 itens (14.9%)
4. **SERVIÇO EXTERNOS**: 2.490 itens (10.3%)
5. **PNEUMÁTICA**: 1.744 itens (7.2%)

---

## 🚀 Como Executar

### Desenvolvimento Local

#### Opção 1 - Script (Windows):
```bash
run.bat
```

#### Opção 2 - Comando direto:
```bash
streamlit run src/backend/app.py
```

#### Instalação de Dependências:
```bash
pip install -r requirements.txt
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

---

## 🐳 Deploy com Docker

### Pré-requisitos no Servidor

1. **Docker** e **Docker Compose** instalados
2. **Docker Swarm** inicializado
3. **Traefik** configurado como reverse proxy
4. **Network externa** `network_public` criada
5. **DNS** apontando `analise-cmv.arvsystems.cloud` para o servidor

### 1. Preparar o Volume de Dados

Antes do primeiro deploy, crie o volume Docker e popule com os dados:

```bash
# Criar volume externo
docker volume create data_cmv_analise

# Popular o volume com dados iniciais
# Método 1: Via container temporário (recomendado)
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/data:/source \
  alpine cp -r /source/* /data/

# Método 2: Copiar manualmente após primeiro deploy
# (ver seção "Manutenção de Dados" abaixo)
```

### 2. Build da Imagem

**Método 1 - GitOps (Recomendado)**:

```bash
# No servidor, clonar/atualizar o repositório
cd /caminho/do/projeto
git pull

# Build da imagem
docker build -t analise-cmv:latest .
```

**Método 2 - SSH + /tmp**:

```bash
# Clonar no /tmp do servidor via SSH
ssh usuario@servidor "cd /tmp && git clone https://github.com/seu-repo/analise-cmv-tool.git"

# Build
ssh usuario@servidor "cd /tmp/analise-cmv-tool && docker build -t analise-cmv:latest ."
```

### 3. Deploy no Docker Swarm

```bash
# Deploy da stack
docker stack deploy -c docker-compose.yml analise-cmv

# Verificar status
docker stack ps analise-cmv

# Ver logs
docker service logs -f analise-cmv_analise_cmv
```

### 4. Verificações Pós-Deploy

```bash
# 1. Verificar se o serviço está rodando
docker service ls

# 2. Verificar healthcheck
docker service ps analise-cmv_analise_cmv

# 3. Testar acesso local
curl http://localhost:8501/_stcore/health

# 4. Verificar logs
docker service logs --tail 50 analise-cmv_analise_cmv

# 5. Testar acesso via domínio
curl -I https://analise-cmv.arvsystems.cloud
```

### 5. Atualização da Aplicação

```bash
# 1. Atualizar código
git pull

# 2. Rebuild da imagem
docker build -t analise-cmv:latest .

# 3. Atualizar serviço (rolling update)
docker service update --image analise-cmv:latest analise-cmv_analise_cmv

# Ou redeploy completo
docker stack deploy -c docker-compose.yml analise-cmv
```

---

## 📁 Estrutura do Projeto

```
analise-cmv-tool/
├── .streamlit/
│   ├── config.toml              # Configurações do Streamlit (tema, cores)
│   └── pages.toml               # Configuração de navegação
├── data/                        # ⚠️ PERSISTIDO NO VOLUME DOCKER
│   ├── processed/
│   │   └── cmv_data.csv         # Base de dados principal (3.8MB)
│   ├── images/                  # Fotos das máquinas (upload usuário)
│   └── cmv_catalog.db           # ⚠️ Banco SQLite de categorizações
├── src/
│   ├── backend/
│   │   ├── app.py               # Página inicial
│   │   └── pages/
│   │       ├── 1_Categorizacao.py  # Consulta e categorização
│   │       └── 2_Catalogo.py       # Catálogo de máquinas
│   └── utils/
│       ├── data_processing.py   # Funções de carga de dados
│       ├── analysis.py          # Funções de análise
│       ├── database.py          # Operações de banco de dados
│       └── export.py            # Exportação para Excel
├── docs/
│   └── CLAUDE.md                # Documentação técnica
├── tests/
├── Dockerfile                   # Build da imagem Docker
├── docker-compose.yml           # Deploy no Swarm + Traefik
├── .dockerignore                # Exclusões do build
├── .env.example                 # Template de variáveis de ambiente
├── .gitignore                   # Proteção de dados sensíveis
├── deploy.sh                    # Script automatizado de deploy
├── requirements.txt             # Dependências Python
├── run.bat                      # Script de execução Windows
├── PERSISTENCIA_DADOS.md        # ⚠️ Documentação sobre persistência
├── DEPLOY_CHECKLIST.md          # Checklist de deploy
├── QUICKSTART.md                # Guia rápido
├── CHANGELOG.md                 # Registro de mudanças
└── README.md                    # Este arquivo
```

### ⚠️ Persistência de Dados

O sistema utiliza:
- **CSV** (`cmv_data.csv`): Base principal de dados (somente leitura)
- **SQLite** (`cmv_catalog.db`): Armazena categorizações feitas pelos usuários
- **Imagens**: Fotos das máquinas enviadas via upload

**Todos os dados são persistidos no volume Docker** `data_cmv_analise`.

📖 **Leia mais**: [PERSISTENCIA_DADOS.md](PERSISTENCIA_DADOS.md) para detalhes completos

---

## 🔧 Manutenção de Dados

### Atualizar CSV de Dados

```bash
# Método 1: Via container temporário
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd):/source \
  alpine cp /source/cmv_data.csv /data/processed/

# Método 2: Via container em execução
docker exec analise-cmv.1.xxxx \
  cp /tmp/novo_cmv_data.csv /app/data/processed/cmv_data.csv

# Reiniciar para recarregar cache
docker service update --force analise-cmv_analise_cmv
```

### Backup do Volume

```bash
# Backup completo do volume (dados + banco + imagens)
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/cmv_backup_$(date +%Y%m%d).tar.gz -C /data .

# Listar backups
ls -lh backup/

# Restaurar backup
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/cmv_backup_YYYYMMDD.tar.gz -C /data
```

### Backup do Banco SQLite

```bash
# Backup apenas do banco de categorizações
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd):/backup \
  alpine cp /data/cmv_catalog.db /backup/cmv_catalog_backup_$(date +%Y%m%d).db
```

---

## 📋 Funcionalidades Principais

### 1. Página Inicial (Dashboard)
- **Métricas gerais**: Total de OSs, OSs categorizadas, valor total
- **Indicadores visuais**: Progresso de categorização
- **Navegação**: Cards com descrição das funcionalidades
- **Informações contextuais**: Dicas de uso e fluxo de trabalho

### 2. Categorização de OS
- **Busca e seleção**: Escolha uma OS específica ou explore toda a base
- **Filtros avançados**: Por item, OC, família, grupo, fornecedor
- **Análise detalhada**: Métricas financeiras, gráficos de distribuição
- **Categorização**: Atribua área de atuação e complexidade
- **Exportação**: Gere relatórios Excel (resumo, detalhado, filtrado)

### 3. Catálogo de Máquinas
- **Galeria visual**: Cards com fotos e informações principais
- **Filtros**: Por área de atuação e complexidade
- **Detalhamento**: Modal com análise completa do projeto
- **Gestão de fotos**: Upload, visualização e remoção de imagens
- **Estatísticas**: Contadores por categoria

---

## 💡 Casos de Uso

### Para Orçamentistas
1. **Buscar projetos similares** ao novo orçamento
2. **Filtrar por família** para encontrar componentes específicos
3. **Exportar listas** de itens para usar como base
4. **Comparar custos** entre projetos semelhantes

### Para Gestores
1. **Visualizar distribuição** de custos por tipo de solução
2. **Identificar padrões** de composição de projetos
3. **Analisar fornecedores** mais utilizados
4. **Acompanhar progresso** de categorização

### Para Time Técnico
1. **Categorizar projetos** por área e complexidade
2. **Documentar soluções** com fotos e descrições
3. **Criar referências** para novos orçamentos
4. **Padronizar nomenclaturas** e famílias

---

## 🔒 Segurança e Privacidade

- ⚠️ **Dados sensíveis**: Base contém informações comerciais confidenciais da ARV Systems
- 🔐 **Recomendado**: Não compartilhar fora da organização
- 📁 **Backup**: Manter cópias seguras dos dados
- 🔑 **Autenticação**: Considere adicionar autenticação para deploy em produção

---

## 🆘 Troubleshooting

### Problema: Dashboard não carrega dados

**Solução**:
```bash
# Verificar se o CSV está no volume
docker exec analise-cmv.1.xxxx ls -lh /app/data/processed/

# Verificar logs
docker service logs --tail 100 analise-cmv_analise_cmv
```

### Problema: Erro ao salvar categorização

**Solução**:
```bash
# Verificar permissões do banco
docker exec analise-cmv.1.xxxx ls -lh /app/data/

# Se necessário, recriar o banco (CUIDADO: apaga categorizações)
docker exec analise-cmv.1.xxxx rm /app/data/cmv_catalog.db
docker service update --force analise-cmv_analise_cmv
```

### Problema: Imagens não aparecem

**Solução**:
```bash
# Verificar pasta de imagens
docker exec analise-cmv.1.xxxx ls -lh /app/data/images/

# Verificar permissões
docker exec analise-cmv.1.xxxx chmod -R 755 /app/data/images/
```

### Problema: Container reiniciando continuamente

**Solução**:
```bash
# Ver logs detalhados
docker service logs --tail 200 --follow analise-cmv_analise_cmv

# Verificar healthcheck
docker inspect $(docker ps -q -f name=analise-cmv)

# Verificar recursos
docker stats
```

---

## 📞 Contatos e Responsáveis

- **Product Owner**: Bruno (Head of Industrial Systems)
- **Stakeholders**: Gestores ARV, Time Técnico, Comercial
- **Objetivo de Negócio**: Reduzir tempo de orçamento em 50% via catalogação

---

## 📝 Notas Importantes

1. **Dados em Produção**: Base de 24k+ registros reais
2. **Performance**: Primeira carga pode demorar alguns segundos
3. **Atualizações**: Substituir CSV no volume para atualizar dados
4. **Customização**: Código-fonte disponível para modificações
5. **Escalabilidade**: Considerar otimizações para crescimento da base

---

## 📄 Licença e Uso

Projeto interno da **ARV Systems**. Uso restrito a funcionários autorizados.

**Versão**: 2.0  
**Última Atualização**: Fevereiro 2026  
**Desenvolvedor**: Bruno - Head of Industrial Systems | ARV Systems

---

## 🏆 Resultado Esperado

Ao final do processo de catalogação, a ARV Systems terá:

✅ **Catálogo de Soluções**: 5-10 tipos padrão de projeto documentados  
✅ **Faixas de Preço**: Referências claras para cada tipo de solução  
✅ **Processo Otimizado**: Orçamentos mais rápidos e precisos  
✅ **Vantagem Competitiva**: Capacidade de resposta ágil mantendo customização



---

## 📋 Funcionalidades Principais

### 1. Visão Geral
- Cards com estatísticas consolidadas
- Valor total, número de OSs, ticket médio
- Distribuição por família de produtos

### 2. Busca e Filtros
- 🔍 Buscar OS por código
- 📦 Filtrar por família de produtos
- 🔢 Ordenar por valor, quantidade de itens ou código

### 3. Análise por OS
- **Resumo Financeiro**: Valor total, número de itens, fornecedores
- **Gráfico de Pizza**: Distribuição de custo por família
- **Gráfico de Barras**: Top 10 itens mais caros
- **Tabela Detalhada**: Lista completa de itens com fornecedor e valores

### 4. Export de Ficha Técnica
Gera arquivo .txt com:
- Resumo financeiro da OS
- Distribuição de custos por família
- Top 10 itens mais caros
- Lista de fornecedores utilizados

**Ideal para:** Documentação interna, apresentações ao time, catalogação de soluções

---

## 💡 Casos de Uso Práticos

### Para o Gestor
1. **Benchmarking de Projetos**: Comparar OSs similares e identificar oportunidades de otimização
2. **Precificação Estratégica**: Usar dados históricos como base para novos orçamentos
3. **Análise de Fornecedores**: Identificar concentração de compras e negociar melhores condições

### Para o Time de Engenharia
1. **Categorização de Soluções**: 
   - Agrupar OSs por similaridade (família principal, faixa de valor)
   - Criar "templates" de solução baseados em projetos anteriores
   
2. **Padronização de Componentes**:
   - Identificar itens recorrentes em múltiplas OSs
   - Reduzir variedade de fornecedores para ganhar escala

3. **Formação de Catálogo**:
   - Documentar "receitas" de projetos bem-sucedidos
   - Criar faixas de preço por tipo de solução

### Para Comercial
1. **Orçamentos mais Rápidos**: Usar fichas técnicas como base
2. **Negociação com Clientes**: Demonstrar composição de custos
3. **Identificar Soluções Rentáveis**: Focar em projetos com melhor margem

---

## 📊 Métricas Importantes

### Ticket Médio por OS
**R$ 2.907,00** - Valor médio de investimento por projeto

### Concentração de Valor
- Top 10 OSs representam aproximadamente **30%** do valor total
- Indica alguns projetos de grande porte (>R$ 300k)

### Diversidade de Famílias
51 famílias diferentes mostram alta complexidade e customização das soluções

---

## 🎯 Próximos Passos Sugeridos

### Curto Prazo (1-2 semanas)
1. ✅ **Categorizar Top 20 OSs**
   - Time deve analisar as OSs mais relevantes
   - Criar tags de tipo de solução (ex: "Linha Transportadora Pesada", "Sistema de Inspeção Visual")
   
2. ✅ **Identificar Padrões**
   - OSs similares em valor e composição
   - Famílias que sempre aparecem juntas

### Médio Prazo (1 mês)
1. **Criar Catálogo de Soluções**
   - 5-10 "tipos padrão" de projeto
   - Faixas de preço por tipo
   - Componentes principais de cada solução

2. **Dashboard Avançado**
   - Adicionar campo de "Tipo de Solução" ao banco de dados
   - Gráficos de comparação entre tipos
   - Análise de margem por tipo

### Longo Prazo (3 meses)
1. **Sistema de Precificação Automatizada**
   - Input: Tipo de solução + customizações
   - Output: Orçamento baseado em histórico + margem

2. **Integração com CRM**
   - Vincular OSs a oportunidades de venda
   - Rastreabilidade completa: lead → proposta → OS → entrega

---



---



---

## 🔒 Segurança e Privacidade

- ⚠️ Dados sensíveis: Arquivo contém informações comerciais confidenciais
- 🔐 Recomendado: Não compartilhar fora da organização
- 📁 Backup: Manter cópias seguras dos arquivos originais

---

## 🆘 Suporte

### Problemas Comuns

**Dashboard HTML não carrega dados:**
- Verificar se `cmv_data.csv` está na mesma pasta
- Abrir console do navegador (F12) para ver erros

**Dashboard Streamlit trava:**
- Base muito grande - usar filtros para reduzir dados
- Aumentar memória disponível

**Gráficos não aparecem:**
- Atualizar navegador
- Desabilitar bloqueadores de JavaScript

### Contato
Para dúvidas ou sugestões de melhorias, contatar o time de sistemas.

---

## 📝 Notas Importantes

1. **Dados Reais**: Este dashboard usa a base de produção com 24k+ registros
2. **Performance**: Primeira carga pode demorar alguns segundos
3. **Atualizações**: Substituir `cmv_data.csv` para atualizar dados
4. **Customização**: Código-fonte disponível para modificações

---

## 🏆 Resultado Esperado

Ao final do processo de catalogação, a ARV Systems terá:

✅ **Catálogo de Soluções**: 5-10 tipos padrão de projeto documentados
✅ **Faixas de Preço**: Referências claras para cada tipo de solução
✅ **Processo Otimizado**: Orçamentos mais rápidos e precisos
✅ **Vantagem Competitiva**: Capacidade de resposta ágil mantendo customização

---

**Versão**: 1.0  
**Data**: Fevereiro 2026  
**Desenvolvido por**: Bruno - Head of Industrial Systems | ARV Systems
