"""
Script para processar e indexar uma amostra rica e representativa dos dados do MIMIC-IV-Note
(discharge.csv.gz e radiology.csv.gz com seus respectivos detalhes)
em um banco SQLite local super rápido (data/explorer.db).
"""

import gzip
import csv
import sqlite3
import re
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'explorer.db')

def extract_radiology_sections(text):
    """Extrai as principais seções de um laudo radiológico (Indication, Findings, Impression, etc.)."""
    sections = {
        'examination': '',
        'indication': '',
        'technique': '',
        'comparison': '',
        'findings': '',
        'impression': ''
    }
    
    # Normalização de quebras de linha
    clean_text = text.replace('\r\n', '\n')
    
    # Regex para capturar seções comuns
    exam_match = re.search(r'EXAMINATION:\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if exam_match:
        sections['examination'] = exam_match.group(1).strip()
        
    ind_match = re.search(r'(?:INDICATION|CLINICAL HISTORY|REASON FOR EXAM):\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if ind_match:
        sections['indication'] = ind_match.group(1).strip()
        
    tech_match = re.search(r'TECHNIQUE:\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if tech_match:
        sections['technique'] = tech_match.group(1).strip()
        
    comp_match = re.search(r'COMPARISON:\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if comp_match:
        sections['comparison'] = comp_match.group(1).strip()
        
    findings_match = re.search(r'FINDINGS:\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if findings_match:
        sections['findings'] = findings_match.group(1).strip()
        
    impression_match = re.search(r'IMPRESSION:\s*(.*?)(?=\n\s*[A-Z\s]{3,20}:|\Z)', clean_text, re.DOTALL | re.IGNORECASE)
    if impression_match:
        sections['impression'] = impression_match.group(1).strip()
        
    return sections

def extract_discharge_sections(text):
    """Extrai as principais seções de um sumário de alta hospitalar."""
    sections = {
        'service': '',
        'chief_complaint': '',
        'history_present_illness': '',
        'past_medical_history': '',
        'brief_hospital_course': '',
        'discharge_diagnosis': '',
        'discharge_condition': '',
        'discharge_instructions': ''
    }
    
    clean_text = text.replace('\r\n', '\n')
    
    patterns = {
        'service': r'Service:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'chief_complaint': r'Chief Complaint:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'history_present_illness': r'History of Present Illness:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'past_medical_history': r'Past Medical History:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'brief_hospital_course': r'Brief Hospital Course:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'discharge_diagnosis': r'Discharge Diagnosis:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'discharge_condition': r'Discharge Condition:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)',
        'discharge_instructions': r'Discharge Instructions:\s*(.*?)(?=\n[A-Z][A-Za-z\s]{2,25}:|\Z)'
    }
    
    for key, pattern in patterns.items():
        m = re.search(pattern, clean_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections[key] = m.group(1).strip()
            
    return sections

def build_explorer_database(max_discharge=6000, max_radiology=18000):
    start_time = time.time()
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
            
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Tabela de Sumários de Alta (Discharge)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS discharge_notes (
        note_id TEXT PRIMARY KEY,
        subject_id TEXT,
        hadm_id TEXT,
        note_type TEXT,
        note_seq INTEGER,
        charttime TEXT,
        storetime TEXT,
        text TEXT,
        word_count INTEGER,
        service TEXT,
        chief_complaint TEXT,
        history_present_illness TEXT,
        past_medical_history TEXT,
        brief_hospital_course TEXT,
        discharge_diagnosis TEXT,
        discharge_instructions TEXT
    )
    ''')
    
    # 2. Tabela de Laudos Radiológicos (Radiology)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS radiology_notes (
        note_id TEXT PRIMARY KEY,
        subject_id TEXT,
        hadm_id TEXT,
        note_type TEXT,
        note_seq INTEGER,
        charttime TEXT,
        storetime TEXT,
        text TEXT,
        word_count INTEGER,
        exam_name TEXT,
        examination_sec TEXT,
        indication_sec TEXT,
        technique_sec TEXT,
        comparison_sec TEXT,
        findings_sec TEXT,
        impression_sec TEXT
    )
    ''')
    
    conn.commit()
    
    # 3. Carregar mapeamento de exam_name de radiology_detail
    print("-> Carregando nomes dos exames de radiology_detail.csv.gz...")
    rad_exam_names = {}
    rad_detail_path = os.path.join(data_dir, 'radiology_detail.csv.gz')
    with gzip.open(rad_detail_path, 'rt', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row['field_name'] == 'exam_name':
                rad_exam_names[row['note_id']] = row['field_value']
            if len(rad_exam_names) >= 60000:
                break
    print(f"   Carregados {len(rad_exam_names)} mapeamentos de exames radiológicos.")
    
    # 4. Ingerir Discharge Summaries
    print(f"-> Ingerindo até {max_discharge} sumários de alta (discharge.csv.gz)...")
    discharge_path = os.path.join(data_dir, 'discharge.csv.gz')
    discharge_hadms = set()
    discharge_subjects = set()
    discharge_batch = []
    
    with gzip.open(discharge_path, 'rt', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            text = row['text']
            word_count = len(text.split())
            sec = extract_discharge_sections(text)
            
            discharge_batch.append((
                row['note_id'],
                row['subject_id'],
                row['hadm_id'],
                row['note_type'],
                int(row['note_seq']) if row['note_seq'].isdigit() else 0,
                row['charttime'],
                row['storetime'],
                text,
                word_count,
                sec['service'],
                sec['chief_complaint'],
                sec['history_present_illness'],
                sec['past_medical_history'],
                sec['brief_hospital_course'],
                sec['discharge_diagnosis'],
                sec['discharge_instructions']
            ))
            
            if row['hadm_id']:
                discharge_hadms.add(row['hadm_id'])
            if row['subject_id']:
                discharge_subjects.add(row['subject_id'])
                
            if len(discharge_batch) >= 500:
                cur.executemany('''
                INSERT OR IGNORE INTO discharge_notes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', discharge_batch)
                discharge_batch = []
                
            if i + 1 >= max_discharge:
                break
                
    if discharge_batch:
        cur.executemany('''
        INSERT OR IGNORE INTO discharge_notes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', discharge_batch)
        
    conn.commit()
    print(f"   Total de {cur.execute('SELECT COUNT(*) FROM discharge_notes').fetchone()[0]} sumários de alta inseridos.")
    print(f"   Internações distintas rastreadas: {len(discharge_hadms)}.")

    # 5. Ingerir Laudos Radiológicos (priorizando internamentos e pacientes com discharge)
    print(f"-> Ingerindo até {max_radiology} laudos radiológicos (radiology.csv.gz)...")
    radiology_path = os.path.join(data_dir, 'radiology.csv.gz')
    rad_batch = []
    rad_count = 0
    
    with gzip.open(radiology_path, 'rt', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            hadm = row['hadm_id']
            subj = row['subject_id']
            
            # Priorizamos se pertencer a pacientes ou internações já capturadas, ou completamos
            is_priority = (hadm in discharge_hadms) or (subj in discharge_subjects)
            
            if is_priority or rad_count < max_radiology // 2 or i % 3 == 0:
                text = row['text']
                word_count = len(text.split())
                sec = extract_radiology_sections(text)
                exam_name = rad_exam_names.get(row['note_id'], sec['examination'] or 'RADIOLOGY EXAM')
                
                rad_batch.append((
                    row['note_id'],
                    row['subject_id'],
                    row['hadm_id'],
                    row['note_type'],
                    int(row['note_seq']) if row['note_seq'].isdigit() else 0,
                    row['charttime'],
                    row['storetime'],
                    text,
                    word_count,
                    exam_name,
                    sec['examination'],
                    sec['indication'],
                    sec['technique'],
                    sec['comparison'],
                    sec['findings'],
                    sec['impression']
                ))
                rad_count += 1
                
                if len(rad_batch) >= 500:
                    cur.executemany('''
                    INSERT OR IGNORE INTO radiology_notes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ''', rad_batch)
                    rad_batch = []
                    
            if rad_count >= max_radiology:
                break
                
    if rad_batch:
        cur.executemany('''
        INSERT OR IGNORE INTO radiology_notes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', rad_batch)
        
    conn.commit()
    print(f"   Total de {cur.execute('SELECT COUNT(*) FROM radiology_notes').fetchone()[0]} laudos radiológicos inseridos.")

    # 6. Criar Índices para busca instantânea
    print("-> Criando índices para performance relacional...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ds_hadm ON discharge_notes(hadm_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ds_subj ON discharge_notes(subject_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rad_hadm ON radiology_notes(hadm_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rad_subj ON radiology_notes(subject_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rad_exam ON radiology_notes(exam_name)")
    
    # 7. Tabela de Pares Conectados (Internações com Ambos os Laudos)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS paired_admissions AS
    SELECT 
        d.hadm_id,
        d.subject_id,
        d.note_id as discharge_note_id,
        COUNT(r.note_id) as radiology_count,
        GROUP_CONCAT(DISTINCT r.exam_name) as exam_list
    FROM discharge_notes d
    JOIN radiology_notes r ON d.hadm_id = r.hadm_id AND d.hadm_id IS NOT NULL AND d.hadm_id != ''
    GROUP BY d.hadm_id, d.subject_id, d.note_id
    ''')
    cur.execute("CREATE INDEX IF NOT EXISTS idx_paired_hadm ON paired_admissions(hadm_id)")
    
    conn.commit()
    paired_count = cur.execute("SELECT COUNT(*) FROM paired_admissions").fetchone()[0]
    print(f"   {paired_count} internações com laudos radiológicos E sumário de alta vinculados!")
    
    conn.close()
    elapsed = time.time() - start_time
    print(f"===> Base de dados de exploração criada com sucesso em {elapsed:.2f}s!")
    print(f"===> Arquivo gerado: {DB_PATH} ({os.path.getsize(DB_PATH) / (1024*1024):.2f} MB)")

if __name__ == '__main__':
    build_explorer_database()
