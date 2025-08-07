import pdfplumber
import pandas as pd
import re
from typing import List, Dict
import os
from datetime import datetime

class PDFExtractor:
    def __init__(self, pdf_path: str):
        """
        Inicializa o extrator de PDF
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
        """
        self.pdf_path = pdf_path
        self.data = []
        
    def extract_data(self) -> List[Dict]:
        """
        Extrai dados do PDF procurando por padrões de placa, data e valores
        
        Returns:
            List[Dict]: Lista de dicionários com os dados extraídos e agregados por placa
        """
        raw_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Processando página {page_num}...")
                    
                    # Tenta extrair tabelas primeiro
                    tables = page.extract_tables()
                    if tables:
                        page_data = self._process_tables(tables, page_num)
                        raw_data.extend(page_data)
                    
                    # Se não encontrar tabelas, processa o texto
                    text = page.extract_text()
                    if text:
                        page_data = self._process_text(text, page_num)
                        raw_data.extend(page_data)
                        
        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
        
        # Mantém os dados separados por placa e data
        self.data = self._process_by_placa_and_date(raw_data)
        return self.data
    
    def _process_tables(self, tables: List, page_num: int) -> List[Dict]:
        """
        Processa tabelas encontradas no PDF
        
        Args:
            tables (List): Lista de tabelas extraídas
            page_num (int): Número da página
            
        Returns:
            List[Dict]: Lista de dados extraídos das tabelas
        """
        extracted_data = []
        
        for table_num, table in enumerate(tables, 1):
            if not table:
                continue
                
            print(f"Processando tabela {table_num} da página {page_num}...")
            
            for row_num, row in enumerate(table):
                if not row or not any(row):
                    continue
                
                # Processa cada linha da tabela
                row_data = self._process_table_row(row, page_num, table_num, row_num)
                if row_data:
                    extracted_data.append(row_data)
        
        return extracted_data
    
    def _process_text(self, text: str, page_num: int) -> List[Dict]:
        """
        Processa texto bruto da página extraindo cada registro individualmente
        Mantém contexto da placa atual para linhas subsequentes
        
        Args:
            text (str): Texto da página
            page_num (int): Número da página
            
        Returns:
            List[Dict]: Lista de dados extraídos do texto
        """
        extracted_data = []
        lines = text.split('\n')
        current_placa = None
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            # Verifica se é uma linha de cabeçalho (ignora)
            if 'PLACA DATA PRODUTO' in line or 'MOTORISTA FROTA' in line:
                continue
                
            # Verifica se é linha de total (ignora)
            if line.strip().startswith('TOTAL R$'):
                current_placa = None  # Reset do contexto após total
                continue
            
            # Verifica se há uma placa na linha atual
            placa_na_linha = self._find_pattern(line, r'\b[A-Z]{3}[-\s]?\d{4}\b|\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b')
            if placa_na_linha:
                current_placa = self._clean_placa(placa_na_linha)
            
            # Tenta extrair dados da linha atual (com contexto da placa)
            line_data = self._extract_line_data_with_context(line, page_num, line_num, current_placa)
            if line_data:
                extracted_data.append(line_data)
        
        return extracted_data
    
    def _extract_line_data_with_context(self, line: str, page_num: int, line_num: int, current_placa: str) -> Dict:
        """
        Extrai dados de uma única linha usando o contexto da placa atual
        
        Args:
            line (str): Linha de texto
            page_num (int): Número da página
            line_num (int): Número da linha
            current_placa (str): Placa atual no contexto
            
        Returns:
            Dict: Dados extraídos da linha ou None se não encontrar dados válidos
        """
        # Procura por placa na linha atual
        placa_na_linha = self._find_pattern(line, r'\b[A-Z]{3}[-\s]?\d{4}\b|\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b')
        
        # Usa a placa da linha ou a placa do contexto
        placa = placa_na_linha if placa_na_linha else current_placa
        
        # Se não temos placa nem no contexto, não processa
        if not placa:
            return None
        
        # Procura por data
        data = self._find_pattern(line, r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b')
        if not data:
            return None
        
        # Procura por valores monetários na linha
        valores = re.findall(r'\d+[.,]\d{2}', line)
        valor = None
        
        if valores:
            # Pega o penúltimo valor (que geralmente é o valor principal)
            # O último valor costuma ser a quantidade
            if len(valores) >= 2:
                valor = valores[-2]  # Penúltimo valor
            else:
                valor = valores[-1]  # Se só tem um valor, usa ele
        
        if valor:
            line_ref = f"linha_{line_num}"
            return {
                'placa': self._clean_placa(placa),
                'data': self._clean_data(data),
                'total': self._clean_valor(valor),
                'texto_original': line,
                'pagina': page_num,
                'linha_referencia': line_ref
            }
        
        return None

    def _extract_line_data(self, line: str, page_num: int, line_num: int) -> Dict:
        """
        Extrai dados de uma única linha
        
        Args:
            line (str): Linha de texto
            page_num (int): Número da página
            line_num (int): Número da linha
            
        Returns:
            Dict: Dados extraídos da linha ou None se não encontrar dados válidos
        """
        # Procura por placa
        placa = self._find_pattern(line, r'\b[A-Z]{3}[-\s]?\d{4}\b|\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b')
        if not placa:
            return None
        
        # Procura por data
        data = self._find_pattern(line, r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b')
        
        # Procura por valor monetário
        valor = self._find_pattern(line, r'R?\$?\s*\d+[.,]\d{2}|\d+[.,]\d{2}')
        
        # Se encontrou placa, cria o registro (mesmo que data/valor estejam vazios)
        if placa:
            placa_limpa = self._clean_placa(placa)
            data_limpa = self._clean_data(data) if data else ''
            valor_limpo = self._clean_valor(valor) if valor else '0,00'
            
            return {
                'placa': placa_limpa,
                'data': data_limpa,
                'total': valor_limpo,
                'texto_original': line.strip(),
                'pagina': page_num,
                'linha_referencia': f"linha_{line_num}"
            }
        
        return None
    
    def _extract_total_value(self, total_line: str) -> str:
        """
        Extrai valor de uma linha TOTAL R$
        
        Args:
            total_line (str): Linha com TOTAL R$
            
        Returns:
            str: Valor extraído
        """
        # Padrão para TOTAL R$ 250,00
        match = re.search(r'TOTAL\s+R\$\s*([\d.,]+)', total_line)
        if match:
            return match.group(1)
        return None
    
    def _get_first_date_from_group(self, group_lines: List[str]) -> str:
        """
        Extrai a primeira data de um grupo de linhas
        
        Args:
            group_lines (List[str]): Linhas do grupo
            
        Returns:
            str: Primeira data encontrada
        """
        for line in group_lines:
            data = self._find_pattern(line, r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b')
            if data:
                return self._clean_data(data)
        return ''
    
    def _estimate_total_from_group(self, group_lines: List[str]) -> str:
        """
        Estima total somando valores individuais do grupo
        
        Args:
            group_lines (List[str]): Linhas do grupo
            
        Returns:
            str: Valor total estimado
        """
        total = 0.0
        
        for line in group_lines:
            # Procura valores na linha (assumindo que o último valor é o total da linha)
            valores = re.findall(r'\d+[.,]\d{2}', line)
            if valores:
                # Pega o maior valor da linha (provavelmente o total)
                maior_valor = max(valores, key=lambda x: self._convert_valor_to_float(x))
                total += self._convert_valor_to_float(maior_valor)
        
        if total > 0:
            return f"{total:.2f}".replace('.', ',')
        
        return None
    
    def _extract_from_row(self, row_values: List, page_num: int, table_num: int) -> Dict:
        """
        Extrai dados de uma linha de tabela
        
        Args:
            row_values (List): Valores da linha
            page_num (int): Número da página
            table_num (int): Número da tabela
            
        Returns:
            Dict: Dicionário com dados extraídos ou None
        """
        if not row_values:
            return None
            
        row_text = ' '.join(str(val) for val in row_values if val)
        return self._extract_from_text_line(row_text, page_num, f"tabela_{table_num}")
    
    def _extract_from_text_line(self, line: str, page_num: int, line_ref: str) -> Dict:
        """
        Extrai dados de uma linha de texto
        
        Args:
            line (str): Linha de texto
            page_num (int): Número da página
            line_ref (str): Referência da linha
            
        Returns:
            Dict: Dicionário com dados extraídos ou None
        """
        # Padrões de regex para identificar os dados
        placa_pattern = r'\b[A-Z]{3}[-\s]?\d{4}\b|\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b'
        data_pattern = r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b'
        valor_pattern = r'R?\$?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2}'
        
        placa = self._find_pattern(line, placa_pattern)
        data = self._find_pattern(line, data_pattern)
        valor = self._find_pattern(line, valor_pattern)
        
        # Se encontrou pelo menos placa e um dos outros campos
        if placa and (data or valor):
            return {
                'placa': self._clean_placa(placa),
                'data': self._clean_data(data) if data else '',
                'total': self._clean_valor(valor) if valor else '',
                'texto_original': line,
                'pagina': page_num,
                'linha_referencia': line_ref
            }
        
        return None
    
    def _find_pattern(self, text: str, pattern: str) -> str:
        """
        Encontra padrão no texto
        
        Args:
            text (str): Texto para buscar
            pattern (str): Padrão regex
            
        Returns:
            str: Primeiro match encontrado ou None
        """
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group() if match else None
    
    def _process_by_placa_and_date(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Processa os dados mantendo registros separados por placa e data
        Diferentes datas para a mesma placa resultam em linhas separadas
        
        Args:
            raw_data (List[Dict]): Dados brutos extraídos
            
        Returns:
            List[Dict]: Dados organizados por placa e data
        """
        if not raw_data:
            return []
        
        print(f"\nProcessando {len(raw_data)} registros por placa e data...")
        
        # Dicionário para agrupar por placa + data
        combined_data = {}
        
        for item in raw_data:
            placa = item.get('placa', '').strip()
            data = item.get('data', '').strip()
            
            if not placa:
                continue
            
            # Chave única: placa + data
            key = f"{placa}|{data}"
            
            # Converte valor para float para soma (se houver múltiplos registros na mesma data)
            valor_str = item.get('total', '').strip()
            valor_float = self._convert_valor_to_float(valor_str)
            
            if key not in combined_data:
                combined_data[key] = {
                    'placa': placa,
                    'data': data,
                    'total_valor': 0.0,
                    'registros_originais': [],
                    'paginas': set(),
                    'total_registros': 0
                }
            
            # Soma valores da mesma placa na mesma data
            combined_data[key]['total_valor'] += valor_float
            combined_data[key]['registros_originais'].append(item.get('texto_original', ''))
            combined_data[key]['paginas'].add(item.get('pagina', 0))
            combined_data[key]['total_registros'] += 1
        
        # Converte para lista de dicionários
        result = []
        for key, dados in combined_data.items():
            placa = dados['placa']
            data = dados['data']
            
            # Formata o valor total
            valor_total_formatado = self._format_currency_br(dados['total_valor'])
            
            # Cria texto original
            if dados['total_registros'] > 1:
                texto_original = f"PLACA: {placa} | DATA: {data} | TOTAL: R$ {valor_total_formatado} | REGISTROS: {dados['total_registros']}"
            else:
                texto_original = f"PLACA: {placa} | DATA: {data} | TOTAL: R$ {valor_total_formatado}"
            
            result.append({
                'placa': placa,
                'data': data,
                'total': valor_total_formatado,
                'texto_original': texto_original,
                'pagina': min(dados['paginas']) if dados['paginas'] else 0,
                'linha_referencia': f"placa_{placa}_data_{data}",
                'registros_individuais': dados['total_registros'],
                'valor_numerico': dados['total_valor']
            })
        
        print(f"Processamento concluído: {len(result)} registros únicos (placa+data)")
        
        # Ordena por placa e depois por data
        result.sort(key=lambda x: (x['placa'], x['data']))
        
        return result

    def _aggregate_by_placa(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Agrega os dados por placa, somando os valores totais de cada placa
        
        Args:
            raw_data (List[Dict]): Dados brutos extraídos
            
        Returns:
            List[Dict]: Dados agregados por placa
        """
        if not raw_data:
            return []
        
        print(f"\nAgregando {len(raw_data)} registros por placa...")
        
        # Dicionário para agrupar por placa
        placas_data = {}
        
        for item in raw_data:
            placa = item.get('placa', '').strip()
            if not placa:
                continue
            
            # Converte valor para float para soma
            valor_str = item.get('total', '').strip()
            valor_float = self._convert_valor_to_float(valor_str)
            
            data = item.get('data', '').strip()
            
            if placa not in placas_data:
                placas_data[placa] = {
                    'placa': placa,
                    'total_valor': 0.0,
                    'datas': set(),
                    'primeira_data': data,
                    'ultima_data': data,
                    'registros_originais': [],
                    'paginas': set(),
                    'total_registros': 0
                }
            
            # Soma o valor
            placas_data[placa]['total_valor'] += valor_float
            
            # Adiciona data se válida
            if data:
                placas_data[placa]['datas'].add(data)
                # Atualiza primeira e última data
                if not placas_data[placa]['primeira_data'] or data < placas_data[placa]['primeira_data']:
                    placas_data[placa]['primeira_data'] = data
                if not placas_data[placa]['ultima_data'] or data > placas_data[placa]['ultima_data']:
                    placas_data[placa]['ultima_data'] = data
            
            # Adiciona informações do registro original
            placas_data[placa]['registros_originais'].append(item.get('texto_original', ''))
            placas_data[placa]['paginas'].add(item.get('pagina', 0))
            placas_data[placa]['total_registros'] += 1
        
        # Converte para lista de dicionários
        result = []
        for placa, dados in placas_data.items():
            # Determina a data a usar (primeira, última, ou mais comum)
            data_final = dados['primeira_data']
            if len(dados['datas']) > 1:
                # Se tem múltiplas datas, usa a primeira
                data_final = dados['primeira_data']
            elif len(dados['datas']) == 1:
                data_final = list(dados['datas'])[0]
            
            # Formata o valor total
            valor_total_formatado = self._format_currency_br(dados['total_valor'])
            
            # Cria texto original agregado
            texto_original = f"PLACA: {placa} | TOTAL: R$ {valor_total_formatado} | REGISTROS: {dados['total_registros']}"
            
            result.append({
                'placa': placa,
                'data': data_final,
                'total': valor_total_formatado,
                'texto_original': texto_original,
                'pagina': min(dados['paginas']) if dados['paginas'] else 0,
                'linha_referencia': f"agregado_{dados['total_registros']}_registros",
                'registros_individuais': dados['total_registros'],
                'valor_numerico': dados['total_valor']
            })
        
        print(f"Agregação concluída: {len(result)} placas únicas encontradas")
        
        # Ordena por placa
        result.sort(key=lambda x: x['placa'])
        
        return result
    
    def _convert_valor_to_float(self, valor_str: str) -> float:
        """
        Converte string de valor para float com tratamento robusto de erros
        
        Args:
            valor_str (str): Valor em string
            
        Returns:
            float: Valor convertido para float
        """
        if not valor_str or valor_str.strip() == '':
            return 0.0
        
        try:
            # Remove R$, espaços e outros caracteres desnecessários
            valor_clean = re.sub(r'[R$\s]', '', str(valor_str).strip())
            
            # Se a string está vazia após limpeza, retorna 0
            if not valor_clean:
                return 0.0
            
            # Detecta se o valor parece ser uma concatenação incorreta
            # Ex: '010.0608030.03060' (múltiplos pontos em posições estranhas)
            if valor_clean.count('.') > 1:
                # Verifica se é um caso de concatenação incorreta
                if len(valor_clean) > 10 and not self._is_valid_currency_format(valor_clean):
                    print(f"Aviso: Valor '{valor_str}' parece ser uma concatenação incorreta, tentando extrair primeiro valor válido")
                    return self._extract_first_valid_value(valor_clean)
            
            # Verifica se tem múltiplas vírgulas (também indica problema)
            if valor_clean.count(',') > 1:
                print(f"Aviso: Valor '{valor_str}' tem múltiplas vírgulas, tentando extrair primeiro valor válido")
                return self._extract_first_valid_value(valor_clean)
            
            # Trata formatação brasileira normal (1.234,56)
            if ',' in valor_clean and '.' in valor_clean:
                # Remove pontos (milhares) e substitui vírgula por ponto (decimal)
                valor_clean = valor_clean.replace('.', '').replace(',', '.')
            elif ',' in valor_clean:
                # Se só tem vírgula, verifica se é decimal ou milhares
                parts = valor_clean.split(',')
                if len(parts) == 2 and len(parts[1]) == 2:
                    # Provavelmente decimal (ex: 100,50)
                    valor_clean = valor_clean.replace(',', '.')
                else:
                    # Provavelmente milhares (ex: 1,000)
                    valor_clean = valor_clean.replace(',', '')
            
            # Última verificação: se ainda contém caracteres não numéricos (exceto ponto)
            if not re.match(r'^\d+\.?\d*$', valor_clean):
                print(f"Aviso: Valor '{valor_str}' contém caracteres inválidos após limpeza: '{valor_clean}'")
                return self._extract_first_valid_value(valor_str)
            
            return float(valor_clean)
            
        except (ValueError, AttributeError) as e:
            print(f"Erro ao converter valor '{valor_str}' para float: {e}")
            return 0.0
    
    def _is_valid_currency_format(self, valor_str: str) -> bool:
        """
        Verifica se uma string tem formato válido de moeda
        
        Args:
            valor_str (str): String a verificar
            
        Returns:
            bool: True se é um formato válido
        """
        # Padrões válidos:
        # 123.45 ou 1234.56 ou 12345.67
        # 1.234,56 ou 12.345,67 ou 123.456,78
        # 123,45 ou 1234,56
        
        patterns = [
            r'^\d{1,3}\.\d{2}$',                    # 123.45
            r'^\d{4,}\.\d{2}$',                     # 1234.56
            r'^\d{1,3}(,\d{3})*\.\d{2}$',         # 1,234.56 (formato americano)
            r'^\d{1,3}(\.\d{3})*,\d{2}$',         # 1.234,56 (formato brasileiro)
            r'^\d+,\d{2}$',                        # 123,45
            r'^\d+$'                               # 123 (inteiro)
        ]
        
        return any(re.match(pattern, valor_str) for pattern in patterns)
    
    def _extract_first_valid_value(self, valor_str: str) -> float:
        """
        Extrai o primeiro valor monetário válido de uma string problemática
        
        Args:
            valor_str (str): String com possível concatenação de valores
            
        Returns:
            float: Primeiro valor válido encontrado
        """
        try:
            # Remove caracteres não numéricos, pontos e vírgulas
            valor_clean = re.sub(r'[^0-9.,]', '', str(valor_str))
            
            # Procura por padrões de valores monetários válidos
            # Padrão brasileiro: 123,45 ou 1.234,56
            br_pattern = r'\d{1,3}(?:\.\d{3})*,\d{2}'
            match = re.search(br_pattern, valor_clean)
            if match:
                found_value = match.group()
                # Converte formato brasileiro para float
                return float(found_value.replace('.', '').replace(',', '.'))
            
            # Padrão americano: 123.45 ou 1,234.56
            us_pattern = r'\d{1,3}(?:,\d{3})*\.\d{2}'
            match = re.search(us_pattern, valor_clean)
            if match:
                found_value = match.group()
                # Converte formato americano para float
                return float(found_value.replace(',', ''))
            
            # Procura por números simples com vírgula decimal
            simple_pattern = r'\d+,\d{2}'
            match = re.search(simple_pattern, valor_clean)
            if match:
                found_value = match.group()
                return float(found_value.replace(',', '.'))
            
            # Procura por números simples com ponto decimal
            simple_pattern = r'\d+\.\d{2}'
            match = re.search(simple_pattern, valor_clean)
            if match:
                found_value = match.group()
                return float(found_value)
            
            # Como último recurso, procura apenas dígitos
            digits = re.findall(r'\d+', valor_clean)
            if digits:
                # Pega o primeiro número encontrado
                first_number = digits[0]
                # Se tem mais de 2 dígitos, assume que os últimos 2 são centavos
                if len(first_number) > 2:
                    return float(f"{first_number[:-2]}.{first_number[-2:]}")
                else:
                    return float(first_number)
            
            print(f"Aviso: Não foi possível extrair valor válido de '{valor_str}'")
            return 0.0
            
        except Exception as e:
            print(f"Erro ao extrair valor de '{valor_str}': {e}")
            return 0.0
    
    def _format_currency_br(self, valor: float) -> str:
        """
        Formata valor para moeda brasileira (R$ 1.234,56)
        
        Args:
            valor (float): Valor numérico
            
        Returns:
            str: Valor formatado em moeda brasileira
        """
        if valor == 0:
            return "0,00"
        
        # Converte para string com 2 casas decimais
        valor_str = f"{valor:.2f}"
        
        # Separa parte inteira e decimal
        partes = valor_str.split('.')
        parte_inteira = partes[0]
        parte_decimal = partes[1]
        
        # Formata parte inteira com separadores de milhares
        if len(parte_inteira) > 3:
            # Adiciona pontos a cada 3 dígitos da direita para esquerda
            parte_inteira_formatada = ""
            for i, digit in enumerate(reversed(parte_inteira)):
                if i > 0 and i % 3 == 0:
                    parte_inteira_formatada = "." + parte_inteira_formatada
                parte_inteira_formatada = digit + parte_inteira_formatada
        else:
            parte_inteira_formatada = parte_inteira
        
        return f"{parte_inteira_formatada},{parte_decimal}"
    
    def _clean_placa(self, placa: str) -> str:
        """
        Limpa e padroniza a placa
        
        Args:
            placa (str): Placa bruta
            
        Returns:
            str: Placa limpa
        """
        if not placa:
            return ''
        
        # Remove espaços e converte para maiúsculo
        placa = re.sub(r'[^A-Z0-9]', '', placa.upper())
        
        # Adiciona hífen se necessário (formato ABC1234 -> ABC-1234)
        if len(placa) == 7 and placa[:3].isalpha() and placa[3:].isdigit():
            placa = f"{placa[:3]}-{placa[3:]}"
        # Formato Mercosul (ABC1D23 -> ABC-1D23)
        elif len(placa) == 7 and placa[:3].isalpha() and placa[3].isdigit() and placa[4].isalpha() and placa[5:].isdigit():
            placa = f"{placa[:3]}-{placa[3:]}"
            
        return placa
    
    def _clean_data(self, data: str) -> str:
        """
        Limpa e padroniza a data
        
        Args:
            data (str): Data bruta
            
        Returns:
            str: Data limpa no formato DD/MM/AAAA
        """
        if not data:
            return ''
            
        # Remove caracteres não numéricos exceto / - .
        data = re.sub(r'[^\d\/\-\.]', '', data)
        
        # Substitui separadores por /
        data = re.sub(r'[-\.]', '/', data)
        
        # Tenta padronizar o ano
        parts = data.split('/')
        if len(parts) == 3:
            dia, mes, ano = parts
            
            # Completa ano com 2 dígitos para 4 dígitos
            if len(ano) == 2:
                current_year = datetime.now().year
                if int(ano) <= (current_year % 100):
                    ano = f"20{ano}"
                else:
                    ano = f"19{ano}"
            
            # Adiciona zero à esquerda se necessário
            dia = dia.zfill(2)
            mes = mes.zfill(2)
            
            return f"{dia}/{mes}/{ano}"
        
        return data
    
    def _clean_valor(self, valor: str) -> str:
        """
        Limpa e padroniza o valor
        
        Args:
            valor (str): Valor bruto
            
        Returns:
            str: Valor limpo
        """
        if not valor:
            return ''
            
        # Remove R$ e espaços
        valor = re.sub(r'R?\$?\s*', '', valor)
        
        # Substitui vírgula por ponto para decimal
        if ',' in valor and '.' in valor:
            # Se tem ambos, assume que vírgula é decimal
            valor = valor.replace('.', '').replace(',', '.')
        elif ',' in valor:
            # Se só tem vírgula, pode ser decimal ou milhares
            parts = valor.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Provavelmente decimal
                valor = valor.replace(',', '.')
        
        return valor
    
    def save_to_excel(self, output_path: str = None):
        """
        Salva os dados extraídos em Excel
        
        Args:
            output_path (str): Caminho do arquivo de saída
        """
        if not self.data:
            print("Nenhum dado encontrado para salvar.")
            return
            
        if not output_path:
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_path = f"{base_name}_dados_extraidos.xlsx"
        
        df = pd.DataFrame(self.data)
        
        # Reordena colunas
        columns_order = ['placa', 'data', 'total', 'texto_original', 'pagina', 'linha_referencia']
        df = df.reindex(columns=columns_order)
        
        df.to_excel(output_path, index=False)
        print(f"Dados salvos em: {output_path}")
    
    def save_to_csv(self, output_path: str = None):
        """
        Salva os dados extraídos em CSV
        
        Args:
            output_path (str): Caminho do arquivo de saída
        """
        if not self.data:
            print("Nenhum dado encontrado para salvar.")
            return
            
        if not output_path:
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_path = f"{base_name}_dados_extraidos.csv"
        
        df = pd.DataFrame(self.data)
        
        # Reordena colunas
        columns_order = ['placa', 'data', 'total', 'texto_original', 'pagina', 'linha_referencia']
        df = df.reindex(columns=columns_order)
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Dados salvos em: {output_path}")
    
    def print_summary(self):
        """
        Exibe um resumo dos dados extraídos
        """
        if not self.data:
            print("Nenhum dado foi extraído.")
            return
            
        print(f"\n=== RESUMO DOS DADOS EXTRAÍDOS ===")
        print(f"Total de placas únicas encontradas: {len(self.data)}")
        
        df = pd.DataFrame(self.data)
        
        # Estatísticas por coluna
        print(f"Registros com data: {len(df[df['data'] != ''])}")
        print(f"Registros com valor: {len(df[df['total'] != ''])}")
        
        # Estatísticas de agregação
        total_registros_individuais = df['registros_individuais'].sum() if 'registros_individuais' in df.columns else len(df)
        print(f"Total de registros individuais processados: {total_registros_individuais}")
        
        # Valor total geral
        if 'valor_numerico' in df.columns:
            valor_total_geral = df['valor_numerico'].sum()
            valor_total_formatado = self._format_currency_br(valor_total_geral)
            print(f"Valor total geral: R$ {valor_total_formatado}")
        
        print(f"\n=== PLACAS E VALORES AGREGADOS ===")
        for i, row in df.iterrows():
            registros_info = f" ({row.get('registros_individuais', 1)} registros)" if 'registros_individuais' in row else ""
            valor_num = f" (R$ {self._format_currency_br(row.get('valor_numerico', 0))})" if 'valor_numerico' in row else ""
            print(f"Placa: {row['placa']} | Data: {row['data']} | Total: R$ {row['total']}{valor_num}{registros_info}")
        
        print(f"\n=== DETALHES DA AGREGAÇÃO ===")
        print(f"Sistema de agregação: ATIVO")
        print(f"Método: Soma por placa única")
        print(f"Registros processados: {total_registros_individuais}")
        print(f"Placas únicas: {len(self.data)}")
        if len(self.data) > 0:
            media_registros = total_registros_individuais / len(self.data)
            print(f"Média de registros por placa: {media_registros:.1f}")


def main():
    """
    Função principal para executar o extrator
    """
    # Caminho do PDF
    pdf_path = "00000002387300 - DEBITOS DETALHADOS.PDF"
    
    if not os.path.exists(pdf_path):
        print(f"Arquivo não encontrado: {pdf_path}")
        return
    
    print(f"Iniciando extração do arquivo: {pdf_path}")
    
    # Cria o extrator
    extractor = PDFExtractor(pdf_path)
    
    # Extrai os dados
    data = extractor.extract_data()
    
    # Exibe resumo
    extractor.print_summary()
    
    if data:
        # Salva os dados
        extractor.save_to_excel()
        extractor.save_to_csv()
    else:
        print("Nenhum dado foi extraído. Verifique o formato do PDF.")


if __name__ == "__main__":
    main()
