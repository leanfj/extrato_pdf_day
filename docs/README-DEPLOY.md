# 🚀 DEPLOY NO CASAOS - GUIA RÁPIDO

## 🎯 **DEPLOY EM 3 PASSOS**

### **Método 1: Upload Automático (RECOMENDADO)**
```bash
# 1. Execute o script de upload
./upload-to-casaos.sh

# 2. Pronto! Acesse: http://192.168.0.9:5000
```

### **Método 2: Manual via SSH**
```bash
# 1. SSH no servidor
ssh root@192.168.0.9

# 2. Navegue para pasta de apps
cd /DATA/AppData

# 3. Clone ou copie os arquivos
git clone [seu-repo] extrator-pdf
cd extrator-pdf

# 4. Execute o deploy
chmod +x deploy-casaos.sh
./deploy-casaos.sh
```

### **Método 3: Via Interface CasaOS**
1. Acesse http://192.168.0.9
2. Vá em **App Store** → **Custom Install**
3. Cole o conteúdo de `docker-compose.casaos.yml`
4. Clique em **Install**

---

## 🌐 **ACESSOS APÓS DEPLOY**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Aplicação Principal** | http://192.168.0.9:5000 | Interface de upload e extração |
| **Dashboard** | http://192.168.0.9:5000/dashboard | Painel de controle e estatísticas |
| **Health Check** | http://192.168.0.9:5000/health | Status da aplicação (JSON) |

---

## 🔧 **COMANDOS DE GERENCIAMENTO**

### **Status e Logs**
```bash
# SSH no servidor
ssh root@192.168.0.9
cd /DATA/AppData/extrator-pdf

# Ver status
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs extrator-pdf
```

### **Controle da Aplicação**
```bash
# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Iniciar
docker-compose up -d

# Reconstruir (após mudanças)
docker-compose up --build -d
```

### **Atualização**
```bash
# Executar script de atualização
./update.sh

# Ou manualmente:
docker-compose down
git pull  # se usando git
docker-compose up --build -d
```

---

## 📊 **MONITORAMENTO**

### **Health Check Automático**
- URL: http://192.168.0.9:5000/health
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Retries: 3

### **Exemplo de Response Health:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-06T20:30:00",
  "version": "1.0.0",
  "uptime": 3600,
  "disk_space_gb": 45.2,
  "checks": {
    "database": "ok",
    "filesystem": "ok", 
    "dependencies": "ok",
    "disk_space": "ok"
  }
}
```

---

## 🔒 **CONFIGURAÇÕES DE SEGURANÇA**

### **Firewall (se necessário)**
```bash
# Abrir porta 5000
ufw allow 5000/tcp
ufw reload
```

### **Backup Automático**
```bash
# Criar script de backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/extrator-pdf_$DATE.tar.gz /DATA/AppData/extrator-pdf/
find /backup -name "extrator-pdf_*.tar.gz" -mtime +7 -delete
```

---

## 🚨 **TROUBLESHOOTING**

### **Problema: Container não inicia**
```bash
# Ver logs detalhados
docker-compose logs extrator-pdf

# Verificar recursos
docker stats
df -h

# Verificar permissões
ls -la uploads/ results/
```

### **Problema: Aplicação não responde**
```bash
# Testar conectividade
curl -f http://192.168.0.9:5000/health

# Reiniciar se necessário
docker-compose restart

# Verificar porta
netstat -tulpn | grep 5000
```

### **Problema: Upload falha**
```bash
# Verificar espaço em disco
df -h

# Verificar permissões das pastas
chmod 755 uploads results

# Verificar logs de erro
docker-compose logs | grep -i error
```

---

## 📁 **ESTRUTURA DE ARQUIVOS NO SERVIDOR**

```
/DATA/AppData/extrator-pdf/
├── app.py                 # Aplicação principal
├── extrator_pdf.py        # Módulo de extração
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração Docker
├── docker-compose.yml    # Orquestração
├── deploy-casaos.sh      # Script de deploy
├── uploads/              # PDFs enviados
├── results/              # Arquivos processados
├── data/                 # Dados da aplicação
├── static/               # CSS, JS, imagens
└── templates/            # Templates HTML
```

---

## 🎯 **CHECKLIST PRÉ-DEPLOY**

- [ ] Servidor CasaOS funcionando (192.168.0.9)
- [ ] SSH habilitado no servidor
- [ ] Docker instalado no servidor
- [ ] Porta 5000 disponível
- [ ] Espaço em disco suficiente (>2GB)
- [ ] Conectividade de rede

---

## 📞 **SUPORTE**

### **Logs Importantes**
```bash
# Logs da aplicação
docker-compose logs extrator-pdf

# Logs do sistema
journalctl -u docker

# Uso de recursos
docker stats extrator-pdf-app
```

### **URLs de Teste**
- http://192.168.0.9:5000 (deve carregar interface)
- http://192.168.0.9:5000/health (deve retornar JSON)
- http://192.168.0.9:5000/dashboard (deve carregar painel)

---

**📅 Criado**: 06 de Agosto de 2025  
**🎯 Servidor**: CasaOS (192.168.0.9)  
**✅ Status**: Pronto para deploy
