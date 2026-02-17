# 📝 Changelog - CMV Hub

Registro de todas as mudanças significativas no projeto.

---

## [2.0.0] - 2026-02-17

### ✨ Melhorias de UX/Navegabilidade

#### Configuração Geral
- **Adicionado** arquivo `.streamlit/config.toml` com tema customizado ARV (preto, vermelho, branco)
- **Adicionado** configurações de título de página, layout wide por padrão
- **Atualizado** `.streamlit/pages.toml` com nomes mais descritivos e ícones

#### Página Inicial (`app.py`)
- **Melhorado** título e descrição da aplicação
- **Adicionado** 4 métricas principais com tooltips explicativos
- **Adicionado** métrica de "Progresso" de categorização
- **Reformulado** cards de navegação com descrições detalhadas
- **Adicionado** seção "Como usar o sistema" expansível
- **Melhorado** sidebar com informações da base de dados
- **Adicionado** dica de valor no rodapé

#### Página de Categorização (`1_Categorizacao.py`)
- **Adicionado** configuração de título de página
- **Melhorado** cabeçalho com descrição e caption
- **Adicionado** tooltips em todos os filtros e métricas
- **Melhorado** organização visual dos filtros com ícones
- **Adicionado** configuração de colunas no dataframe
- **Adicionado** indicadores de representatividade (percentual do total)
- **Melhorado** labels dos campos de categorização
- **Adicionado** animação de balões ao salvar categorização
- **Melhorado** feedback visual com ícones (✅, ❌, ⚠️, 💡)

#### Página de Catálogo (`2_Catalogo.py`)
- **Adicionado** configuração de título de página
- **Melhorado** cabeçalho e descrições
- **Adicionado** tooltips nos filtros da sidebar
- **Melhorado** visualização dos cards com labels de complexidade expandidos
- **Adicionado** ícones nos cards (📋, 💰, 📦)
- **Melhorado** modal de detalhes com seções bem definidas
- **Adicionado** configuração de colunas no dataframe de itens
- **Melhorado** gerenciamento de fotos com feedback visual aprimorado
- **Adicionado** confirmação de exclusão (dois cliques)
- **Melhorado** organização de informações no modal

### 🐳 Deploy e Infraestrutura

#### Docker
- **Criado** `Dockerfile` otimizado para produção
  - Base: Python 3.11-slim
  - Healthcheck integrado
  - Configurações de segurança
  - Estrutura de volumes
  
- **Criado** `docker-compose.yml` para Docker Swarm
  - Integração com Traefik
  - SSL automático via Let's Encrypt
  - Domínio: `analise-cmv.arvsystems.cloud`
  - Volume externo: `data_cmv_analise`
  - Network externa: `network_public`
  - Rolling updates configurados
  - Restart policy configurado

- **Criado** `.dockerignore` para otimizar build
- **Criado** `.gitignore` para proteger dados sensíveis

#### Scripts e Automação
- **Criado** `deploy.sh` - Script automatizado de deploy
  - Verificações de pré-requisitos
  - Criação automática de volume e network
  - Build e deploy automatizados
  - Logs e status pós-deploy

#### Documentação
- **Atualizado** `README.md` com seção completa de deploy
  - Instruções detalhadas de deploy Docker
  - Comandos de manutenção de dados
  - Troubleshooting
  - Estrutura do projeto
  
- **Criado** `DEPLOY_CHECKLIST.md` - Checklist passo a passo
- **Criado** `QUICKSTART.md` - Guia rápido de início
- **Criado** `.env.example` - Template de variáveis de ambiente
- **Criado** `CHANGELOG.md` - Este arquivo

### 🔧 Melhorias Técnicas
- **Adicionado** `requests` ao requirements.txt para healthcheck
- **Criado** estrutura de pastas para volumes Docker
- **Adicionado** `.gitkeep` em `data/images/` para manter estrutura

### 📊 Estatísticas
- Total de arquivos criados: 10
- Total de arquivos modificados: 5
- Linhas de código adicionadas: ~1500
- Linhas de documentação adicionadas: ~800

---

## [1.0.0] - Data Anterior

### 🎉 Release Inicial
- Sistema básico de análise de CMV
- Dashboard Streamlit funcional
- Categorização de OS
- Exportação para Excel
- Banco de dados SQLite
- Upload de imagens

---

## Formato

O formato deste changelog é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

### Tipos de Mudanças

- **Adicionado** para novas funcionalidades
- **Modificado** para mudanças em funcionalidades existentes
- **Descontinuado** para funcionalidades que serão removidas
- **Removido** para funcionalidades removidas
- **Corrigido** para correções de bugs
- **Segurança** para vulnerabilidades corrigidas
