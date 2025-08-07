# Guia de Uso - Extrator de PDF

## 🚀 Como usar o projeto

### 1. Instalação Inicial

```bash
# 1. Entre na pasta do projeto
cd extrator_pdf

# 2. Crie o ambiente virtual
python3 -m venv venv

# 3. Ative o ambiente virtual
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt
```

### 2. Uso Básico

#### Extrair dados de um PDF específico:
```bash
# Ativa o ambiente virtual
source venv/bin/activate

# Executa o extrator no arquivo padrão
python extrator_pdf.py

# OU executa em um arquivo específico
python exemplo_uso.py "nome_do_arquivo.pdf"
```

#### Processar múltiplos PDFs:
```bash
# Ativa o ambiente virtual
source venv/bin/activate

# Processa todos os PDFs da pasta atual
python processar_lote.py
```

#### Analisar dados extraídos:
```bash
# Ativa o ambiente virtual
source venv/bin/activate

# Analisa um arquivo de dados específico
python analisar_dados.py "arquivo_dados.csv"
```

### 3. Arquivos do Projeto

- `extrator_pdf.py` - Script principal com a classe PDFExtractor
- `exemplo_uso.py` - Script simples para uso direto
- `processar_lote.py` - Processa múltiplos PDFs em lote
- `analisar_dados.py` - Analisa os dados extraídos
- `requirements.txt` - Dependências do projeto
- `README.md` - Documentação completa

### 4. Tipos de Saída

O extrator gera automaticamente:
- **Excel (.xlsx)**: Para análise e manipulação em planilhas
- **CSV (.csv)**: Para integração com outros sistemas
- **Relatórios de análise**: Estatísticas detalhadas

### 5. Dados Extraídos

Cada registro contém:
- `placa`: Placa do veículo (formatada)
- `data`: Data do débito (DD/MM/AAAA)
- `total`: Valor do débito
- `texto_original`: Linha original do PDF
- `pagina`: Número da página
- `linha_referencia`: Referência da linha/tabela

### 6. Exemplos de Uso

#### Exemplo 1: Uso programático
```python
from extrator_pdf import PDFExtractor

# Cria o extrator
extractor = PDFExtractor("meu_arquivo.pdf")

# Extrai os dados
dados = extractor.extract_data()

# Salva os resultados
extractor.save_to_excel("resultado.xlsx")
extractor.save_to_csv("resultado.csv")

# Exibe resumo
extractor.print_summary()
```

#### Exemplo 2: Processamento em lote
```python
import glob
from extrator_pdf import PDFExtractor

# Encontra todos os PDFs
pdfs = glob.glob("*.pdf")

todos_dados = []
for pdf in pdfs:
    extractor = PDFExtractor(pdf)
    dados = extractor.extract_data()
    todos_dados.extend(dados)

# Salva dados consolidados
import pandas as pd
df = pd.DataFrame(todos_dados)
df.to_excel("consolidado.xlsx", index=False)
```

### 7. Solução de Problemas

#### ❌ "Nenhum dado encontrado"
- Verifique se o PDF contém texto extraível (não é apenas imagem)
- Confirme se o formato do PDF é compatível
- Examine o campo `texto_original` nos dados para ajustar padrões

#### ❌ "Erro de instalação"
```bash
# Se houver problemas com dependências
pip install --upgrade pip
pip install -r requirements.txt
```

#### ❌ "Ambiente virtual não funciona"
```bash
# Recrie o ambiente virtual
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 8. Personalização

Para ajustar os padrões de reconhecimento, edite no arquivo `extrator_pdf.py`:

```python
# Padrões de regex (linhas ~119-121)
placa_pattern = r'\b[A-Z]{3}[-\s]?\d{4}\b|\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b'
data_pattern = r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b'
valor_pattern = r'R?\$?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2}'
```

### 9. Fluxo Completo Recomendado

1. **Extração**: Use `extrator_pdf.py` ou `processar_lote.py`
2. **Análise**: Use `analisar_dados.py` para verificar qualidade
3. **Ajustes**: Se necessário, ajuste padrões e reprocesse
4. **Relatórios**: Use os arquivos Excel gerados para análises finais

### 10. Estrutura de Pastas Recomendada

```
extrator_pdf/
├── venv/                    # Ambiente virtual
├── pdfs_originais/          # PDFs para processar
├── dados_extraidos/         # Arquivos CSV/Excel gerados
├── relatorios/             # Relatórios de análise
└── scripts/                # Scripts do projeto
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique este guia primeiro
2. Examine as mensagens de erro
3. Teste com um PDF menor para isolar o problema
4. Verifique se todas as dependências estão instaladas
