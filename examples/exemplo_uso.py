#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simples para extrair dados de PDFs de débitos detalhados.
Uso: python exemplo_uso.py arquivo.pdf
"""

import sys
import os

# Adiciona o diretório pai ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extrator_pdf import PDFExtractor

def main():
    # Verifica se foi fornecido um arquivo
    if len(sys.argv) < 2:
        print("Uso: python exemplo_uso.py arquivo.pdf")
        print("\nExemplo:")
        print("python exemplo_uso.py '00000002387300 - DEBITOS DETALHADOS.PDF'")
        return
    
    pdf_path = sys.argv[1]
    
    # Verifica se o arquivo existe
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo não encontrado: {pdf_path}")
        return
    
    print(f"🔍 Processando arquivo: {pdf_path}")
    print("=" * 50)
    
    try:
        # Cria o extrator
        extractor = PDFExtractor(pdf_path)
        
        # Extrai os dados
        dados = extractor.extract_data()
        
        if dados:
            # Exibe resumo
            extractor.print_summary()
            
            # Pergunta se deseja salvar
            print("\n" + "=" * 50)
            resposta = input("Deseja salvar os dados extraídos? (s/N): ").lower()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                # Salva em Excel e CSV
                extractor.save_to_excel()
                extractor.save_to_csv()
                print("✅ Dados salvos com sucesso!")
            else:
                print("Dados não foram salvos.")
                
        else:
            print("❌ Nenhum dado foi encontrado no PDF.")
            print("\nPossíveis causas:")
            print("- PDF pode ser uma imagem (não tem texto extraível)")
            print("- Formato do PDF não é compatível com os padrões reconhecidos")
            print("- Arquivo pode estar corrompido")
            
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    main()
