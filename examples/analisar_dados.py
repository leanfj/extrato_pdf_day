#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para análise dos dados extraídos dos PDFs.
Gera relatórios e estatísticas dos dados.
"""

import pandas as pd
import os
import sys
from datetime import datetime

def analisar_dados(arquivo_dados):
    """
    Analisa os dados extraídos e gera relatórios
    
    Args:
        arquivo_dados (str): Caminho para o arquivo CSV ou Excel com os dados
    """
    
    try:
        # Lê o arquivo
        if arquivo_dados.endswith('.xlsx'):
            df = pd.read_excel(arquivo_dados)
        elif arquivo_dados.endswith('.csv'):
            df = pd.read_csv(arquivo_dados, encoding='utf-8-sig')
        else:
            print("❌ Formato de arquivo não suportado. Use .xlsx ou .csv")
            return
        
        print(f"📊 ANÁLISE DOS DADOS: {os.path.basename(arquivo_dados)}")
        print("=" * 60)
        
        # Informações básicas
        print(f"📋 INFORMAÇÕES GERAIS:")
        print(f"  Total de registros: {len(df)}")
        print(f"  Colunas: {list(df.columns)}")
        
        if 'placa' in df.columns:
            placas_unicas = df['placa'].nunique()
            print(f"  Placas únicas: {placas_unicas}")
            
            # Top 10 placas com mais registros
            if placas_unicas > 1:
                print(f"\n🚗 TOP 10 PLACAS COM MAIS REGISTROS:")
                top_placas = df['placa'].value_counts().head(10)
                for i, (placa, count) in enumerate(top_placas.items(), 1):
                    print(f"  {i:2d}. {placa}: {count} registro(s)")
        
        # Análise de datas
        if 'data' in df.columns and not df['data'].isna().all():
            print(f"\n📅 ANÁLISE DE DATAS:")
            datas_validas = df[df['data'] != '']['data']
            
            if len(datas_validas) > 0:
                print(f"  Registros com data: {len(datas_validas)}")
                
                # Converte datas
                try:
                    datas_convertidas = pd.to_datetime(datas_validas, format='%d/%m/%Y', errors='coerce')
                    datas_validas_conv = datas_convertidas.dropna()
                    
                    if len(datas_validas_conv) > 0:
                        print(f"  Data mais antiga: {datas_validas_conv.min().strftime('%d/%m/%Y')}")
                        print(f"  Data mais recente: {datas_validas_conv.max().strftime('%d/%m/%Y')}")
                        
                        # Análise por mês
                        if len(datas_validas_conv) > 1:
                            datas_por_mes = datas_validas_conv.dt.to_period('M').value_counts().sort_index()
                            print(f"\n📈 REGISTROS POR MÊS:")
                            for periodo, count in datas_por_mes.items():
                                print(f"  {periodo}: {count} registro(s)")
                
                except Exception as e:
                    print(f"  ⚠️  Erro ao processar datas: {e}")
        
        # Análise de valores
        if 'total' in df.columns and not df['total'].isna().all():
            print(f"\n💰 ANÁLISE DE VALORES:")
            valores_validos = df[df['total'] != '']['total']
            
            if len(valores_validos) > 0:
                print(f"  Registros com valor: {len(valores_validos)}")
                
                try:
                    # Converte valores para float
                    valores_numericos = valores_validos.str.replace(',', '.').astype(float)
                    valores_limpos = valores_numericos.dropna()
                    
                    if len(valores_limpos) > 0:
                        print(f"  Valor total: R$ {valores_limpos.sum():,.2f}")
                        print(f"  Valor médio: R$ {valores_limpos.mean():,.2f}")
                        print(f"  Valor mínimo: R$ {valores_limpos.min():,.2f}")
                        print(f"  Valor máximo: R$ {valores_limpos.max():,.2f}")
                        
                        # Faixas de valores
                        print(f"\n💵 DISTRIBUIÇÃO POR FAIXAS DE VALOR:")
                        faixas = [0, 10, 25, 50, 100, 200, float('inf')]
                        labels = ['Até R$ 10', 'R$ 10-25', 'R$ 25-50', 'R$ 50-100', 'R$ 100-200', 'Acima R$ 200']
                        
                        distribuicao = pd.cut(valores_limpos, bins=faixas, labels=labels, right=False)
                        contagem_faixas = distribuicao.value_counts().sort_index()
                        
                        for faixa, count in contagem_faixas.items():
                            if count > 0:
                                print(f"  {faixa}: {count} registro(s)")
                
                except Exception as e:
                    print(f"  ⚠️  Erro ao processar valores: {e}")
        
        # Análise por arquivo fonte (se existe)
        if 'arquivo_fonte' in df.columns:
            print(f"\n📁 ANÁLISE POR ARQUIVO:")
            por_arquivo = df['arquivo_fonte'].value_counts()
            for arquivo, count in por_arquivo.items():
                print(f"  {arquivo}: {count} registro(s)")
        
        # Análise de qualidade dos dados
        print(f"\n🔍 QUALIDADE DOS DADOS:")
        for coluna in ['placa', 'data', 'total']:
            if coluna in df.columns:
                vazios = (df[coluna] == '').sum() + df[coluna].isna().sum()
                preenchidos = len(df) - vazios
                percentual = (preenchidos / len(df)) * 100
                print(f"  {coluna}: {preenchidos}/{len(df)} ({percentual:.1f}%) preenchidos")
        
        # Sugestões de melhorias
        print(f"\n💡 SUGESTÕES:")
        
        if 'placa' in df.columns:
            placas_vazias = (df['placa'] == '').sum()
            if placas_vazias > 0:
                print(f"  - {placas_vazias} registros sem placa identificada")
        
        if 'data' in df.columns:
            datas_vazias = (df['data'] == '').sum()
            if datas_vazias > 0:
                print(f"  - {datas_vazias} registros sem data identificada")
        
        if 'total' in df.columns:
            valores_vazios = (df['total'] == '').sum()
            if valores_vazios > 0:
                print(f"  - {valores_vazios} registros sem valor identificado")
        
        # Gera relatório em arquivo
        gerar_relatorio_detalhado(df, arquivo_dados)
        
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")

def gerar_relatorio_detalhado(df, arquivo_original):
    """
    Gera um relatório detalhado em Excel
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base = os.path.splitext(os.path.basename(arquivo_original))[0]
        arquivo_relatorio = f"relatorio_{nome_base}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(arquivo_relatorio, engine='openpyxl') as writer:
            # Aba principal com todos os dados
            df.to_excel(writer, sheet_name='Dados Completos', index=False)
            
            # Aba com resumo por placa
            if 'placa' in df.columns and 'total' in df.columns:
                try:
                    df_valores = df.copy()
                    df_valores['total_numerico'] = pd.to_numeric(
                        df_valores['total'].str.replace(',', '.'), errors='coerce'
                    )
                    
                    resumo_placas = df_valores.groupby('placa').agg({
                        'total_numerico': ['count', 'sum', 'mean'],
                        'data': lambda x: ', '.join(x.dropna().unique())
                    }).round(2)
                    
                    resumo_placas.columns = ['Qtd_Registros', 'Total_Valor', 'Valor_Medio', 'Datas']
                    resumo_placas = resumo_placas.sort_values('Total_Valor', ascending=False)
                    
                    resumo_placas.to_excel(writer, sheet_name='Resumo por Placa')
                except:
                    pass
            
            # Aba com estatísticas gerais
            estatisticas = {
                'Métrica': [
                    'Total de Registros',
                    'Placas Únicas',
                    'Registros com Data',
                    'Registros com Valor',
                    'Completude (%)'
                ],
                'Valor': [
                    len(df),
                    df['placa'].nunique() if 'placa' in df.columns else 'N/A',
                    len(df[df['data'] != '']) if 'data' in df.columns else 'N/A',
                    len(df[df['total'] != '']) if 'total' in df.columns else 'N/A',
                    f"{((len(df) - (df['placa'] == '').sum() - (df['data'] == '').sum() - (df['total'] == '').sum()) / (len(df) * 3) * 100):.1f}%" if all(col in df.columns for col in ['placa', 'data', 'total']) else 'N/A'
                ]
            }
            
            df_stats = pd.DataFrame(estatisticas)
            df_stats.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        print(f"\n📄 RELATÓRIO DETALHADO SALVO: {arquivo_relatorio}")
        
    except Exception as e:
        print(f"⚠️  Erro ao gerar relatório: {e}")

def main():
    print("📊 ANALISADOR DE DADOS EXTRAÍDOS")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        # Lista arquivos disponíveis
        arquivos_dados = []
        for ext in ['*.csv', '*.xlsx']:
            arquivos_dados.extend([f for f in os.listdir('.') if f.endswith(ext.replace('*', ''))])
        
        if arquivos_dados:
            print("📁 Arquivos de dados encontrados:")
            for i, arquivo in enumerate(arquivos_dados, 1):
                print(f"  {i}. {arquivo}")
            
            escolha = input(f"\nEscolha um arquivo (1-{len(arquivos_dados)}) ou digite o nome: ").strip()
            
            try:
                if escolha.isdigit():
                    arquivo_escolhido = arquivos_dados[int(escolha) - 1]
                else:
                    arquivo_escolhido = escolha
            except (IndexError, ValueError):
                print("❌ Escolha inválida.")
                return
        else:
            arquivo_escolhido = input("Digite o caminho do arquivo de dados: ").strip()
    else:
        arquivo_escolhido = sys.argv[1]
    
    if not os.path.exists(arquivo_escolhido):
        print(f"❌ Arquivo não encontrado: {arquivo_escolhido}")
        return
    
    analisar_dados(arquivo_escolhido)

if __name__ == "__main__":
    main()
