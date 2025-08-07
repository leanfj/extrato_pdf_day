#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para processar múltiplos PDFs em lote.
Processa todos os PDFs em uma pasta e consolida os resultados.
"""

import os
import glob
import pandas as pd
from extrator_pdf import PDFExtractor
from datetime import datetime

def processar_multiplos_pdfs(pasta_pdfs="."):
    """
    Processa todos os PDFs em uma pasta
    
    Args:
        pasta_pdfs (str): Caminho da pasta com os PDFs
    """
    # Encontra todos os PDFs na pasta
    padrao_pdf = os.path.join(pasta_pdfs, "*.pdf")
    arquivos_pdf = glob.glob(padrao_pdf, recursive=False)
    
    # Também procura por PDFs em maiúsculo
    padrao_pdf_maiusculo = os.path.join(pasta_pdfs, "*.PDF")
    arquivos_pdf.extend(glob.glob(padrao_pdf_maiusculo, recursive=False))
    
    if not arquivos_pdf:
        print(f"❌ Nenhum arquivo PDF encontrado em: {pasta_pdfs}")
        return
    
    print(f"📁 Encontrados {len(arquivos_pdf)} arquivo(s) PDF:")
    for i, arquivo in enumerate(arquivos_pdf, 1):
        print(f"  {i}. {os.path.basename(arquivo)}")
    
    print("\n" + "=" * 60)
    
    # Lista para armazenar todos os dados
    todos_dados = []
    estatisticas = {
        'processados': 0,
        'com_dados': 0,
        'sem_dados': 0,
        'com_erro': 0
    }
    
    # Processa cada PDF
    for i, arquivo_pdf in enumerate(arquivos_pdf, 1):
        nome_arquivo = os.path.basename(arquivo_pdf)
        print(f"\n🔍 [{i}/{len(arquivos_pdf)}] Processando: {nome_arquivo}")
        
        try:
            # Cria o extrator
            extractor = PDFExtractor(arquivo_pdf)
            
            # Extrai os dados
            dados = extractor.extract_data()
            
            if dados:
                # Adiciona informação do arquivo fonte
                for registro in dados:
                    registro['arquivo_fonte'] = nome_arquivo
                
                todos_dados.extend(dados)
                estatisticas['com_dados'] += 1
                print(f"  ✅ {len(dados)} registro(s) extraído(s)")
            else:
                estatisticas['sem_dados'] += 1
                print(f"  ⚠️  Nenhum dado encontrado")
            
            estatisticas['processados'] += 1
            
        except Exception as e:
            estatisticas['com_erro'] += 1
            print(f"  ❌ Erro: {e}")
    
    # Exibe estatísticas finais
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS FINAIS:")
    print(f"  Arquivos processados: {estatisticas['processados']}")
    print(f"  Com dados extraídos: {estatisticas['com_dados']}")
    print(f"  Sem dados: {estatisticas['sem_dados']}")
    print(f"  Com erro: {estatisticas['com_erro']}")
    
    if todos_dados:
        print(f"\n📋 RESUMO CONSOLIDADO:")
        print(f"  Total de registros: {len(todos_dados)}")
        
        # Cria DataFrame consolidado
        df_consolidado = pd.DataFrame(todos_dados)
        
        # Estatísticas detalhadas
        print(f"  Placas únicas: {df_consolidado['placa'].nunique()}")
        print(f"  Registros com data: {len(df_consolidado[df_consolidado['data'] != ''])}")
        print(f"  Registros com valor: {len(df_consolidado[df_consolidado['total'] != ''])}")
        
        # Estatísticas por arquivo
        print(f"\n📁 REGISTROS POR ARQUIVO:")
        por_arquivo = df_consolidado.groupby('arquivo_fonte').size().sort_values(ascending=False)
        for arquivo, count in por_arquivo.items():
            print(f"  {arquivo}: {count} registros")
        
        # Salva arquivo consolidado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_excel = f"dados_consolidados_{timestamp}.xlsx"
        arquivo_csv = f"dados_consolidados_{timestamp}.csv"
        
        # Reordena colunas
        columns_order = ['arquivo_fonte', 'placa', 'data', 'total', 'texto_original', 'pagina', 'linha_referencia']
        df_consolidado = df_consolidado.reindex(columns=columns_order)
        
        df_consolidado.to_excel(arquivo_excel, index=False)
        df_consolidado.to_csv(arquivo_csv, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 ARQUIVOS SALVOS:")
        print(f"  📊 Excel: {arquivo_excel}")
        print(f"  📄 CSV: {arquivo_csv}")
        
        # Análise adicional
        if df_consolidado['total'].notna().any() and df_consolidado['total'].str.replace(',', '.').str.replace('', '0').astype(float).sum() > 0:
            valor_total = df_consolidado['total'].str.replace(',', '.').str.replace('', '0').astype(float).sum()
            print(f"\n💰 VALOR TOTAL: R$ {valor_total:,.2f}")
    
    else:
        print("\n❌ Nenhum dado foi extraído de nenhum arquivo.")

def main():
    print("🚀 PROCESSADOR DE MÚLTIPLOS PDFs")
    print("=" * 60)
    
    # Pasta atual por padrão
    pasta = input("Digite o caminho da pasta (Enter para pasta atual): ").strip()
    if not pasta:
        pasta = "."
    
    if not os.path.exists(pasta):
        print(f"❌ Pasta não encontrada: {pasta}")
        return
    
    processar_multiplos_pdfs(pasta)

if __name__ == "__main__":
    main()
