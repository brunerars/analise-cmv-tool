#!/bin/bash

# ===========================================
# Deploy Script para CMV Hub - ARV Systems
# ===========================================
# 
# Este script automatiza o deploy da aplicação
# no Docker Swarm com Traefik
#
# Uso: ./deploy.sh
# ===========================================

set -e  # Exit on error

echo "🚀 Iniciando deploy do CMV Hub..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está em um Docker Swarm
if ! docker info | grep -q "Swarm: active"; then
    echo -e "${RED}❌ Erro: Docker Swarm não está ativo!${NC}"
    echo "Inicialize o Swarm com: docker swarm init"
    exit 1
fi

# Verificar se a network existe
if ! docker network ls | grep -q "network_public"; then
    echo -e "${YELLOW}⚠️  Network 'network_public' não encontrada.${NC}"
    read -p "Deseja criar a network? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker network create --driver overlay network_public
        echo -e "${GREEN}✅ Network criada com sucesso!${NC}"
    else
        echo -e "${RED}❌ Deploy cancelado. Network necessária.${NC}"
        exit 1
    fi
fi

# Verificar se o volume existe
if ! docker volume ls | grep -q "data_cmv_analise"; then
    echo -e "${YELLOW}⚠️  Volume 'data_cmv_analise' não encontrado.${NC}"
    read -p "Deseja criar o volume? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume create data_cmv_analise
        echo -e "${GREEN}✅ Volume criado com sucesso!${NC}"
        echo -e "${YELLOW}⚠️  ATENÇÃO: Você precisa popular o volume com os dados!${NC}"
        echo "Execute: docker run --rm -v data_cmv_analise:/data -v \$(pwd)/data:/source alpine cp -r /source/* /data/"
        read -p "Pressione Enter para continuar após popular os dados..."
    else
        echo -e "${RED}❌ Deploy cancelado. Volume necessário.${NC}"
        exit 1
    fi
fi

# Build da imagem
echo ""
echo "🔨 Construindo imagem Docker..."
docker build -t analise-cmv:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no build da imagem!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Imagem construída com sucesso!${NC}"

# Deploy da stack
echo ""
echo "📦 Fazendo deploy da stack no Swarm..."
docker stack deploy -c docker-compose.yml analise-cmv

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no deploy da stack!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Stack deployed com sucesso!${NC}"

# Aguardar alguns segundos
echo ""
echo "⏳ Aguardando serviço inicializar..."
sleep 10

# Verificar status
echo ""
echo "📊 Status do serviço:"
docker service ps analise-cmv_analise_cmv --no-trunc

echo ""
echo "📋 Logs recentes:"
docker service logs --tail 20 analise-cmv_analise_cmv

echo ""
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "🌐 Acesse a aplicação em: https://analise-cmv.arvsystems.cloud"
echo ""
echo "Comandos úteis:"
echo "  - Ver logs: docker service logs -f analise-cmv_analise_cmv"
echo "  - Ver status: docker service ps analise-cmv_analise_cmv"
echo "  - Atualizar: docker service update --force analise-cmv_analise_cmv"
echo "  - Remover: docker stack rm analise-cmv"
echo ""
