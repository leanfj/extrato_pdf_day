#!/bin/bash

# 🚀 Script de Inicialização do Extrator PDF
# Este script prepara o ambiente para desenvolvimento

set -e

echo "🚀 Inicializando Extrator PDF..."

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📦 Criando diretórios necessários...${NC}"
mkdir -p uploads results logs data

echo -e "${BLUE}🔧 Configurando permissões...${NC}"
chmod 755 uploads results

echo -e "${BLUE}📄 Verificando arquivo .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Copiando .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Edite o arquivo .env com suas configurações!${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
fi

echo -e "${BLUE}🐍 Verificando ambiente virtual...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}📚 Ativando ambiente virtual e instalando dependências...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Projeto inicializado com sucesso!${NC}"
echo -e "${BLUE}🚀 Para executar:${NC}"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo -e "${BLUE}🐳 Para usar Docker:${NC}"
echo "   docker-compose up -d"