#!/bin/bash

# Configuração e Inicialização do Extrator de PDF
# Este script facilita o setup inicial e execução da aplicação

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar dependências
check_dependencies() {
    print_status "Verificando dependências..."
    
    # Verifica Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalado"
        exit 1
    fi
    print_success "Python 3 encontrado"
    
    # Verifica pip
    if ! command -v pip &> /dev/null; then
        print_error "pip não está instalado"
        exit 1
    fi
    print_success "pip encontrado"
    
    # Verifica Docker (opcional)
    if command -v docker &> /dev/null; then
        print_success "Docker encontrado"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker não encontrado (opcional para desenvolvimento local)"
        DOCKER_AVAILABLE=false
    fi
}

# Função para setup do ambiente
setup_environment() {
    print_status "Configurando ambiente..."
    
    # Cria ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        print_status "Criando ambiente virtual..."
        python3 -m venv venv
        print_success "Ambiente virtual criado"
    else
        print_success "Ambiente virtual já existe"
    fi
    
    # Ativa ambiente virtual
    source venv/bin/activate
    print_success "Ambiente virtual ativado"
    
    # Instala dependências
    print_status "Instalando dependências..."
    pip install -r requirements.txt
    print_success "Dependências instaladas"
    
    # Cria diretórios necessários
    mkdir -p uploads results
    print_success "Diretórios criados"
}

# Função para executar testes
run_tests() {
    print_status "Executando testes básicos..."
    
    source venv/bin/activate
    
    # Testa importação dos módulos
    python3 -c "import extrator_pdf; print('✓ Módulo extrator_pdf OK')"
    python3 -c "import app; print('✓ Módulo Flask app OK')"
    
    print_success "Testes básicos concluídos"
}

# Função para iniciar aplicação
start_app() {
    local mode=${1:-dev}
    
    print_status "Iniciando aplicação em modo: $mode"
    
    if [ "$mode" = "docker" ] && [ "$DOCKER_AVAILABLE" = true ]; then
        print_status "Usando Docker..."
        ./deploy.sh dev
    else
        print_status "Usando Python diretamente..."
        source venv/bin/activate
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        python3 app.py
    fi
}

# Função para mostrar informações do sistema
show_info() {
    print_status "Informações do Sistema:"
    echo "  Python: $(python3 --version)"
    echo "  Pip: $(pip --version)"
    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo "  Docker: $(docker --version)"
    fi
    echo "  OS: $(uname -s)"
    echo "  Arquitetura: $(uname -m)"
    echo ""
    
    print_status "Estrutura do Projeto:"
    if command -v tree &> /dev/null; then
        tree -L 2 -I "venv|__pycache__|*.pyc|uploads|results"
    else
        ls -la
    fi
}

# Função para limpar ambiente
clean_environment() {
    print_warning "Limpando ambiente..."
    
    # Para aplicação se estiver rodando
    pkill -f "python.*app.py" || true
    
    # Remove arquivos temporários
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Limpa uploads e results (com confirmação)
    read -p "Deseja limpar arquivos de upload e resultados? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        rm -rf uploads/* results/* 2>/dev/null || true
        print_success "Arquivos de upload e resultados removidos"
    fi
    
    print_success "Limpeza concluída"
}

# Função para mostrar ajuda
show_help() {
    echo "🐍 Extrator de PDF - Script de Configuração"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  setup     - Configura o ambiente (primeira execução)"
    echo "  start     - Inicia a aplicação (desenvolvimento)"
    echo "  docker    - Inicia usando Docker"
    echo "  test      - Executa testes básicos"
    echo "  info      - Mostra informações do sistema"
    echo "  clean     - Limpa arquivos temporários"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 setup     # Primeira configuração"
    echo "  $0 start     # Inicia aplicação"
    echo "  $0 docker    # Inicia com Docker"
    echo ""
}

# Função principal
main() {
    echo "================================================="
    echo "🚀 Extrator de PDF - Setup e Execução"
    echo "================================================="
    echo ""
    
    case ${1:-help} in
        "setup")
            check_dependencies
            setup_environment
            run_tests
            print_success "Setup concluído! Execute '$0 start' para iniciar a aplicação."
            ;;
        "start")
            check_dependencies
            start_app dev
            ;;
        "docker")
            if [ "$DOCKER_AVAILABLE" = true ]; then
                start_app docker
            else
                print_error "Docker não está disponível"
                exit 1
            fi
            ;;
        "test")
            check_dependencies
            run_tests
            ;;
        "info")
            show_info
            ;;
        "clean")
            clean_environment
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Executa função principal
main "$@"
