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



#### Instalação

```bash
# 1. Instalar dependências
pip install streamlit pandas plotly openpyxl

# 2. Colocar os arquivos na mesma pasta
- dashboard_cmv_streamlit.py
- cmv_data.csv

# 3. Executar o dashboard
streamlit run dashboard_cmv_streamlit.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`



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
