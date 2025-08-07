# 🚀 GUIA DE DEPLOY - CasaOS (192.168.0.9)

## 📋 **Opções de Deploy**

### 🐳 **OPÇÃO 1: Docker Compose (RECOMENDADO)**
### 🔧 **OPÇÃO 2: Aplicação Manual**
### 📦 **OPÇÃO 3: App Store CasaOS**

---

## 🐳 **OPÇÃO 1: Docker Compose (RECOMENDADO)**

### **1. Preparar Arquivos de Deploy**

#### **A. docker-compose.yml**
```yaml
version: '3.8'

services:
  extrator-pdf:
    build: .
    container_name: extrator-pdf-app
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - FLASK_APP=app.py
    restart: unless-stopped
    networks:
      - extrator-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  extrator-network:
    driver: bridge

volumes:
  uploads:
  results:
  data:
```

#### **B. .env (configurações)**
```env
# Configurações da aplicação
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_super_segura_aqui_2025

# Configurações de rede
HOST=0.0.0.0
PORT=5000

# Configurações de upload
MAX_CONTENT_LENGTH=50MB
UPLOAD_FOLDER=uploads
RESULTS_FOLDER=results

# Configurações de segurança
ALLOWED_EXTENSIONS=pdf

# Configurações de banco (se necessário no futuro)
# DATABASE_URL=sqlite:///data/extrator.db
```

#### **C. nginx.conf (proxy reverso)**
```nginx
upstream extrator_app {
    server extrator-pdf-app:5000;
}

server {
    listen 80;
    server_name 192.168.0.9 extrator-pdf.local;
    client_max_body_size 50M;
    
    # Logs
    access_log /var/log/nginx/extrator_access.log;
    error_log /var/log/nginx/extrator_error.log;
    
    # Arquivos estáticos
    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Aplicação principal
    location / {
        proxy_pass http://extrator_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        proxy_pass http://extrator_app/health;
        access_log off;
    }
}
```

### **2. Scripts de Deploy**

#### **A. deploy.sh**
```bash
#!/bin/bash

echo "🚀 INICIANDO DEPLOY DO EXTRATOR PDF"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
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

# Para containers existentes
log_info "Parando containers existentes..."
docker-compose down

# Remove imagens antigas (opcional)
log_info "Removendo imagens antigas..."
docker image prune -f

# Constrói e inicia os containers
log_info "Construindo e iniciando containers..."
docker-compose up --build -d

# Aguarda containers iniciarem
log_info "Aguardando containers iniciarem..."
sleep 10

# Verifica status
log_info "Verificando status dos containers..."
docker-compose ps

# Testa aplicação
log_info "Testando aplicação..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    log_success "✅ Aplicação rodando com sucesso!"
    log_success "🌐 Acesse: http://192.168.0.9:5000"
else
    log_error "❌ Falha ao acessar aplicação"
    log_info "Logs do container:"
    docker-compose logs extrator-pdf
fi

# Mostra logs em tempo real (opcional)
read -p "Deseja ver os logs em tempo real? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi
```

#### **B. update.sh**
```bash
#!/bin/bash

echo "🔄 ATUALIZANDO EXTRATOR PDF"
echo "=========================="

# Para aplicação
docker-compose down

# Atualiza código (se usando git)
if [ -d ".git" ]; then
    echo "📥 Atualizando código..."
    git pull
fi

# Reconstrói e reinicia
echo "🔨 Reconstruindo aplicação..."
docker-compose build --no-cache

echo "🚀 Reiniciando aplicação..."
docker-compose up -d

echo "✅ Atualização concluída!"
echo "🌐 Acesse: http://192.168.0.9:5000"
```

### **3. Configuração no CasaOS**

#### **A. Via Interface Web**
1. Acesse http://192.168.0.9
2. Vá em **App Store** → **Custom Install**
3. Cole este docker-compose:

```yaml
name: extrator-pdf
services:
  extrator-pdf:
    image: ghcr.io/seu-usuario/extrator-pdf:latest
    container_name: extrator-pdf
    ports:
      - "5000:5000"
    volumes:
      - /DATA/AppData/extrator-pdf/uploads:/app/uploads
      - /DATA/AppData/extrator-pdf/results:/app/results
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    cpu_shares: 90
    deploy:
      resources:
        limits:
          memory: 1G
    networks:
      - casa_network
```

#### **B. Via Terminal SSH**
```bash
# Conecta ao servidor
ssh root@192.168.0.9

# Navega para pasta de apps
cd /DATA/AppData

# Clona repositório (ou copia arquivos)
git clone https://github.com/seu-usuario/extrator-pdf.git
cd extrator-pdf

# Executa deploy
chmod +x deploy.sh
./deploy.sh
```

---

## 🔧 **OPÇÃO 2: Instalação Manual**

### **1. Preparação do Servidor**
```bash
# SSH no servidor
ssh root@192.168.0.9

# Atualiza sistema
apt update && apt upgrade -y

# Instala dependências
apt install -y python3 python3-pip python3-venv nginx git curl

# Cria usuário para aplicação
useradd -m -s /bin/bash extrator
usermod -aG sudo extrator
```

### **2. Instalação da Aplicação**
```bash
# Muda para usuário da aplicação
su - extrator

# Clona ou copia aplicação
mkdir -p /home/extrator/apps
cd /home/extrator/apps
git clone [seu-repositorio] extrator-pdf
cd extrator-pdf

# Cria ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt
pip install gunicorn

# Testa aplicação
python app.py
```

### **3. Configuração do Systemd**
```bash
# Cria serviço
sudo nano /etc/systemd/system/extrator-pdf.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=Extrator PDF Web Application
After=network.target

[Service]
Type=exec
User=extrator
Group=extrator
WorkingDirectory=/home/extrator/apps/extrator-pdf
Environment=PATH=/home/extrator/apps/extrator-pdf/venv/bin
ExecStart=/home/extrator/apps/extrator-pdf/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Ativa e inicia serviço
sudo systemctl daemon-reload
sudo systemctl enable extrator-pdf
sudo systemctl start extrator-pdf
sudo systemctl status extrator-pdf
```

### **4. Configuração do Nginx**
```bash
# Configuração do site
sudo nano /etc/nginx/sites-available/extrator-pdf
```

```nginx
server {
    listen 80;
    server_name 192.168.0.9;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static/ {
        alias /home/extrator/apps/extrator-pdf/static/;
    }
}
```

```bash
# Ativa site
sudo ln -s /etc/nginx/sites-available/extrator-pdf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📦 **OPÇÃO 3: App CasaOS Personalizado**

### **1. Criar app-store.json**
```json
{
  "version": "1.0.0",
  "title": "Extrator PDF",
  "description": "Sistema para extração de dados de PDFs de débitos detalhados",
  "short_description": "Extrator de dados PDF",
  "developer": "Seu Nome",
  "author": "Seu Nome",
  "icon": "https://cdn.jsdelivr.net/gh/IceWhaleTech/CasaOS-AppStore@main/Apps/Nextcloud/icon.png",
  "screenshot_link": [
    "screenshot1.png",
    "screenshot2.png"
  ],
  "thumbnail": "thumbnail.png",
  "category": "Productivity",
  "port_map": "5000",
  "scheme": "http",
  "index": "/",
  "container": {
    "image": "python:3.11-slim",
    "shell": "sh",
    "privileged": false,
    "network_model": "bridge",
    "web_ui": {
      "http": "5000",
      "path": "/"
    },
    "health_check": "curl -f http://localhost:5000/ || exit 1",
    "environment": [
      "FLASK_ENV=production",
      "FLASK_APP=app.py"
    ],
    "restart_policy": "unless-stopped",
    "volumes": [
      {
        "container": "/app/uploads",
        "host": "/DATA/AppData/$AppID/uploads"
      },
      {
        "container": "/app/results", 
        "host": "/DATA/AppData/$AppID/results"
      }
    ],
    "ports": [
      {
        "container": "5000",
        "host": "5000",
        "type": "tcp",
        "allocation": "automatic"
      }
    ],
    "devices": [],
    "constraints": {
      "min_memory": 64,
      "min_storage": 100
    }
  }
}
```

---

## 🚀 **DEPLOY RÁPIDO (RECOMENDADO)**

### **Comando Único para CasaOS:**
```bash
# SSH no servidor
ssh root@192.168.0.9

# Comando de deploy completo
curl -sSL https://raw.githubusercontent.com/seu-usuario/extrator-pdf/main/deploy-casaos.sh | bash
```

### **Script deploy-casaos.sh:**
```bash
#!/bin/bash

echo "🚀 DEPLOY AUTOMÁTICO - EXTRATOR PDF"
echo "=================================="

# Cria estrutura de diretórios
mkdir -p /DATA/AppData/extrator-pdf/{uploads,results,data}

# Download da aplicação
cd /DATA/AppData/extrator-pdf
curl -sSL https://github.com/seu-usuario/extrator-pdf/archive/main.zip -o app.zip
unzip app.zip
mv extrator-pdf-main/* .
rm -rf extrator-pdf-main app.zip

# Instala Docker Compose se não existir
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Executa deploy
docker-compose up -d --build

echo "✅ Deploy concluído!"
echo "🌐 Acesse: http://192.168.0.9:5000"
echo "📊 Dashboard: http://192.168.0.9:5000/dashboard"
```

---

## 🌐 **CONFIGURAÇÃO DE REDE**

### **1. Acesso Local**
- **IP Principal**: http://192.168.0.9:5000
- **Dashboard**: http://192.168.0.9:5000/dashboard
- **Health Check**: http://192.168.0.9:5000/health

### **2. DNS Local (Opcional)**
```bash
# Adiciona entrada DNS local
echo "192.168.0.9 extrator-pdf.local" >> /etc/hosts

# Acesso via: http://extrator-pdf.local:5000
```

### **3. Firewall**
```bash
# Abre porta 5000
ufw allow 5000/tcp
ufw reload
```

---

## 🔧 **MONITORAMENTO**

### **1. Logs da Aplicação**
```bash
# Docker logs
docker-compose logs -f

# Systemd logs (se manual)
sudo journalctl -u extrator-pdf -f
```

### **2. Health Check**
```bash
# Teste manual
curl -f http://192.168.0.9:5000/health

# Monitoramento contínuo
watch -n 30 'curl -s http://192.168.0.9:5000/health | echo "$(date): OK"'
```

### **3. Recursos do Sistema**
```bash
# Uso de recursos
docker stats extrator-pdf-app

# Espaço em disco
df -h /DATA/AppData/extrator-pdf/
```

---

## 🔒 **SEGURANÇA**

### **1. Firewall Básico**
```bash
# Regras UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 5000/tcp
ufw enable
```

### **2. SSL/HTTPS (Opcional)**
```bash
# Instala Certbot
apt install certbot python3-certbot-nginx

# Gera certificado (se domínio público)
certbot --nginx -d seu-dominio.com
```

### **3. Backup Automático**
```bash
# Script de backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/extrator-pdf_$DATE.tar.gz /DATA/AppData/extrator-pdf/
find /backup -name "extrator-pdf_*.tar.gz" -mtime +7 -delete
```

---

## ✅ **CHECKLIST DE DEPLOY**

### **Pré-Deploy**
- [ ] Servidor CasaOS funcionando em 192.168.0.9
- [ ] SSH habilitado no servidor
- [ ] Docker instalado
- [ ] Porta 5000 disponível

### **Deploy**
- [ ] Arquivos copiados para servidor
- [ ] Docker Compose configurado
- [ ] Containers iniciados
- [ ] Aplicação respondendo
- [ ] Health check funcionando

### **Pós-Deploy**
- [ ] Teste de upload de PDF
- [ ] Teste de extração de dados
- [ ] Teste de dashboard
- [ ] Backup configurado
- [ ] Monitoramento ativo

---

## 🚨 **TROUBLESHOOTING**

### **Problema: Container não inicia**
```bash
# Verifica logs
docker-compose logs extrator-pdf

# Verifica recursos
docker stats
df -h
```

### **Problema: Aplicação não responde**
```bash
# Reinicia containers
docker-compose restart

# Testa conectividade
curl -v http://192.168.0.9:5000
```

### **Problema: Upload falha**
```bash
# Verifica permissões
ls -la uploads/
chmod 755 uploads/

# Verifica espaço
df -h
```

---

**📅 Data**: 06 de Agosto de 2025  
**🎯 Objetivo**: Deploy em CasaOS (192.168.0.9)  
**✅ Status**: Guia completo pronto para execução
