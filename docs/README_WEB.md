# 🌐 Aplicação Web - Extrator de PDF

## Visão Geral

Aplicação web moderna para extração de dados de PDFs de débitos detalhados, com interface intuitiva, dashboard interativo e sistema de download dos resultados.

## 🚀 Funcionalidades

### ✨ Interface Web
- **Upload de Arquivos**: Interface drag-and-drop para envio de PDFs
- **Processamento em Tempo Real**: Feedback visual do progresso
- **Visualização de Dados**: DataGrid interativo com os dados extraídos
- **Dashboard**: Estatísticas e gráficos dos processamentos
- **Downloads**: Excel, CSV e ZIP com ambos os formatos

### 📊 Dashboard Analítico
- **Estatísticas Gerais**: Total de arquivos, taxa de sucesso, registros extraídos
- **Gráficos Interativos**: Status dos processamentos e registros por arquivo
- **Histórico Completo**: Lista de todos os processamentos realizados
- **Filtros e Busca**: Pesquisa avançada no histórico

### 🔧 Recursos Técnicos
- **Responsive Design**: Funciona em desktop, tablet e mobile
- **DataTables**: Tabelas interativas com ordenação e filtros
- **Bootstrap 5**: Interface moderna e profissional
- **Charts.js**: Gráficos interativos e responsivos
- **Flask Backend**: API REST para processamento

## 📦 Estrutura do Projeto

```
extrator_pdf/
├── app.py                  # Aplicação Flask principal
├── extrator_pdf.py         # Lógica de extração de PDF
├── templates/              # Templates HTML
│   ├── base.html          # Template base
│   ├── index.html         # Página principal
│   ├── results.html       # Página de resultados
│   ├── dashboard.html     # Dashboard
│   ├── 404.html           # Página de erro 404
│   └── 500.html           # Página de erro 500
├── static/                 # Arquivos estáticos
│   ├── css/
│   │   └── style.css      # CSS customizado
│   └── js/                # JavaScript (se necessário)
├── uploads/                # Diretório para uploads
├── results/                # Diretório para resultados
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── nginx.conf             # Configuração Nginx
├── deploy.sh              # Script de deploy
└── requirements.txt       # Dependências Python
```

## 🏃‍♂️ Como Executar

### Opção 1: Desenvolvimento Local

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Instalar dependências web
pip install Flask==3.0.0 Werkzeug==3.0.1 gunicorn==21.2.0

# 3. Executar aplicação
python app.py
```

**Acesso**: http://localhost:5000

### Opção 2: Docker (Recomendado)

```bash
# Desenvolvimento
./deploy.sh dev

# Produção (com Nginx)
./deploy.sh prod
```

**Acesso**: 
- Desenvolvimento: http://localhost:5000
- Produção: http://localhost (nginx) ou http://localhost:5000 (direto)

### Opção 3: Docker Manual

```bash
# Construir imagem
docker build -t extrator-pdf .

# Executar container
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/results:/app/results extrator-pdf
```

## 🎯 Como Usar a Aplicação

### 1. Upload de Arquivo
1. Acesse a página principal
2. Clique em "Escolher arquivo" ou arraste o PDF
3. Clique em "Processar Arquivo"
4. Aguarde o processamento

### 2. Visualizar Resultados
- **Estatísticas**: Cards com resumo dos dados extraídos
- **Tabela Interativa**: Dados completos com ordenação e filtro
- **Downloads**: Botões para baixar Excel, CSV ou ambos

### 3. Acessar Dashboard
- Clique em "Dashboard" no menu
- Visualize estatísticas gerais
- Analise gráficos de performance
- Consulte histórico de processamentos

## 🔌 API Endpoints

### Principais Rotas

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página principal |
| `/upload` | POST | Upload e processamento de PDF |
| `/results/<job_id>` | GET | Página de resultados |
| `/dashboard` | GET | Dashboard analítico |
| `/download/<job_id>/<type>` | GET | Download de arquivos |

### API REST

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/job/<job_id>` | GET | Status do processamento |
| `/api/data/<job_id>` | GET | Dados extraídos (JSON) |
| `/api/dashboard/stats` | GET | Estatísticas do dashboard |

### Exemplo de Uso da API

```bash
# Verificar status de um job
curl http://localhost:5000/api/job/abc123

# Obter dados extraídos
curl http://localhost:5000/api/data/abc123

# Estatísticas do dashboard
curl http://localhost:5000/api/dashboard/stats
```

## 🐳 Deploy em Produção

### Deploy Simples

```bash
# Clone o repositório
git clone <repo-url>
cd extrator_pdf

# Execute deploy em produção
./deploy.sh prod
```

### Deploy com Customizações

```bash
# 1. Edite variáveis de ambiente (se necessário)
vim docker-compose.yml

# 2. Customize configuração do Nginx
vim nginx.conf

# 3. Execute deploy
docker-compose --profile production up -d
```

### Variáveis de Ambiente

```bash
# No docker-compose.yml ou .env
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=sua-chave-secreta-aqui
MAX_CONTENT_LENGTH=52428800  # 50MB
```

## 🔧 Configurações Avançadas

### Nginx como Proxy Reverso

O arquivo `nginx.conf` está configurado para:
- Servir arquivos estáticos diretamente
- Proxy reverso para aplicação Flask
- Compressão gzip
- Headers de segurança
- Upload de até 50MB

### Personalização da Interface

Edite os arquivos em `templates/` e `static/css/style.css` para:
- Alterar cores e tema
- Modificar layout
- Adicionar funcionalidades
- Customizar textos

### Monitoramento

```bash
# Logs da aplicação
docker-compose logs -f web

# Status dos containers
docker-compose ps

# Uso de recursos
docker stats
```

## 🔒 Segurança

### Medidas Implementadas

- **Upload Validation**: Apenas arquivos PDF são aceitos
- **File Size Limit**: Máximo de 50MB por arquivo
- **User Context**: Container roda com usuário não-root
- **Security Headers**: Headers de segurança no Nginx
- **Input Sanitization**: Nomes de arquivos são sanitizados

### Recomendações para Produção

1. **HTTPS**: Configure SSL/TLS
2. **Firewall**: Restrinja acesso às portas
3. **Backup**: Configure backup dos volumes
4. **Monitoring**: Implemente monitoramento (Prometheus/Grafana)
5. **Rate Limiting**: Configure limite de requisições

## 📈 Performance

### Otimizações Implementadas

- **Gunicorn**: Servidor WSGI para produção
- **Static Files**: Servidos pelo Nginx
- **Compression**: Gzip habilitado
- **Caching**: Headers de cache configurados
- **Resource Limits**: Limites de memória e CPU

### Escalabilidade

Para maior demanda:

```yaml
# No docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
    environment:
      - WORKERS=4
```

## 🛠️ Troubleshooting

### Problemas Comuns

**Erro 413: File too large**
```bash
# Aumente o limite no nginx.conf
client_max_body_size 100M;
```

**Container não inicia**
```bash
# Verifique logs
docker-compose logs web

# Reconstrua a imagem
docker-compose up --build
```

**PDF não é processado**
- Verifique se o PDF contém texto (não é imagem)
- Confirme que o arquivo não está corrompido
- Examine os logs para erros específicos

### Comandos Úteis

```bash
# Restart completo
docker-compose down && docker-compose up -d

# Limpeza de espaço
docker system prune -a

# Backup de dados
tar -czf backup.tar.gz uploads/ results/

# Restore de dados
tar -xzf backup.tar.gz
```

## 📞 Suporte

Para problemas específicos:

1. **Verifique os logs**: `docker-compose logs -f`
2. **Teste com PDF menor**: Isole o problema
3. **Verifique recursos**: CPU/Memória disponível
4. **Consulte documentação**: README.md e GUIA_DE_USO.md

## 🎉 Próximos Passos

Possíveis melhorias futuras:

- [ ] Autenticação de usuários
- [ ] API rate limiting
- [ ] Queue system (Redis/Celery)
- [ ] Websockets para progresso em tempo real
- [ ] Suporte a múltiplos formatos
- [ ] Machine Learning para melhor extração
- [ ] Exportação em mais formatos (JSON, XML)
- [ ] Dashboard com mais métricas
