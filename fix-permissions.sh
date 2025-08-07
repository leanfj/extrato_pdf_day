#!/bin/bash

# 🔧 Script de Correção de Permissões para CasaOS
# Este script corrige problemas de permissão nos diretórios

set -e

echo "🔧 Corrigindo permissões para CasaOS..."

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se está no diretório correto
if [ ! -f "app.py" ]; then
    log_error "app.py não encontrado. Execute este script no diretório da aplicação."
    exit 1
fi

log_info "Parando containers existentes..."
docker-compose down || true

log_info "Criando diretórios com permissões corretas..."
mkdir -p uploads results data logs

log_info "Configurando permissões dos diretórios..."
chmod 777 uploads results data logs
sudo chown -R $USER:$USER uploads results data logs 2>/dev/null || true

log_info "Configurando permissões recursivas..."
find uploads results data logs -type d -exec chmod 755 {} \; 2>/dev/null || true
find uploads results data logs -type f -exec chmod 644 {} \; 2>/dev/null || true

log_info "Rebuilding container com permissões corrigidas..."
docker-compose build --no-cache

log_info "Iniciando aplicação..."
docker-compose up -d

log_success "Correção de permissões concluída!"

log_info "Testando aplicação..."
sleep 10

if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    log_success "✅ Aplicação funcionando corretamente!"
    log_success "🌐 Acesso: http://localhost:5000"
else
    log_warning "⚠️  Aplicação pode estar iniciando. Aguarde alguns segundos."
fi

echo -e "\n${YELLOW}Se ainda houver problemas de permissão, execute:${NC}"
echo "sudo chmod -R 777 uploads results data logs"
echo "docker-compose restart"
