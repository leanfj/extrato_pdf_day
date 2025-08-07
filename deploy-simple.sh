#!/bin/bash

# 🚀 DEPLOY SIMPLIFICADO PARA CASAOS
# Versão robusta que evita problemas de permissão

set -e

echo "🚀 Deploy Simplificado - CasaOS..."

# Cores básicas
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERRO]${NC} $1"; }

# Verifica se está no local correto
if [ ! -f "app.py" ]; then
    log_error "Execute este script no diretório raiz do projeto (onde está o app.py)"
    exit 1
fi

log_info "1/5 Criando diretórios..."
mkdir -p uploads results data logs
chmod 777 uploads results data logs
log_success "Diretórios criados com permissões abertas"

log_info "2/5 Parando containers antigos..."
docker-compose down 2>/dev/null || log_info "Nenhum container para parar"

log_info "3/5 Limpando cache Docker..."
docker system prune -f >/dev/null 2>&1 || true

log_info "4/5 Construindo e iniciando..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    log_success "Container iniciado!"
else
    log_error "Falha no build/start"
    docker-compose logs
    exit 1
fi

log_info "5/5 Testando aplicação..."
sleep 10

# Teste simples
if curl -f -s http://localhost:5000/health >/dev/null 2>&1; then
    log_success "✅ Aplicação funcionando!"
    echo ""
    echo "🌐 Acesso: http://localhost:5000"
    echo "❤️  Health: http://localhost:5000/health"
    echo ""
    echo "📋 Comandos úteis:"
    echo "  docker-compose logs -f    # Ver logs"
    echo "  docker-compose restart    # Reiniciar"
    echo "  docker-compose down       # Parar"
else
    log_warning "Aplicação pode estar iniciando..."
    echo "Verifique os logs: docker-compose logs -f"
fi

log_success "Deploy concluído! 🚀"
