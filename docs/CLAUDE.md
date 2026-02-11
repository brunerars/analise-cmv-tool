# Dashboard CMV - Análise por OS | ARV Systems

## Contexto do Projeto

### Objetivo
Sistema de análise de Custo de Mercadoria Vendida (CMV) para mapear custos por OS (Ordem de Serviço), permitindo categorização de soluções B2B e formação de catálogo de referência para precificação.

### Problema de Negócio
A ARV Systems é uma empresa B2B de automação industrial que trabalha com soluções 100% customizadas. Apesar de não termos "produtos de prateleira", precisamos:
1. **Criar referências de custo** para acelerar orçamentos futuros
2. **Categorizar soluções similares** para formar um "catálogo mental" do time
3. **Fornecer "raio-x" financeiro** dos projetos para melhorar precificação

### Usuários
- **Gestor**: Precisa de visão estratégica, ROI, oportunidades de otimização
- **Time Técnico**: Precisa categorizar soluções e identificar padrões
- **Comercial**: Precisa de referências rápidas para orçamentos

---

## Estrutura de Dados

### Base Principal: CMV Detalhado
**Arquivo**: `cmv_data.csv` (24.277 linhas, 3.8MB)

**Colunas**:
```
1. Empresa              - Nome da empresa (sempre ARV SYSTEM)
2. Item                 - Descrição do item comprado
3. FAMILIA              - Categoria principal (51 famílias únicas)
4. GRUPO                - Subcategoria do item
5. Unidade              - Unidade de medida (PC, KG, MT, etc)
6. QuantidadeComprada   - Quantidade adquirida
7. QuantidadePendenteEntrega - Quantidade ainda não entregue
8. ValorTotalComprado   - Valor total pago pelo item
9. ValorTotalPedenteEntrega - Valor pendente de entrega
10. Numero_servico      - Código da OS
11. CodigoOS            - Código da OS (não precisa utilizar este, no final 1128/002 e 1128/003 é o mesmo projeto.)
12. OrdemCompra         - Número da ordem de compra
13. Fornecedor          - Nome do fornecedor
14. CodigoInterno       - Código interno do item
```

**Métricas Principais**:
- Total de OSs: 6.842
- Valor Total: R$ 19.881.536,75
- Ticket Médio/OS: R$ 2.905,81
- Famílias de Produtos: 51

---


## Estrutura do Projeto

```
cmv-hub/
├── data/
│   ├── raw/                          # Arquivos originais (XLS)
│   └── processed/
│       └── cmv_data.csv              # Base processada
├── src/
│   ├── __init__.py
│   ├── backend/
│   │   └── dashboard_cmv_streamlit.py
│   └── utils/
│       ├── __init__.py
│       ├── data_processing.py        # Funções de carga de dados
│       └── analysis.py               # Funções de análise
├── docs/
│   └── CLAUDE.md                     # Este arquivo
├── tests/
│   └── __init__.py
├── README.md
├── requirements.txt
├── run.bat                           # Script de execução Windows
└── venv/
```

---

## Como Executar

**Opção 1 - Script (Windows):**
```bash
run.bat
```

**Opção 2 - Comando direto:**
```bash
streamlit run src/backend/dashboard_cmv_streamlit.py
```

**Dependências:**
```bash
pip install -r requirements.txt
```

---

## Dashboard Streamlit

**Tecnologia**: Python + Streamlit + Plotly

**Features**:
- Análise estatística por OS
- Gráficos interativos com Plotly
- Performance otimizada com cache
- Tabelas ordenáveis e filtráveis
- Export de fichas técnicas customizadas

---

## Módulos

### `src/utils/data_processing.py`
- `load_data(csv_path)` - Carrega e processa CSV

### `src/utils/analysis.py`
- `analyze_os(df)` - Agrega dados por OS
- `get_os_details(df, codigo_os)` - Retorna análise detalhada
- `export_ficha_tecnica(os_details, codigo_os)` - Gera ficha técnica

---



---

## Análises Importantes

### Top 5 OSs por Valor
```
1. OS 1128/002: R$ 1.247.647,77 (13 itens)
2. OS 1058/004: R$ 999.324,44 (294 itens)
3. OS 1128/003: R$ 763.088,29 (145 itens)
4. OS 1058/003: R$ 761.975,20 (75 itens)
5. OS 1058/001: R$ 675.144,92 (431 itens)
```

### Top 5 Famílias por Valor
```
1. MATERIAIS ELETROELETRONICOS: R$ 5.691.654,84 (28.63%)
2. SERVIÇO EXTERNOS: R$ 2.750.302,92 (13.83%)
3. PNEUMATICA: R$ 2.221.261,07 (11.17%)
4. MECANICO: R$ 2.034.029,61 (10.23%)
5. ESTEIRA/TRANSPORTADORES: R$ 1.043.207,09 (5.25%)
```

### Distribuição por Faixa de Valor
```
< R$ 10k:        6.629 OSs (96.89%)
R$ 10k-50k:        143 OSs (2.09%)
R$ 50k-100k:        36 OSs (0.53%)
R$ 100k-200k:       14 OSs (0.20%)
R$ 200k-500k:       12 OSs (0.18%)
> R$ 500k:           5 OSs (0.07%)
```

### Top Fornecedores
```
1. OMRON: R$ 2.198.537,19 (11.06%)
2. FESTO: R$ 1.906.349,55 (9.59%)
3. FLEXLINK: R$ 645.143,14 (3.24%)
```

### Combinações Frequentes de Famílias
```
- Material Específico + Serviço Externos: 1.686 OSs
- Ferragens + Mecânico: 173 OSs
- Ferragens + Lineares: 135 OSs
```

---

## Tarefas e Melhorias Futuras



### Fase 2: Categorização (Em Andamento)
- [ ] Analisar Top 20 OSs com time técnico
- [ ] Definir 5-7 "tipos padrão" de solução
- [ ] Criar campo "Tipo de Solução" no banco
- [ ] Documentar padrões de composição por tipo

### Fase 3: Inteligência (Planejado)
- [ ] Algoritmo de similaridade entre OSs
- [ ] Sugestão automática de categoria para nova OS
- [ ] Análise de margem por tipo de solução
- [ ] Previsão de custo baseada em histórico

### Fase 4: Integração (Futuro)
- [ ] API REST para consulta de dados
- [ ] Integração com sistema de orçamentos
- [ ] Dashboard em produção (Next.js/React)
- [ ] Sistema de precificação automatizada

---


```python
# TODO: Adicionar clustering de OSs similares
# Usar scikit-learn para agrupar por composição

# TODO: Implementar análise temporal
# Se houver dados de data, mostrar evolução de custos

# TODO: Criar dashboard de fornecedores
# Análise profunda por fornecedor (preços, prazos, etc)

# TODO: Export para Excel com formatação
# Atualmente só TXT, seria útil XLSX formatado
```

### Qualidade de Dados
```python
# TODO: Validar e limpar dados de fornecedores
# Alguns fornecedores têm nomes duplicados (OMRON vs OMRON LTDA)

# TODO: Normalizar famílias
# 51 famílias parece muito, pode ter redundância

# TODO: Tratar valores pendentes
# Analisar impacto de QuantidadePendenteEntrega
```

---

## Como Trabalhar com Claude Code

### Comandos Úteis para Claude

**Análise de Dados**:
```
"Analise a OS 1128/002 e me mostre composição detalhada"
"Compare as OSs 1058/001 e 1058/004, quais as diferenças?"
"Liste todos os fornecedores da família PNEUMATICA"
```

**Desenvolvimento**:
```
"Adicione um filtro de faixa de valor no dashboard HTML"
"Crie uma função para detectar OSs similares usando K-means"
"Refatore a função analyze_os para incluir análise temporal"
```

**Melhorias de UX**:
```
"Adicione tooltips nos gráficos explicando cada métrica"
"Melhore a responsividade mobile do dashboard"
"Crie um modo de comparação lado a lado de OSs"
```

**Integrações**:
```
"Crie uma API FastAPI para servir dados do CMV"
"Implemente export para Excel com formatação condicional"
"Adicione autenticação JWT no dashboard Streamlit"
```

---

## Glossário de Termos

- **OS (Ordem de Serviço)**: Projeto individual executado pela ARV
- **CMV (Custo de Mercadoria Vendida)**: Todos os custos diretos de um projeto
- **Família**: Categoria principal de um item (ex: PNEUMATICA, MECANICO)
- **Grupo**: Subcategoria dentro de uma família
- **Ticket Médio**: Valor médio gasto por OS (Total / Número de OSs)
- **Ficha Técnica**: Resumo estruturado de uma OS para catalogação

---

## Contatos e Responsáveis

- **Product Owner**: Bruno (Head of Industrial Systems)
- **Stakeholders**: Gestores ARV, Time Técnico, Comercial
- **Objetivo de Negócio**: Reduzir tempo de orçamento em 50% via catalogação

---

## Notas Importantes

1. **Dados Sensíveis**: Base contém informações comerciais confidenciais da ARV
2. **Backup**: Sempre manter cópia do arquivo XLS original
3. **Atualizações**: Para atualizar dados, reprocessar o XLS para CSV
4. **Performance**: Base de 24k linhas é gerenciável, mas considerar otimizações para crescimento

---



---



---

## Licença e Uso

Projeto interno da ARV Systems. Uso restrito a funcionários autorizados.

**Versão**: 2.0
**Última Atualização**: Fevereiro 2026
**Desenvolvedor**: Bruno - Head of Industrial Systems
