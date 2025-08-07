#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da nova funcionalidade de extração por placa e data
Demonstra a diferença entre agregação e separação por data
"""

from extrator_pdf import PDFExtractor
import os

def test_new_functionality():
    """Testa a nova funcionalidade de separação por placa e data"""
    
    # Procura por um PDF no diretório atual
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') or f.endswith('.PDF')]
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado no diretório atual")
        print("📋 Para testar, coloque um PDF na raiz do projeto")
        return
    
    pdf_file = pdf_files[0]
    print(f"🔍 Testando com arquivo: {pdf_file}")
    
    try:
        # Cria o extrator
        extractor = PDFExtractor(pdf_file)
        
        # Extrai os dados com a nova lógica
        print("\n📊 NOVA LÓGICA - Separação por Placa + Data:")
        data = extractor.extract_data()
        
        if data:
            print(f"✅ Encontrados {len(data)} registros únicos (placa+data)")
            
            # Mostra alguns exemplos
            print("\n📋 Exemplos dos primeiros registros:")
            for i, item in enumerate(data[:5], 1):
                print(f"  {i}. Placa: {item['placa']} | Data: {item['data']} | Valor: {item['total']}")
            
            # Conta quantas placas únicas
            placas_unicas = set(item['placa'] for item in data)
            print(f"\n🚗 Total de placas únicas: {len(placas_unicas)}")
            
            # Mostra placas com múltiplas datas
            placas_multiplas_datas = {}
            for item in data:
                placa = item['placa']
                if placa not in placas_multiplas_datas:
                    placas_multiplas_datas[placa] = set()
                placas_multiplas_datas[placa].add(item['data'])
            
            placas_com_multiplas = {p: datas for p, datas in placas_multiplas_datas.items() if len(datas) > 1}
            
            if placas_com_multiplas:
                print(f"\n📅 Placas com múltiplas datas ({len(placas_com_multiplas)}):")
                for placa, datas in list(placas_com_multiplas.items())[:3]:
                    print(f"  🚗 {placa}: {', '.join(sorted(datas))}")
            else:
                print("\n📅 Nenhuma placa encontrada com múltiplas datas neste PDF")
            
            # Salva arquivos de exemplo
            print("\n💾 Salvando arquivos de exemplo...")
            extractor.save_to_excel("teste_nova_logica.xlsx")
            extractor.save_to_csv("teste_nova_logica.csv")
            print("✅ Arquivos salvos: teste_nova_logica.xlsx e teste_nova_logica.csv")
            
        else:
            print("❌ Nenhum dado extraído do PDF")
            
    except Exception as e:
        print(f"❌ Erro ao processar PDF: {e}")

def explain_changes():
    """Explica as mudanças implementadas"""
    print("🔄 MUDANÇAS IMPLEMENTADAS:")
    print()
    print("ANTES (Agregação por placa):")
    print("  • Uma linha por placa")
    print("  • Valores somados independente da data")
    print("  • Resultado: ABC1234 | 10/01 | R$ 500,00 (soma de todas as datas)")
    print()
    print("AGORA (Separação por placa + data):")
    print("  • Uma linha por combinação placa+data")
    print("  • Valores mantidos separados por data")
    print("  • Resultado:")
    print("    - ABC1234 | 10/01 | R$ 200,00")
    print("    - ABC1234 | 15/01 | R$ 150,00")
    print("    - ABC1234 | 20/01 | R$ 150,00")
    print()
    print("✅ BENEFÍCIOS:")
    print("  • Maior precisão nos dados")
    print("  • Rastreabilidade por data")
    print("  • Melhor análise temporal")
    print("  • Dados mais granulares")

if __name__ == "__main__":
    print("🚀 TESTE DA NOVA FUNCIONALIDADE DE EXTRAÇÃO")
    print("=" * 50)
    
    explain_changes()
    
    print("\n" + "=" * 50)
    
    test_new_functionality()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
    print("📝 A aplicação web agora mantém registros separados por data!")
