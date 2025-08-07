# 🔧 Solução para Problemas de Permissão no CasaOS

## 🚨 Problema Identificado

**Erro**: `[Errno 13] Permission denied: 'uploads/arquivo.pdf'`

**Causa**: Conflito de permissões entre o usuário do container Docker e os diretórios mapeados no host.

---

## ✅ Soluções Implementadas

### 1. **Correção no Dockerfile**
```dockerfile
# Criação de diretórios com permissões adequadas
RUN mkdir -p uploads results data logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/uploads /app/results /app/data /app/logs
```

### 2. **Docker Compose Otimizado**
```yaml
# Versão padrão com volumes nomeados (sem conflitos de permissão)
volumes:
  - uploads_data:/app/uploads
  - results_data:/app/results
  - data_storage:/app/data
```

### 3. **Script de Correção Automática**
Criado `fix-permissions.sh` para resolver problemas rapidamente:
```bash
./fix-permissions.sh
```

---

## 🚀 Como Aplicar a Correção

### **Opção 1: Script Automático (Recomendado)**
```bash
# No servidor CasaOS
./fix-permissions.sh
```

### **Opção 2: Comandos Manuais**
```bash
# Parar containers
docker-compose down

# Corrigir permissões
chmod 777 uploads results data logs
sudo chown -R $USER:$USER uploads results data logs

# Rebuild e restart
docker-compose build --no-cache
docker-compose up -d
```

### **Opção 3: Usar Volumes Nomeados**
```bash
# Usar docker-compose.yml padrão (sem bind mounts)
docker-compose -f docker-compose.yml up -d
```

---

## 🔍 Verificação da Correção

### 1. **Testar Upload**
```bash
curl -X POST -F "file=@teste.pdf" http://localhost:5000/upload
```

### 2. **Verificar Permissões**
```bash
ls -la uploads results data logs
```

### 3. **Logs do Container**
```bash
docker-compose logs -f extrator-pdf
```

---

## 📋 Diferentes Configurações

### **Para CasaOS (Acesso aos Arquivos)**
Use `docker-compose.host-access.yml`:
```yaml
# Permite acesso direto aos arquivos do host
volumes:
  - ./uploads:/app/uploads
  - ./results:/app/results
user: "1000:1000"
```

### **Para Deploy Simples (Isolado)**
Use `docker-compose.yml` padrão:
```yaml
# Volumes isolados, sem problemas de permissão
volumes:
  - uploads_data:/app/uploads
  - results_data:/app/results
```

---

## 🛠️ Comandos de Diagnóstico

### **Verificar Usuário do Container**
```bash
docker exec extrator-pdf-app id
```

### **Verificar Permissões no Container**
```bash
docker exec extrator-pdf-app ls -la /app/uploads
```

### **Verificar Permissões no Host**
```bash
ls -la uploads/
```

### **Testar Escrita no Container**
```bash
docker exec extrator-pdf-app touch /app/uploads/test.txt
```

---

## 🎯 Resumo da Solução

### ✅ **Correções Aplicadas**
1. **Dockerfile**: Permissões 777 para diretórios de trabalho
2. **Docker Compose**: Volumes nomeados para evitar conflitos
3. **Script de Correção**: Automação da correção de permissões
4. **Deploy CasaOS**: Permissões adequadas durante a criação

### 🔧 **Scripts Disponíveis**
- `fix-permissions.sh` - Correção automática
- `deploy-casaos.sh` - Deploy com permissões corretas
- `docker-compose.host-access.yml` - Para acesso direto aos arquivos

### 📊 **Status de Funcionamento**
- ✅ Upload de PDFs
- ✅ Processamento de arquivos
- ✅ Geração de planilhas
- ✅ Download de resultados

---

## 🚨 Se o Problema Persistir

### **Solução de Emergência**
```bash
# Permissões máximas (use apenas se necessário)
sudo chmod -R 777 uploads results data logs
docker-compose restart
```

### **Rebuild Completo**
```bash
# Rebuild sem cache
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### **Verificar SELinux/AppArmor**
```bash
# Verificar se SELinux está bloqueando
sudo dmesg | grep -i denied
```

---

## 🎉 Resultado Esperado

Após aplicar as correções:
- ✅ Uploads funcionando sem erros de permissão
- ✅ Arquivos processados corretamente
- ✅ Resultados gerados e acessíveis
- ✅ Sistema estável no CasaOS

**🚀 A aplicação deve funcionar perfeitamente no CasaOS!**
