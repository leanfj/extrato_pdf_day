# 🏠 INSTRUÇÕES ESPECÍFICAS PARA CASAOS

## 🚀 **DEPLOY SIMPLES - 5 MINUTOS**

### **OPÇÃO A: Upload Automático (Mais Fácil)**
```bash
# No seu computador local:
./upload-to-casaos.sh
```

### **OPÇÃO B: Comando Manual**
```bash
# SSH no CasaOS
ssh root@192.168.0.9

# Comando único de deploy
curl -sSL https://raw.githubusercontent.com/seu-usuario/extrator-pdf/main/install-casaos.sh | bash
```

### **OPÇÃO C: Via Interface CasaOS**
1. Acesse: http://192.168.0.9 (interface CasaOS)
2. Clique em **App Store**
3. Clique em **Custom Install** 
4. Cole este YAML:

```yaml
name: extrator-pdf
services:
  app:
    container_name: extrator-pdf
    image: python:3.11-slim
    ports:
      - "5000:5000"
    volumes:
      - /DATA/AppData/extrator-pdf/uploads:/app/uploads
      - /DATA/AppData/extrator-pdf/results:/app/results
      - /DATA/AppData/extrator-pdf/app:/app
    working_dir: /app
    command: >
      sh -c "
      pip install flask pdfplumber pandas openpyxl gunicorn requests &&
      python app.py
      "
    environment:
      - FLASK_ENV=production
      - FLASK_APP=app.py
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
x-casaos:
  title: "Extrator PDF"
  description: "Extrator de dados de arquivos PDF"
  icon: "https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/pdf.png"
  port_map: "5000"
  index: "/"
```

5. Clique em **Install**
6. Aguarde a instalação
7. Acesse pelo ícone criado

---

## 📂 **ONDE FICAM OS ARQUIVOS NO CASAOS**

```
/DATA/AppData/extrator-pdf/
├── uploads/          # PDFs que você envia
├── results/          # Planilhas geradas
├── app/              # Código da aplicação
└── logs/             # Logs do sistema
```

---

## 🌐 **COMO ACESSAR APÓS INSTALAÇÃO**

### **URLs de Acesso:**
- **Principal**: http://192.168.0.9:5000
- **Dashboard**: http://192.168.0.9:5000/dashboard
- **Status**: http://192.168.0.9:5000/health

### **Via CasaOS:**
1. Acesse http://192.168.0.9
2. Clique no ícone do "Extrator PDF"
3. Interface abrirá automaticamente

---

## 🔧 **GERENCIAMENTO VIA CASAOS**

### **Parar/Iniciar Aplicação:**
1. Acesse http://192.168.0.9 (CasaOS)
2. Vá em **Apps**
3. Encontre "Extrator PDF"
4. Use os botões **Stop/Start/Restart**

### **Ver Logs:**
1. No CasaOS, clique no app
2. Clique em **Logs**
3. Veja logs em tempo real

### **Configurações:**
1. No CasaOS, clique no app
2. Clique em **Settings**
3. Ajuste conforme necessário

---

## 📱 **ACESSO DE OUTROS DISPOSITIVOS**

### **Na Sua Rede Local:**
Qualquer dispositivo na rede pode acessar:
- **Desktop**: http://192.168.0.9:5000
- **Notebook**: http://192.168.0.9:5000  
- **Tablet**: http://192.168.0.9:5000
- **Celular**: http://192.168.0.9:5000

### **Configuração de DNS (Opcional):**
Para usar nomes amigáveis, adicione ao `/etc/hosts` dos dispositivos:
```
192.168.0.9 extrator-pdf.local
```
Depois acesse: http://extrator-pdf.local:5000

---

## 🔒 **SEGURANÇA NA REDE LOCAL**

### **Firewall do CasaOS:**
```bash
# SSH no servidor
ssh root@192.168.0.9

# Verificar porta aberta
netstat -tulpn | grep 5000

# Se necessário, abrir porta
ufw allow 5000/tcp
```

### **Acesso Restrito:**
Se quiser restringir acesso, edite o docker-compose para:
```yaml
ports:
  - "127.0.0.1:5000:5000"  # Apenas local
```

---

## 💾 **BACKUP E RESTAURAÇÃO**

### **Backup Manual:**
```bash
# SSH no CasaOS
ssh root@192.168.0.9

# Backup completo
tar -czf backup-extrator-pdf.tar.gz /DATA/AppData/extrator-pdf/

# Download do backup
scp root@192.168.0.9:backup-extrator-pdf.tar.gz ./
```

### **Restauração:**
```bash
# Upload do backup
scp backup-extrator-pdf.tar.gz root@192.168.0.9:/tmp/

# SSH e restaurar
ssh root@192.168.0.9
cd /DATA/AppData/
tar -xzf /tmp/backup-extrator-pdf.tar.gz
```

### **Backup Automático (Opcional):**
```bash
# Criar script de backup diário
cat > /etc/cron.daily/backup-extrator << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backup/extrator-pdf_$DATE.tar.gz /DATA/AppData/extrator-pdf/
find /backup -name "extrator-pdf_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/backup-extrator
```

---

## 🚨 **RESOLUÇÃO DE PROBLEMAS**

### **Aplicação não abre:**
1. Verifique se container está rodando:
   - CasaOS → Apps → Extrator PDF → Status
2. Se parado, clique em **Start**
3. Se erro, verifique logs

### **Erro de permissão:**
```bash
ssh root@192.168.0.9
cd /DATA/AppData/extrator-pdf
chmod -R 755 uploads results
chown -R 1000:1000 uploads results
```

### **Falta de espaço:**
```bash
# Verificar espaço
df -h /DATA

# Limpar arquivos antigos
find /DATA/AppData/extrator-pdf/results -mtime +30 -delete
```

### **Container não inicia:**
```bash
# Ver logs detalhados
docker logs extrator-pdf

# Reiniciar Docker
systemctl restart docker
```

---

## 📈 **MONITORAMENTO**

### **Verificação de Saúde:**
```bash
# Teste rápido
curl http://192.168.0.9:5000/health

# Resposta esperada:
# {"status": "healthy", ...}
```

### **Uso de Recursos:**
```bash
# Ver uso de CPU/RAM
docker stats extrator-pdf

# Ver espaço em disco
du -sh /DATA/AppData/extrator-pdf/
```

---

## 🎯 **DICAS DE USO**

### **Para Melhor Performance:**
1. Use PDFs com até 50MB
2. Processe um arquivo por vez
3. Limpe resultados antigos regularmente

### **Formatos Suportados:**
- ✅ PDF (único formato aceito)
- ✅ Saída: Excel (.xlsx) e CSV (.csv)

### **Backup dos Resultados:**
- Os arquivos ficam em `/DATA/AppData/extrator-pdf/results/`
- Faça backup regularmente
- Acesse via interface web para download

---

## 📞 **SUPORTE RÁPIDO**

### **Comandos de Diagnóstico:**
```bash
# Teste completo
curl -f http://192.168.0.9:5000/health && echo "✅ OK" || echo "❌ ERRO"

# Status do container
docker ps | grep extrator

# Logs recentes
docker logs --tail=20 extrator-pdf
```

### **Reset Completo (Se Necessário):**
```bash
ssh root@192.168.0.9
cd /DATA/AppData/extrator-pdf
docker-compose down
docker system prune -f
docker-compose up -d --build
```

---

**🏠 Configurado para CasaOS em 192.168.0.9**  
**📅 Data: 06 de Agosto de 2025**  
**✅ Pronto para uso na sua rede doméstica!**
