#!/bin/bash

# 🚀 Script de Deploy Simplificado
# Executa o deploy completo para CasaOS

set -e

echo "🚀 Iniciando deploy para CasaOS..."

# Verifica se está no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: app.py não encontrado!"
    echo "Execute este script no diretório raiz do projeto."
    exit 1
fi

# Executa o script de deploy completo
echo "📋 Executando deploy-casaos.sh..."
cd deploy
./deploy-casaos.sh

echo "✅ Deploy concluído!"
