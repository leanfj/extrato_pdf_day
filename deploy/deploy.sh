#!/bin/bash

# Script de Deploy da Aplicação Web Extrator de PDF
# Uso: ./deploy.sh [dev|prod]

set -e

# Configurações
APP_NAME="extrator-pdf"
DOCKER_IMAGE="$APP_NAME:latest"
ENV=${1:-dev}

echo "🚀 Iniciando deploy do Extrator de PDF - Ambiente: $ENV"

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker não está rodando. Inicie o Docker e tente novamente."
        exit 1
    fi
    echo "✅ Docker está rodando"
}

# Função para limpar containers antigos
cleanup() {
    echo "🧹 Limpando containers antigos..."
    docker-compose down --remove-orphans 2>/dev/null || true
    docker container prune -f 2>/dev/null || true
    echo "✅ Limpeza concluída"
}

# Função para construir a imagem
build_image() {
    echo "🔨 Construindo imagem Docker..."
    docker build -t $DOCKER_IMAGE . --no-cache
    echo "✅ Imagem construída com sucesso"
}

# Função para fazer deploy em desenvolvimento
deploy_dev() {
    echo "🔧 Deploy em desenvolvimento..."
    
    # Para o ambiente de desenvolvimento sem nginx
    docker-compose up --build -d web
    
    echo "✅ Deploy de desenvolvimento concluído"
    echo "🌐 Aplicação disponível em: http://localhost:5000"
}

# Função para fazer deploy em produção
deploy_prod() {
    echo "🚀 Deploy em produção..."
    
    # Para o ambiente de produção com nginx
    docker-compose --profile production up --build -d
    
    echo "✅ Deploy de produção concluído"
    echo "🌐 Aplicação disponível em: http://localhost"
    echo "🌐 Aplicação direta (sem nginx): http://localhost:5000"
}

# Função para verificar saúde da aplicação
health_check() {
    echo "🏥 Verificando saúde da aplicação..."
    
    # Aguarda alguns segundos para a aplicação iniciar
    sleep 10
    
    # Verifica se a aplicação está respondendo
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Aplicação está saudável"
        return 0
    else
        echo "❌ Aplicação não está respondendo"
        echo "📋 Logs do container:"
        docker-compose logs web --tail=20
        return 1
    fi
}

# Função para exibir logs
show_logs() {
    echo "📋 Exibindo logs da aplicação..."
    docker-compose logs -f web
}

# Função para exibir status
show_status() {
    echo "📊 Status dos containers:"
    docker-compose ps
    
    echo ""
    echo "💾 Uso de disco:"
    docker system df
    
    echo ""
    echo "🔍 Containers em execução:"
    docker ps --filter "name=$APP_NAME"
}

# Função principal
main() {
    echo "============================================"
    echo "🐳 Deploy Extrator de PDF"
    echo "============================================"
    
    check_docker
    cleanup
    build_image
    
    case $ENV in
        "dev")
            deploy_dev
            ;;
        "prod")
            deploy_prod
            ;;
        *)
            echo "❌ Ambiente inválido. Use 'dev' ou 'prod'"
            exit 1
            ;;
    esac
    
    health_check
    show_status
    
    echo ""
    echo "============================================"
    echo "✅ Deploy concluído com sucesso!"
    echo "============================================"
    echo ""
    echo "📖 Comandos úteis:"
    echo "  Ver logs:        docker-compose logs -f web"
    echo "  Parar app:       docker-compose down"
    echo "  Status:          docker-compose ps"
    echo "  Rebuild:         docker-compose up --build -d"
    echo ""
    
    # Pergunta se quer ver logs
    read -p "Deseja ver os logs em tempo real? (y/N): " show_logs_choice
    if [[ $show_logs_choice =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Tratamento de sinais
trap 'echo ""; echo "❌ Deploy interrompido"; exit 1' INT TERM

# Executa função principal
main
