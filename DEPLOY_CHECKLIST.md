# 📋 Checklist de Deploy - CMV Hub

Use este checklist para garantir que todos os passos foram executados corretamente no deploy da aplicação.

---

## ✅ Pré-Requisitos no Servidor

- [ ] Docker instalado e rodando
- [ ] Docker Compose instalado
- [ ] Docker Swarm inicializado (`docker swarm init`)
- [ ] Traefik configurado como reverse proxy
- [ ] Network externa `network_public` criada
- [ ] DNS configurado: `analise-cmv.arvsystems.cloud` apontando para o servidor
- [ ] Certificado SSL configurado no Traefik (Let's Encrypt)
- [ ] Acesso SSH ao servidor configurado

---

## 📦 Preparação dos Dados

### 1. Criar Volume Docker

```bash
docker volume create data_cmv_analise
```

- [ ] Volume `data_cmv_analise` criado com sucesso

### 2. Popular Volume com Dados Iniciais

**Opção A - Via container temporário (recomendado):**

```bash
docker run --rm \
  -v data_cmv_analise:/data \
  -v $(pwd)/data:/source \
  alpine cp -r /source/* /data/
```

**Opção B - Manualmente após primeiro deploy:**

```bash
# Copiar CSV
docker cp data/processed/cmv_data.csv <container_id>:/app/data/processed/

# O banco SQLite será criado automaticamente
```

- [ ] Arquivo `cmv_data.csv` copiado para o volume
- [ ] Verificado que o arquivo está acessível: `docker run --rm -v data_cmv_analise:/data alpine ls -lh /data/processed/`

---

## 🔨 Build e Deploy

### 3. Clonar/Atualizar Repositório

```bash
cd /caminho/do/deploy
git clone <url-do-repositorio>
# ou
git pull origin main
```

- [ ] Código mais recente no servidor

### 4. Build da Imagem

```bash
docker build -t analise-cmv:latest .
```

- [ ] Build concluído sem erros
- [ ] Imagem `analise-cmv:latest` listada em `docker images`

### 5. Deploy da Stack

```bash
docker stack deploy -c docker-compose.yml analise-cmv
```

Ou use o script automatizado:

```bash
chmod +x deploy.sh
./deploy.sh
```

- [ ] Stack deployed com sucesso
- [ ] Serviço `analise-cmv_analise_cmv` listado em `docker service ls`

---

## 🔍 Verificações Pós-Deploy

### 6. Verificar Status do Serviço

```bash
# Status geral
docker service ls

# Status detalhado
docker service ps analise-cmv_analise_cmv

# Deve mostrar estado "Running"
```

- [ ] Serviço em estado "Running"
- [ ] Nenhum erro nos eventos do serviço

### 7. Verificar Logs

```bash
# Últimos logs
docker service logs --tail 50 analise-cmv_analise_cmv

# Logs em tempo real
docker service logs -f analise-cmv_analise_cmv
```

- [ ] Logs mostram inicialização bem-sucedida
- [ ] Mensagem "You can now view your Streamlit app in your browser"
- [ ] Nenhum erro crítico nos logs

### 8. Verificar Healthcheck

```bash
# Inspecionar container
docker ps | grep analise-cmv

# Ver healthcheck status
docker inspect <container_id> | grep -A 10 Health
```

- [ ] Healthcheck status: "healthy"

### 9. Testar Acesso Local

```bash
# Testar endpoint de health
curl http://localhost:8501/_stcore/health

# Deve retornar 200 OK
```

- [ ] Endpoint de health respondendo
- [ ] Código de status 200

### 10. Testar Acesso via Domínio

```bash
# Testar HTTPS
curl -I https://analise-cmv.arvsystems.cloud

# Deve retornar 200 OK e certificado SSL válido
```

- [ ] Site acessível via HTTPS
- [ ] Certificado SSL válido
- [ ] Redirecionamento HTTP → HTTPS funcionando

### 11. Testar Funcionalidades da Aplicação

Acesse via navegador: `https://analise-cmv.arvsystems.cloud`

- [ ] Página inicial carrega corretamente
- [ ] Métricas exibem dados corretos
- [ ] Página de Categorização funciona
- [ ] Seleção de OS carrega dados
- [ ] Filtros funcionam corretamente
- [ ] Gráficos são renderizados
- [ ] Exportação Excel funciona
- [ ] Página de Catálogo funciona
- [ ] Upload de imagens funciona
- [ ] Categorização salva no banco

---

## 💾 Verificar Persistência de Dados

### 12. Testar Persistência

```bash
# 1. Categorizar uma OS via interface
# 2. Reiniciar serviço
docker service update --force analise-cmv_analise_cmv

# 3. Verificar se categorização permanece
```

- [ ] Dados persistem após reinicialização
- [ ] Imagens carregadas permanecem disponíveis
- [ ] Banco SQLite mantém dados

---

## 🔄 Atualização Futura

### Passos para Atualizar a Aplicação

```bash
# 1. Atualizar código
git pull

# 2. Rebuild
docker build -t analise-cmv:latest .

# 3. Atualizar serviço (rolling update)
docker service update --image analise-cmv:latest analise-cmv_analise_cmv

# 4. Verificar
docker service logs --tail 50 analise-cmv_analise_cmv
```

---

## 📊 Monitoramento Contínuo

### Comandos Úteis

```bash
# Ver status
docker service ps analise-cmv_analise_cmv

# Ver logs
docker service logs -f analise-cmv_analise_cmv

# Ver recursos
docker stats

# Ver volume
docker volume inspect data_cmv_analise

# Backup
docker run --rm -v data_cmv_analise:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/cmv_backup_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🚨 Troubleshooting

### Se algo der errado:

1. **Ver logs detalhados:**
   ```bash
   docker service logs --tail 200 analise-cmv_analise_cmv
   ```

2. **Verificar eventos:**
   ```bash
   docker service ps analise-cmv_analise_cmv --no-trunc
   ```

3. **Acessar container:**
   ```bash
   docker exec -it <container_id> /bin/sh
   ```

4. **Remover e redeploy:**
   ```bash
   docker stack rm analise-cmv
   # Aguardar 30 segundos
   docker stack deploy -c docker-compose.yml analise-cmv
   ```

---

## ✅ Deploy Concluído

- [ ] Todos os itens deste checklist foram verificados
- [ ] Aplicação acessível e funcionando
- [ ] Dados persistindo corretamente
- [ ] Logs não mostram erros críticos
- [ ] Equipe notificada sobre o deploy

**Data do Deploy:** ___/___/______  
**Responsável:** ___________________  
**Versão Deployed:** _______________

---

**🎉 Parabéns! O CMV Hub está no ar!**

Acesso: https://analise-cmv.arvsystems.cloud
