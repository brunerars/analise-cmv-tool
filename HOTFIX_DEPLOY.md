# 🔥 Hotfix - Atualização Urgente v2.0.1

## 🐛 Bugs Corrigidos

### 1. AttributeError em Catálogo
- **Erro**: `'float' object has no attribute 'replace'`
- **Status**: ✅ CORRIGIDO

### 2. Path de dados no Docker
- **Erro**: `Arquivo de dados não encontrado em: /app/data/processed/cmv_data.csv`
- **Status**: ✅ CORRIGIDO

---

## 🚀 Como Aplicar o Hotfix

### Método 1: Atualização Rápida (Recomendado)

```bash
# 1. No servidor, atualizar código
cd /caminho/do/projeto
git pull

# 2. Rebuild da imagem
docker build -t analise-cmv:latest .

# 3. Atualizar serviço (rolling update - zero downtime)
docker service update --image analise-cmv:latest analise-cmv_analise_cmv

# 4. Verificar logs
docker service logs --tail 50 -f analise-cmv_analise_cmv
```

### Método 2: Redeploy Completo

```bash
# 1. Atualizar código
cd /caminho/do/projeto
git pull

# 2. Remover stack antiga
docker stack rm analise-cmv

# 3. Aguardar 30 segundos
sleep 30

# 4. Rebuild
docker build -t analise-cmv:latest .

# 5. Deploy novamente
docker stack deploy -c docker-compose.yml analise-cmv
```

### Método 3: Script Automatizado

```bash
# Usar o script de deploy
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Verificação Pós-Atualização

### 1. Verificar se o serviço está rodando

```bash
docker service ps analise-cmv_analise_cmv
```

Deve mostrar estado: **Running**

### 2. Verificar logs

```bash
docker service logs --tail 20 analise-cmv_analise_cmv
```

Deve mostrar:
- ✅ "You can now view your Streamlit app in your browser"
- ✅ Sem erros de "FileNotFoundError"
- ✅ Sem erros de "AttributeError"

### 3. Testar no navegador

Acesse: `https://analise-cmv.arvsystems.cloud`

**Testes:**
1. ✅ Página inicial carrega
2. ✅ Navegue para "Catálogo"
3. ✅ Clique em "Ver Detalhes" em uma OS
4. ✅ Verifique se o total aparece sem erro: `📦 Total: **X itens** | 💰 Valor: **R$ X.XXX.XXX,XX**`

---

## 🔍 O Que Foi Alterado

### Arquivos Modificados

1. **src/backend/pages/2_Catalogo.py**
   - Linha 362: Corrigido cálculo de total de valores
   - Removido lambda desnecessário com `.replace()`

2. **src/utils/data_processing.py**
   - Adicionada função `get_data_path()` para detecção automática de ambiente

3. **src/utils/database.py**
   - Adicionada função `get_data_dir()` para paths dinâmicos

4. **src/backend/app.py**
   - Atualizado para usar `get_data_path()`

5. **src/backend/pages/1_Categorizacao.py**
   - Atualizado para usar `get_data_path()`

### Como Funciona Agora

**Ambiente Local (desenvolvimento):**
```
ROOT_DIR/data/processed/cmv_data.csv
ROOT_DIR/data/cmv_catalog.db
ROOT_DIR/data/images/
```

**Ambiente Docker (produção):**
```
/app/data/processed/cmv_data.csv
/app/data/cmv_catalog.db
/app/data/images/
```

O código **detecta automaticamente** o ambiente e usa o path correto!

---

## 📊 Impacto

- ✅ Zero downtime com rolling update
- ✅ Dados persistidos mantidos intactos
- ✅ Categorização e imagens preservadas
- ✅ Funciona em dev e produção

---

## 🆘 Troubleshooting

### Problema: Serviço não inicia após update

```bash
# Ver logs detalhados
docker service logs --tail 100 analise-cmv_analise_cmv

# Forçar restart
docker service update --force analise-cmv_analise_cmv
```

### Problema: Ainda mostra erro de arquivo não encontrado

```bash
# Verificar se CSV está no volume
docker exec $(docker ps -q -f name=analise-cmv) ls -lh /app/data/processed/

# Se não estiver, copiar novamente
docker run --rm -v data_cmv_analise:/data -v $(pwd)/data:/source \
  alpine cp /source/processed/cmv_data.csv /data/processed/
```

### Problema: Erro persiste

```bash
# Redeploy completo
docker stack rm analise-cmv
sleep 30
docker build -t analise-cmv:latest .
docker stack deploy -c docker-compose.yml analise-cmv
```

---

## 📝 Checklist de Atualização

- [ ] Código atualizado (`git pull`)
- [ ] Imagem rebuilt (`docker build`)
- [ ] Serviço atualizado (`docker service update`)
- [ ] Logs verificados (sem erros)
- [ ] Site acessível via HTTPS
- [ ] Página inicial carrega
- [ ] Catálogo funciona
- [ ] Detalhes de OS exibem total sem erro
- [ ] Categorização funciona
- [ ] Upload de imagens funciona

---

**Versão**: 2.0.1  
**Data**: 17/02/2026  
**Tipo**: Hotfix Crítico  
**Prioridade**: Alta
