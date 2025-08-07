#!/bin/bash

# 🚀 DEPLOY AUTOMÁTICO PARA CASAOS
# Servidor: 192.168.0.9
# Data: 06 de Agosto de 2025

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções para log colorido
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════╗"
echo "║     🚀 DEPLOY EXTRATOR PDF - CASAOS    ║"
echo "║        Servidor: 192.168.0.9          ║"
echo "║        Data: $(date +%d/%m/%Y)              ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Variáveis
SERVER_IP="192.168.0.9"
APP_NAME="extrator-pdf"
APP_PORT="5000"
DOCKER_IMAGE_NAME="extrator-pdf-app"

# Verifica se está no diretório correto
if [ ! -f "../app.py" ]; then
    log_error "app.py não encontrado. Execute este script do diretório deploy/ dentro da aplicação."
    exit 1
fi

# Vai para o diretório raiz do projeto
cd ..

log_step "1/8 Verificando pré-requisitos..."

# Verifica Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi

# Verifica Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_warning "Docker Compose não encontrado. Tentando instalar..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

log_success "Pré-requisitos verificados!"

log_step "2/8 Criando estrutura de diretórios..."

# Cria diretórios necessários com permissões adequadas
mkdir -p uploads results data logs
chmod 777 uploads results data logs

# Tenta configurar ownership, mas não falha se não conseguir
if command -v chown >/dev/null 2>&1; then
    chown -R $USER:$USER uploads results data logs 2>/dev/null || log_warning "Não foi possível definir ownership dos diretórios (normal em alguns ambientes)"
fi

log_success "Diretórios criados!"

log_step "3/8 Configurando variáveis de ambiente..."

# Cria arquivo .env se não existir
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Configurações de produção
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Configurações de rede
HOST=0.0.0.0
PORT=5000

# Configurações de upload
MAX_CONTENT_LENGTH=50MB
UPLOAD_FOLDER=uploads
RESULTS_FOLDER=results

# Configurações de segurança
ALLOWED_EXTENSIONS=pdf

# Timezone
TZ=America/Sao_Paulo
EOF
    log_success "Arquivo .env criado!"
else
    log_info "Arquivo .env já existe."
fi

log_step "4/8 Parando containers existentes..."

# Para containers existentes
if docker ps -a | grep -q $DOCKER_IMAGE_NAME; then
    docker-compose down
    log_success "Containers existentes parados!"
else
    log_info "Nenhum container existente encontrado."
fi

log_step "5/8 Limpando imagens antigas..."

# Remove imagens antigas (opcional)
docker image prune -f > /dev/null 2>&1
log_success "Imagens antigas removidas!"

log_step "6/8 Construindo e iniciando aplicação..."

# Constrói e inicia os containers
docker-compose up --build -d

if [ $? -eq 0 ]; then
    log_success "Containers iniciados com sucesso!"
else
    log_error "Falha ao iniciar containers!"
    docker-compose logs
    exit 1
fi

log_step "7/8 Aguardando aplicação inicializar..."

# Aguarda containers iniciarem
sleep 15

# Verifica se containers estão rodando
if docker-compose ps | grep -q "Up"; then
    log_success "Containers rodando!"
else
    log_error "Containers não estão rodando!"
    docker-compose logs
    exit 1
fi

log_step "8/8 Testando aplicação..."

# Função para testar conectividade
test_connectivity() {
    local url=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s $url > /dev/null 2>&1; then
            return 0
        fi
        log_info "Tentativa $attempt/$max_attempts: aguardando aplicação..."
        sleep 3
        attempt=$((attempt + 1))
    done
    return 1
}

# Testa aplicação local
if test_connectivity "http://localhost:$APP_PORT"; then
    log_success "✅ Aplicação local funcionando!"
else
    log_error "❌ Falha ao acessar aplicação local"
    log_info "Logs da aplicação:"
    docker-compose logs --tail=20 extrator-pdf
fi

# Testa aplicação na rede
if test_connectivity "http://$SERVER_IP:$APP_PORT"; then
    log_success "✅ Aplicação acessível na rede!"
else
    log_warning "⚠️  Aplicação pode não estar acessível na rede"
    log_info "Verifique firewall e configurações de rede"
fi

# Verifica health check
log_info "Verificando health check..."
sleep 5
if docker inspect extrator-pdf-app | grep -q '"Health"'; then
    HEALTH_STATUS=$(docker inspect extrator-pdf-app | grep -A 5 '"Health"' | grep '"Status"' | cut -d'"' -f4)
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        log_success "✅ Health check: HEALTHY"
    else
        log_warning "⚠️  Health check: $HEALTH_STATUS"
    fi
fi

# Mostra informações finais
echo -e "\n${CYAN}╔════════════════════════════════════════╗"
echo "║           🎉 DEPLOY CONCLUÍDO!         ║"
echo "╚════════════════════════════════════════╝${NC}\n"

log_success "🌐 Acesso Local: http://localhost:$APP_PORT"
log_success "🌐 Acesso Rede: http://$SERVER_IP:$APP_PORT"
log_success "📊 Dashboard: http://$SERVER_IP:$APP_PORT/dashboard"
log_success "❤️  Health Check: http://$SERVER_IP:$APP_PORT/health"

echo -e "\n${YELLOW}📋 COMANDOS ÚTEIS:${NC}"
echo "  🔍 Ver logs:           docker-compose logs -f"
echo "  🔄 Reiniciar:          docker-compose restart"
echo "  🛑 Parar:              docker-compose down"
echo "  📊 Status:             docker-compose ps"
echo "  🧹 Limpar:             docker system prune -f"

echo -e "\n${YELLOW}📁 DIRETÓRIOS:${NC}"
echo "  📤 Uploads:            $(pwd)/uploads"
echo "  📥 Resultados:         $(pwd)/results"
echo "  💾 Dados:              $(pwd)/data"
echo "  📜 Logs:               docker-compose logs"

# Pergunta se quer ver logs em tempo real
echo -e "\n${PURPLE}Deseja ver os logs em tempo real? (y/n):${NC} \c"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Mostrando logs em tempo real (Ctrl+C para sair)...${NC}"
    docker-compose logs -f
fi

log_success "Deploy concluído com sucesso! 🚀"
