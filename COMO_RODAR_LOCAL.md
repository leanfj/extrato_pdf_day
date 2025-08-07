# 🚀 Como Rodar o Projeto Localmente

Este guia mostra todas as formas de executar o Extrator PDF localmente.

## 📋 Pré-requisitos

- **Python 3.11+** instalado
- **Git** (para clonar o repositório)
- **Docker** (opcional, para execução containerizada)

---

## 🛠️ Método 1: Setup Automático (Recomendado)

### 1. Clone o repositório
```bash
git clone https://github.com/leanfj/extrato_pdf_day.git
cd extrato_pdf_day
```

### 2. Execute o script de setup
```bash
./setup.sh
```

Este script irá:
- ✅ Criar diretórios necessários
- ✅ Configurar arquivo `.env`
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências

### 3. Ative o ambiente e execute
```bash
source venv/bin/activate
python app.py
```

### 4. Acesse no navegador
```
http://localhost:5000
```

---

## 🐍 Método 2: Setup Manual

### 1. Clone e entre no diretório
```bash
git clone https://github.com/leanfj/extrato_pdf_day.git
cd extrato_pdf_day
```

### 2. Crie o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure o ambiente
```bash
cp .env.example .env
# Edite o .env se necessário
```

### 5. Crie os diretórios
```bash
mkdir -p uploads results logs data
```

### 6. Execute a aplicação
```bash
python app.py
```

---

## 🐳 Método 3: Docker (Mais Simples)

### 1. Clone o repositório
```bash
git clone https://github.com/leanfj/extrato_pdf_day.git
cd extrato_pdf_day
```

### 2. Execute com Docker Compose
```bash
docker-compose up -d
```

### 3. Acesse no navegador
```
http://localhost:5000
```

### 4. Para parar
```bash
docker-compose down
```

---

## 🔧 Configurações Personalizadas

### Mudança de Porta
Se a porta 5000 estiver ocupada:

```bash
# Método 1: Variável de ambiente
export FLASK_RUN_PORT=5001
python app.py

# Método 2: Direto no código
python -c "
import os
os.environ['FLASK_RUN_PORT'] = '5001'
from app import app
app.run(host='0.0.0.0', port=5001, debug=True)
"
```

### Modo de Desenvolvimento
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Modo de Produção
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📂 Scripts de Exemplo

Além da interface web, você pode usar os scripts na pasta `examples/`:

### 1. Processamento simples de um PDF
```bash
cd examples
python exemplo_uso.py "../caminho/para/arquivo.pdf"
```

### 2. Processamento em lote
```bash
cd examples
python processar_lote.py "../pasta_com_pdfs/"
```

### 3. Análise de dados extraídos
```bash
cd examples
python analisar_dados.py "../arquivo_dados.xlsx"
```

---

## 🔍 Verificação de Status

### Verificar se está rodando
```bash
curl http://localhost:5000/health
```

### Ver logs em tempo real
```bash
# Docker
docker-compose logs -f

# Local (se disponível)
tail -f logs/app.log
```

### Status dos containers (Docker)
```bash
docker-compose ps
```

---

## 🚨 Solucionando Problemas

### Porta ocupada
```bash
# Verificar o que está usando a porta
sudo lsof -i :5000

# Parar processo específico
sudo kill <PID>

# Ou usar porta diferente
python -c "from app import app; app.run(port=5001)"
```

### Dependências em falta
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Permissões de pasta
```bash
chmod 755 uploads results
chown $USER:$USER uploads results
```

### Limpar ambiente
```bash
# Remover ambiente virtual
rm -rf venv

# Limpar containers Docker
docker-compose down -v
docker system prune -f
```

---

## 📝 URLs Disponíveis

Após iniciar a aplicação:

- **🏠 Página Principal**: http://localhost:5000
- **📊 Dashboard**: http://localhost:5000/dashboard
- **❤️ Health Check**: http://localhost:5000/health
- **📄 API Status**: http://localhost:5000/api/status

---

## 🎯 Resumo dos Comandos

### Início Rápido
```bash
# Opção 1: Setup automático
./setup.sh && source venv/bin/activate && python app.py

# Opção 2: Docker
docker-compose up -d

# Opção 3: Manual
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python app.py
```

### Desenvolvimento
```bash
source venv/bin/activate
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Produção Local
```bash
source venv/bin/activate
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ✅ Sucesso!

Se tudo estiver funcionando, você verá:
- ✅ Aplicação rodando em http://localhost:5000
- ✅ Interface web carregando
- ✅ Upload de PDFs funcionando
- ✅ Geração de planilhas Excel

**🎉 Agora você pode usar o Extrator PDF localmente!**
