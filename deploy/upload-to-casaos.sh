#!/bin/bash

# 📤 SCRIPT DE UPLOAD PARA CASAOS
# Envia a aplicação para o servidor CasaOS e executa o deploy

SERVER_IP="192.168.0.9"
SERVER_USER="leandro"  # ou seu usuário no CasaOS
APP_NAME="extrator-pdf"

echo "🚀 UPLOAD E DEPLOY PARA CASAOS"
echo "================================"
echo "Servidor: $SERVER_IP"
echo "Usuário: $SERVER_USER"
echo "App: $APP_NAME"
echo ""

# Verifica conectividade
echo "🔍 Testando conectividade..."
if ping -c 1 $SERVER_IP > /dev/null 2>&1; then
    echo "✅ Servidor acessível!"
else
    echo "❌ Servidor não acessível. Verifique a rede."
    exit 1
fi

# Cria arquivo compactado
echo "📦 Criando pacote da aplicação..."
tar -czf extrator-pdf-deploy.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='uploads/*' \
    --exclude='results/*' \
    --exclude='venv' \
    --exclude='*.log' \
    .

echo "✅ Pacote criado: extrator-pdf-deploy.tar.gz"

# Upload para servidor
echo "📤 Enviando para servidor..."
scp extrator-pdf-deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

if [ $? -eq 0 ]; then
    echo "✅ Upload concluído!"
else
    echo "❌ Falha no upload. Verifique SSH."
    exit 1
fi

# Remove arquivo local
rm extrator-pdf-deploy.tar.gz

# Executa deploy no servidor
echo "🚀 Executando deploy no servidor..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    echo "📁 Criando estrutura no CasaOS..."
    
    # Navega para pasta de apps do CasaOS
    cd /DATA/AppData
    
    # Remove instalação anterior se existir
    if [ -d "extrator-pdf" ]; then
        echo "🗑️  Removendo instalação anterior..."
        cd extrator-pdf
        docker-compose down 2>/dev/null || true
        cd ..
        rm -rf extrator-pdf
    fi
    
    # Cria diretório da aplicação
    mkdir -p extrator-pdf
    cd extrator-pdf
    
    # Extrai aplicação
    echo "📦 Extraindo aplicação..."
    tar -xzf /tmp/extrator-pdf-deploy.tar.gz
    rm /tmp/extrator-pdf-deploy.tar.gz
    
    # Cria diretórios necessários
    mkdir -p uploads results data logs
    chmod 755 uploads results data
    
    # Executa deploy
    echo "🚀 Iniciando deploy..."
    chmod +x deploy-casaos.sh
    ./deploy-casaos.sh
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "================================"
    echo "🌐 Acesse: http://$SERVER_IP:5000"
    echo "📊 Dashboard: http://$SERVER_IP:5000/dashboard"
    echo "❤️  Health: http://$SERVER_IP:5000/health"
    echo ""
    echo "📋 Para gerenciar:"
    echo "  ssh $SERVER_USER@$SERVER_IP"
    echo "  cd /DATA/AppData/extrator-pdf"
    echo "  docker-compose logs -f"
else
    echo "❌ Falha no deploy. Verifique os logs."
fi
