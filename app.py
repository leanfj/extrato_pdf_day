#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicação Web para Extração de Dados de PDFs
Flask application with file upload, processing, and data visualization
"""

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
import re
import time
from datetime import datetime
import uuid
from extrator_pdf import PDFExtractor
import tempfile
import zipfile
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'extrator-pdf-2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configurações
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'pdf', 'PDF'}

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Base de dados em memória para jobs de processamento
processing_jobs = {}

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def process_pdf_file(file_path, job_id):
    """Processa um arquivo PDF e retorna os dados extraídos"""
    try:
        # Atualiza status
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['message'] = 'Extraindo dados do PDF...'
        
        # Cria o extrator
        extractor = PDFExtractor(file_path)
        
        # Extrai os dados
        data = extractor.extract_data()
        
        if data:
            # Salva os dados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"dados_extraidos_{job_id}_{timestamp}.xlsx"
            csv_filename = f"dados_extraidos_{job_id}_{timestamp}.csv"
            
            excel_path = os.path.join(RESULTS_FOLDER, excel_filename)
            csv_path = os.path.join(RESULTS_FOLDER, csv_filename)
            
            # Salva arquivos
            extractor.save_to_excel(excel_path)
            extractor.save_to_csv(csv_path)
            
            # Calcula estatísticas
            df = pd.DataFrame(data)
            stats = {
                'total_registros': len(df),
                'placas_unicas': df['placa'].nunique(),
                'registros_com_data': len(df[df['data'] != '']),
                'registros_com_valor': len(df[df['total'] != '']),
                'valor_total': calculate_total_value(df)
            }
            
            # Atualiza status final
            processing_jobs[job_id].update({
                'status': 'completed',
                'message': 'Processamento concluído com sucesso!',
                'data': data,
                'stats': stats,
                'excel_file': excel_filename,
                'csv_file': csv_filename,
                'excel_path': excel_path,
                'csv_path': csv_path
            })
            
        else:
            processing_jobs[job_id].update({
                'status': 'error',
                'message': 'Nenhum dado foi encontrado no PDF. Verifique se o arquivo contém texto extraível.'
            })
            
    except Exception as e:
        processing_jobs[job_id].update({
            'status': 'error',
            'message': f'Erro ao processar o arquivo: {str(e)}'
        })

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

def format_currency_br(valor):
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

def safe_convert_to_float(valor_str):
    """
    Converte string de valor para float de forma segura
    
    Args:
        valor_str (str): Valor em string
        
    Returns:
        float: Valor convertido para float ou 0.0 se erro
    """
    if pd.isna(valor_str) or valor_str == '' or valor_str is None:
        return 0.0
    
    try:
        # Remove caracteres desnecessários
        valor_clean = re.sub(r'[R$\s]', '', str(valor_str).strip())
        
        if not valor_clean:
            return 0.0
        
        # Se tem muitos pontos ou vírgulas, pode ser concatenação incorreta
        if valor_clean.count('.') > 1 or valor_clean.count(',') > 1:
            # Tenta extrair primeiro valor válido
            # Procura por padrão brasileiro: 123,45 ou 1.234,56
            br_match = re.search(r'\d{1,3}(?:\.\d{3})*,\d{2}', valor_clean)
            if br_match:
                found = br_match.group()
                return float(found.replace('.', '').replace(',', '.'))
            
            # Procura por padrão americano: 123.45
            us_match = re.search(r'\d+\.\d{2}', valor_clean)
            if us_match:
                return float(us_match.group())
            
            return 0.0
        
        # Trata formatação normal
        if ',' in valor_clean and '.' in valor_clean:
            # Formato brasileiro: 1.234,56
            valor_clean = valor_clean.replace('.', '').replace(',', '.')
        elif ',' in valor_clean:
            # Verifica se é decimal (123,45) ou milhares (1,234)
            parts = valor_clean.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                valor_clean = valor_clean.replace(',', '.')
            else:
                valor_clean = valor_clean.replace(',', '')
        
        return float(valor_clean)
        
    except (ValueError, AttributeError) as e:
        print(f"Erro ao converter valor '{valor_str}': {e}")
        return 0.0

def calculate_total_value(df):
    """
    Calcula valor total de forma segura
    
    Args:
        df (DataFrame): DataFrame com coluna 'total'
        
    Returns:
        float: Valor total calculado
    """
    try:
        if 'total' not in df.columns or df.empty:
            return 0.0
        
        # Aplica conversão segura para cada valor
        valores_convertidos = df['total'].apply(safe_convert_to_float)
        return valores_convertidos.sum()
        
    except Exception as e:
        print(f"Erro ao calcular valor total: {e}")
        return 0.0

# Função global para usar nos templates
app.jinja_env.globals.update(format_currency_br=format_currency_br)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload e processamento de arquivo"""
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Tipo de arquivo não permitido. Use apenas arquivos PDF.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Gera ID único para o job
        job_id = str(uuid.uuid4())
        
        # Salva o arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{job_id}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Inicializa job de processamento
        processing_jobs[job_id] = {
            'id': job_id,
            'filename': filename,
            'file_path': file_path,
            'status': 'queued',
            'message': 'Arquivo enviado, iniciando processamento...',
            'created_at': datetime.now(),
            'data': [],
            'stats': {}
        }
        
        # Processa o arquivo (em produção, usar Celery ou similar)
        process_pdf_file(file_path, job_id)
        
        flash('Arquivo processado com sucesso!', 'success')
        return redirect(url_for('results', job_id=job_id))
        
    except Exception as e:
        flash(f'Erro ao processar arquivo: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results/<job_id>')
def results(job_id):
    """Página de resultados"""
    if job_id not in processing_jobs:
        flash('Job não encontrado', 'error')
        return redirect(url_for('index'))
    
    job = processing_jobs[job_id]
    return render_template('results.html', job=job)

@app.route('/api/job/<job_id>')
def api_job_status(job_id):
    """API para verificar status do job"""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    job = processing_jobs[job_id]
    
    # Não retorna dados completos na API por performance
    response = {
        'id': job['id'],
        'filename': job['filename'],
        'status': job['status'],
        'message': job['message'],
        'stats': job.get('stats', {})
    }
    
    return jsonify(response)

@app.route('/api/data/<job_id>')
def api_job_data(job_id):
    """API para obter dados do job"""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    job = processing_jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job ainda não foi concluído'}), 400
    
    return jsonify({
        'data': job['data'],
        'stats': job['stats']
    })

@app.route('/download/<job_id>/<file_type>')
def download_file(job_id, file_type):
    """Download de arquivos processados"""
    if job_id not in processing_jobs:
        flash('Job não encontrado', 'error')
        return redirect(url_for('index'))
    
    job = processing_jobs[job_id]
    
    if job['status'] != 'completed':
        flash('Processamento ainda não foi concluído', 'error')
        return redirect(url_for('results', job_id=job_id))
    
    try:
        if file_type == 'excel':
            return send_file(job['excel_path'], as_attachment=True, download_name=job['excel_file'])
        elif file_type == 'csv':
            return send_file(job['csv_path'], as_attachment=True, download_name=job['csv_file'])
        elif file_type == 'both':
            # Cria um ZIP com ambos os arquivos
            memory_file = BytesIO()
            
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(job['excel_path'], job['excel_file'])
                zf.write(job['csv_path'], job['csv_file'])
            
            memory_file.seek(0)
            
            zip_filename = f"dados_extraidos_{job_id}.zip"
            return send_file(
                memory_file,
                mimetype='application/zip',
                as_attachment=True,
                download_name=zip_filename
            )
        else:
            flash('Tipo de arquivo inválido', 'error')
            return redirect(url_for('results', job_id=job_id))
            
    except Exception as e:
        flash(f'Erro ao fazer download: {str(e)}', 'error')
        return redirect(url_for('results', job_id=job_id))

@app.route('/dashboard')
def dashboard():
    """Dashboard com histórico de processamentos"""
    # Ordena jobs por data de criação (mais recentes primeiro)
    jobs_list = sorted(
        processing_jobs.values(),
        key=lambda x: x['created_at'],
        reverse=True
    )
    
    # Estatísticas gerais
    total_jobs = len(jobs_list)
    completed_jobs = len([j for j in jobs_list if j['status'] == 'completed'])
    total_records = sum([j.get('stats', {}).get('total_registros', 0) for j in jobs_list])
    
    dashboard_stats = {
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        'total_records': total_records
    }
    
    return render_template('dashboard.html', jobs=jobs_list, stats=dashboard_stats)

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """API para estatísticas do dashboard"""
    jobs_list = list(processing_jobs.values())
    
    total_jobs = len(jobs_list)
    completed_jobs = len([j for j in jobs_list if j['status'] == 'completed'])
    error_jobs = len([j for j in jobs_list if j['status'] == 'error'])
    processing_jobs_count = len([j for j in jobs_list if j['status'] == 'processing'])
    
    total_records = sum([j.get('stats', {}).get('total_registros', 0) for j in jobs_list])
    total_placas = sum([j.get('stats', {}).get('placas_unicas', 0) for j in jobs_list])
    
    stats = {
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'error_jobs': error_jobs,
        'processing_jobs': processing_jobs_count,
        'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        'total_records': total_records,
        'total_placas': total_placas
    }
    
    return jsonify(stats)

@app.errorhandler(413)
def too_large(e):
    flash('Arquivo muito grande. Tamanho máximo: 50MB', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.route('/health')
def health_check():
    """Health check endpoint para Docker/CasaOS"""
    try:
        # Marca timestamp de início se não existir
        if not hasattr(health_check, 'start_time'):
            health_check.start_time = time.time()
        
        # Verifica se a aplicação está funcionando
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': time.time() - health_check.start_time,
            'checks': {
                'database': 'ok',
                'filesystem': 'ok' if os.path.exists('uploads') and os.path.exists('results') else 'error',
                'imports': 'ok'
            }
        }
        
        # Verifica se consegue importar dependências críticas
        try:
            import pdfplumber
            import pandas as pd
            status['checks']['dependencies'] = 'ok'
        except ImportError as e:
            status['checks']['dependencies'] = f'error: {str(e)}'
            status['status'] = 'unhealthy'
        
        # Verifica espaço em disco
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        status['disk_space_gb'] = round(free_space, 2)
        
        if free_space < 1:  # Menos de 1GB
            status['checks']['disk_space'] = 'warning'
        else:
            status['checks']['disk_space'] = 'ok'
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
