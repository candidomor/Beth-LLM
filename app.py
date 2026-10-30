import streamlit as st
import sqlite3
import pandas as pd
import os
import re

# Configuração da página
st.set_page_config(
    page_title="MIMIC-IV-Note Explorer | Mestrado LLM",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para ambiente clínico e acadêmico
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .clinical-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-rad {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    .badge-ds {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-findings {
        background-color: #e0f2fe;
        color: #0369a1;
        border-left: 4px solid #0284c7;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .badge-impression {
        background-color: #ecfdf5;
        color: #047857;
        border-left: 4px solid #10b981;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .badge-indication {
        background-color: #fffbeb;
        color: #b45309;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .badge-course {
        background-color: #f5f3ff;
        color: #6d28d9;
        border-left: 4px solid #8b5cf6;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .metric-box {
        background: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        padding: 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .highlight-id {
        font-family: monospace;
        font-size: 0.95rem;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'explorer.db')

def get_connection():
    if not os.path.exists(DB_PATH):
        st.error(f"Banco de dados não encontrado em {DB_PATH}. Execute `python prepare_db.py` primeiro!")
        st.stop()
    return sqlite3.connect(DB_PATH)

@st.cache_data
def load_overview_stats():
    conn = get_connection()
    c = conn.cursor()
    total_ds = c.execute("SELECT COUNT(*) FROM discharge_notes").fetchone()[0]
    total_rad = c.execute("SELECT COUNT(*) FROM radiology_notes").fetchone()[0]
    paired_admissions = c.execute("SELECT COUNT(*) FROM paired_admissions").fetchone()[0]
    avg_rad_words = c.execute("SELECT ROUND(AVG(word_count)) FROM radiology_notes").fetchone()[0]
    avg_ds_words = c.execute("SELECT ROUND(AVG(word_count)) FROM discharge_notes").fetchone()[0]
    
    top_exams = pd.read_sql_query("""
        SELECT exam_name as 'Tipo de Exame', COUNT(*) as 'Quantidade'
        FROM radiology_notes
        GROUP BY exam_name
        ORDER BY Quantidade DESC
        LIMIT 10
    """, conn)
    
    conn.close()
    return {
        'total_ds': total_ds,
        'total_rad': total_rad,
        'paired_admissions': paired_admissions,
        'avg_rad_words': avg_rad_words,
        'avg_ds_words': avg_ds_words,
        'top_exams': top_exams
    }

# Cabeçalho Principal
col_title, col_info = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-header">🩺 MIMIC-IV-Note Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Mestrado em Computação Aplicada | Modelos Generativos e de Linguagem | Projeto Final (45 dias)</div>', unsafe_allow_html=True)
with col_info:
    st.info("🎓 **Tema**: Avaliando a Qualidade de Laudos Médicos com LLMs abertos")

# Abas de navegação
tab_overview, tab_radiology, tab_discharge, tab_integrated, tab_academic, tab_sandbox = st.tabs([
    "📊 Visão Geral dos Dados",
    "🩻 Laudos Radiológicos (Radiology)",
    "📋 Sumários de Alta (Discharge)",
    "🔗 Prontuário Integrado (Linha do Tempo)",
    "🎓 Guia do Projeto & 4 Caminhos (45 dias)",
    "🧪 Sandbox do Pipeline de Qualidade"
])

# ==========================================
# ABA 1: VISÃO GERAL DOS DADOS
# ==========================================
with tab_overview:
    stats = load_overview_stats()
    
    st.markdown("### 📈 Estatísticas do Repositório Local Indexado")
    st.markdown("Os dados abaixo foram indexados diretamente a partir dos arquivos brutos comprimidos (`discharge.csv.gz`, `radiology.csv.gz` e detalhes) da base de dados **MIMIC-IV-Note v2.2**:")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">{stats['total_rad']:,}</div>
            <div class="metric-label">Laudos Radiológicos</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">{stats['total_ds']:,}</div>
            <div class="metric-label">Sumários de Alta</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number" style="color: #059669;">{stats['paired_admissions']:,}</div>
            <div class="metric-label">Internações Conectadas</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">{int(stats['avg_rad_words'])}</div>
            <div class="metric-label">Média Palavras (Radiologia)</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">{int(stats['avg_ds_words'])}</div>
            <div class="metric-label">Média Palavras (Sumário Alta)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_chart, col_desc = st.columns([3, 2])
    with col_chart:
        st.subheader("📊 Top 10 Tipos de Exames de Imagem mais Frequentes")
        st.bar_chart(data=stats['top_exams'].set_index('Tipo de Exame'), color="#2563eb")
        
    with col_desc:
        st.subheader("💡 Como os Bancos se Conectam?")
        st.markdown("""
        O MIMIC-IV-Note organiza o fluxo hospitalar através de identificadores relacionais chaves:
        
        - **`subject_id`**: Identificador único do paciente (um paciente pode ter múltiplas internações ao longo da vida).
        - **`hadm_id`**: Identificador da internação hospitalar (*Hospital Admission*).
        - **`note_id`**: Identificador único de cada laudo emitido.
        - **`radiology.csv.gz`**: Contém exames de imagem (Raio-X, Tomografia, Ultrassom, Ressonância) realizados durante ou antes da internação.
        - **`discharge.csv.gz`**: Contém o sumário final emitido pelo médico quando o paciente recebe alta hospitalar, resumindo o quadro clínico, medicações e diagnósticos.
        
        > **Oportunidade para o Projeto**: As **2.190 internações conectadas** contêm tanto os laudos de imagem quanto o sumário de alta correspondente, permitindo auditorias de consistência cruzada entre documentos clínicos!
        """)

# ==========================================
# ABA 2: EXPLORADOR DE LAUDOS RADIOLÓGICOS
# ==========================================
with tab_radiology:
    st.subheader("🩻 Navegador Inteligente de Laudos Radiológicos")
    st.markdown("Consulte laudos de imagem estruturados em seções clínicas padronizadas (**Indicação**, **Achados** e **Impressão**).")
    
    conn = get_connection()
    c = conn.cursor()
    
    exam_types = [row[0] for row in c.execute("SELECT DISTINCT exam_name FROM radiology_notes WHERE exam_name != '' ORDER BY exam_name").fetchall()]
    
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        selected_exam = st.selectbox("Filtrar por Tipo de Exame:", ["(Todos os Exames)"] + exam_types)
    with col_f2:
        search_query = st.text_input("Buscar termo nos Achados ou Impressão:", placeholder="Ex: pneumonia, fracture, nodule, edema, normal")
    with col_f3:
        only_with_findings = st.checkbox("Apenas com 'Findings' explícitos", value=True)
        
    # Construção da Query
    query = """
        SELECT note_id, subject_id, hadm_id, exam_name, charttime, word_count, 
               indication_sec, technique_sec, comparison_sec, findings_sec, impression_sec, text
        FROM radiology_notes
        WHERE 1=1
    """
    params = []
    
    if selected_exam != "(Todos os Exames)":
        query += " AND exam_name = ?"
        params.append(selected_exam)
        
    if search_query:
        query += " AND (findings_sec LIKE ? OR impression_sec LIKE ? OR text LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])
        
    if only_with_findings:
        query += " AND findings_sec != '' AND impression_sec != ''"
        
    query += " ORDER BY charttime DESC LIMIT 50"
    
    df_rad = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df_rad.empty:
        st.warning("Nenhum laudo encontrado com os filtros selecionados. Tente ajustar os termos de busca.")
    else:
        st.write(f"Mostrando **{len(df_rad)}** laudos encontrados (amostra rápida):")
        
        # Seletor de laudo
        options = [f"{row['note_id']} | {row['exam_name']} | Data: {row['charttime']} | {row['word_count']} palavras" for _, row in df_rad.iterrows()]
        selected_idx = st.selectbox("Selecione um laudo para visualizar detalhadamente:", range(len(options)), format_func=lambda i: options[i])
        
        sel_row = df_rad.iloc[selected_idx]
        
        st.markdown("---")
        
        # Metadados do Laudo
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"**ID do Laudo**: <span class='highlight-id'>{sel_row['note_id']}</span>", unsafe_allow_html=True)
        m2.markdown(f"**Paciente (Subject ID)**: <span class='highlight-id'>{sel_row['subject_id']}</span>", unsafe_allow_html=True)
        m3.markdown(f"**Internação (HADM ID)**: <span class='highlight-id'>{sel_row['hadm_id'] or 'Ambulatorial / PS'}</span>", unsafe_allow_html=True)
        m4.markdown(f"**Data/Hora**: {sel_row['charttime']}")
        
        tab_structured, tab_raw = st.tabs(["✨ Visualização Humanizada (Estruturada)", "📄 Texto Bruto Original (Raw)"])
        
        with tab_structured:
            st.markdown(f"### 🎯 Exame: `{sel_row['exam_name']}`")
            
            # Indicação
            if sel_row['indication_sec']:
                st.markdown("**🩺 Indicação Clínica (Motivo do Exame / Hipótese):**")
                st.markdown(f"<div class='badge-indication'>{sel_row['indication_sec']}</div>", unsafe_allow_html=True)
            
            # Técnica / Comparação
            if sel_row['technique_sec'] or sel_row['comparison_sec']:
                col_tech, col_comp = st.columns(2)
                with col_tech:
                    if sel_row['technique_sec']:
                        st.markdown(f"**⚙️ Técnica**: {sel_row['technique_sec']}")
                with col_comp:
                    if sel_row['comparison_sec']:
                        st.markdown(f"**🔄 Comparação com Exames Anteriores**: {sel_row['comparison_sec']}")
            
            # Achados Detalhados (Findings)
            st.markdown("**🔍 Achados Detalhados (Findings - O que o radiologista observou):**")
            if sel_row['findings_sec']:
                st.markdown(f"<div class='badge-findings'>{sel_row['findings_sec']}</div>", unsafe_allow_html=True)
            else:
                st.info("Este laudo possui os achados integrados diretamente no corpo do texto ou na impressão.")
                
            # Impressão Diagnóstica (Impression)
            st.markdown("**💡 Impressão Diagnóstica (Impression - Conclusão do Laudo):**")
            if sel_row['impression_sec']:
                st.markdown(f"<div class='badge-impression'><strong>{sel_row['impression_sec']}</strong></div>", unsafe_allow_html=True)
            else:
                st.info("Sem seção explícita de IMPRESSION separada.")
                
            # Insight Clínico para LLM
            with st.expander("🤖 Ideia de Aplicação de LLM neste laudo"):
                st.markdown("""
                **Tarefa Clássica de Avaliação de Qualidade:**
                - **Consistência Findings -> Impression**: O modelo de LLM aberta recebe os *Achados* (`Findings`) e deve avaliar se a *Impressão* (`Impression`):
                  1. Omitiu algum achado relevante citado nos Achados (ex: não mencionou um nódulo ou consolidação).
                  2. Alucinou alguma patologia que não estava descrita nos Achados.
                  3. Utilizou classificação diagnóstica adequada.
                """)
        
        with tab_raw:
            st.code(sel_row['text'], language='text')

# ==========================================
# ABA 3: EXPLORADOR DE SUMÁRIOS DE ALTA
# ==========================================
with tab_discharge:
    st.subheader("📋 Navegador de Sumários de Alta (Discharge Summaries)")
    st.markdown("Os sumários de alta reúnem todo o histórico do paciente durante a hospitalização, seus diagnósticos e condutas.")
    
    conn = get_connection()
    c = conn.cursor()
    
    services = [row[0] for row in c.execute("SELECT DISTINCT service FROM discharge_notes WHERE service != '' ORDER BY service").fetchall()]
    
    col_ds1, col_ds2 = st.columns([1, 2])
    with col_ds1:
        selected_service = st.selectbox("Filtrar por Especialidade/Serviço:", ["(Todos)"] + services)
    with col_ds2:
        ds_search = st.text_input("Buscar por diagnóstico ou termo clínico:", placeholder="Ex: heart failure, pneumonia, stroke, cirrhosis, surgery")
        
    ds_query = """
        SELECT note_id, subject_id, hadm_id, service, charttime, word_count,
               chief_complaint, history_present_illness, past_medical_history,
               brief_hospital_course, discharge_diagnosis, discharge_instructions, text
        FROM discharge_notes
        WHERE 1=1
    """
    ds_params = []
    
    if selected_service != "(Todos)":
        ds_query += " AND service = ?"
        ds_params.append(selected_service)
        
    if ds_search:
        ds_query += " AND (discharge_diagnosis LIKE ? OR brief_hospital_course LIKE ? OR chief_complaint LIKE ?)"
        t = f"%{ds_search}%"
        ds_params.extend([t, t, t])
        
    ds_query += " ORDER BY charttime DESC LIMIT 40"
    
    df_ds = pd.read_sql_query(ds_query, conn, params=ds_params)
    conn.close()
    
    if df_ds.empty:
        st.warning("Nenhum sumário de alta encontrado para os filtros.")
    else:
        st.write(f"Mostrando **{len(df_ds)}** sumários de alta:")
        ds_options = [f"{row['note_id']} | HADM: {row['hadm_id']} | Serv: {row['service'] or 'N/A'} | {row['word_count']} palavras" for _, row in df_ds.iterrows()]
        sel_ds_idx = st.selectbox("Selecione o sumário de alta:", range(len(ds_options)), format_func=lambda i: ds_options[i])
        
        sel_ds = df_ds.iloc[sel_ds_idx]
        st.markdown("---")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.markdown(f"**ID Sumário**: <span class='highlight-id'>{sel_ds['note_id']}</span>", unsafe_allow_html=True)
        col_m2.markdown(f"**Paciente (Subject)**: <span class='highlight-id'>{sel_ds['subject_id']}</span>", unsafe_allow_html=True)
        col_m3.markdown(f"**Internação (HADM)**: <span class='highlight-id'>{sel_ds['hadm_id']}</span>", unsafe_allow_html=True)
        col_m4.markdown(f"**Especialidade**: {sel_ds['service'] or 'Geral'}")
        
        tab_ds_struct, tab_ds_raw = st.tabs(["✨ Prontuário Estruturado", "📄 Texto Completo Bruto"])
        
        with tab_ds_struct:
            if sel_ds['chief_complaint']:
                st.markdown("**🚨 Queixa Principal (Chief Complaint):**")
                st.info(sel_ds['chief_complaint'])
                
            if sel_ds['history_present_illness']:
                st.markdown("**🏥 História da Doença Atual (HPI):**")
                st.markdown(f"<div class='badge-indication'>{sel_ds['history_present_illness'][:1000]}...</div>", unsafe_allow_html=True)
                
            if sel_ds['brief_hospital_course']:
                st.markdown("**💊 Evolução e Curso Hospitalar (Brief Hospital Course):**")
                st.markdown(f"<div class='badge-course'>{sel_ds['brief_hospital_course'][:1500]}...</div>", unsafe_allow_html=True)
                
            if sel_ds['discharge_diagnosis']:
                st.markdown("**🎯 Diagnóstico de Alta (Discharge Diagnosis):**")
                st.markdown(f"<div class='badge-impression'>{sel_ds['discharge_diagnosis']}</div>", unsafe_allow_html=True)
                
            if sel_ds['discharge_instructions']:
                with st.expander("📝 Instruções de Alta dadas ao Paciente"):
                    st.write(sel_ds['discharge_instructions'])
                    
        with tab_ds_raw:
            st.code(sel_ds['text'], language='text')

# ==========================================
# ABA 4: PRONTUÁRIO INTEGRADO (TIMELINE)
# ==========================================
with tab_integrated:
    st.subheader("🔗 Prontuário Integrado: Internação Completa (Radiologia + Sumário de Alta)")
    st.markdown("""
    Nesta visualização, conectamos a **internação hospitalar (`hadm_id`)** com **todos os exames de radiologia** realizados e o **sumário final de alta**.
    Essa é a base perfeita para avaliar se o sumário de alta refletiu fielmente os exames diagnósticos realizados!
    """)
    
    conn = get_connection()
    c = conn.cursor()
    
    paired_df = pd.read_sql_query("""
        SELECT hadm_id, subject_id, radiology_count, exam_list
        FROM paired_admissions
        ORDER BY radiology_count DESC
        LIMIT 100
    """, conn)
    
    if paired_df.empty:
        st.warning("Nenhuma internação com pares encontrada.")
        conn.close()
    else:
        paired_options = [
            f"Internação #{row['hadm_id']} (Paciente: {row['subject_id']}) — {row['radiology_count']} exames de imagem"
            for _, row in paired_df.iterrows()
        ]
        sel_paired_idx = st.selectbox("Selecione uma internação para explorar o prontuário completo:", range(len(paired_options)), format_func=lambda i: paired_options[i])
        
        chosen_hadm = paired_df.iloc[sel_paired_idx]['hadm_id']
        
        # Buscar dados do Sumário de Alta dessa internação
        ds_record = pd.read_sql_query("""
            SELECT note_id, charttime, text, brief_hospital_course, discharge_diagnosis
            FROM discharge_notes
            WHERE hadm_id = ?
            LIMIT 1
        """, conn, params=[chosen_hadm])
        
        # Buscar todos os laudos radiológicos dessa internação
        rad_records = pd.read_sql_query("""
            SELECT note_id, exam_name, charttime, findings_sec, impression_sec, text
            FROM radiology_notes
            WHERE hadm_id = ?
            ORDER BY charttime ASC
        """, conn, params=[chosen_hadm])
        
        conn.close()
        
        st.markdown(f"### 📋 Prontuário da Internação `HADM ID: {chosen_hadm}`")
        
        col_rad_side, col_ds_side = st.columns([1, 1])
        
        with col_rad_side:
            st.markdown(f"#### 🩻 Exames de Imagem Realizados ({len(rad_records)})")
            for idx, r_row in rad_records.iterrows():
                with st.expander(f"📷 {r_row['charttime']} — {r_row['exam_name']}", expanded=(idx==0)):
                    st.markdown(f"**ID Laudo:** `{r_row['note_id']}`")
                    if r_row['findings_sec']:
                        st.markdown("**Achados:**")
                        st.markdown(f"<div class='badge-findings'>{r_row['findings_sec']}</div>", unsafe_allow_html=True)
                    if r_row['impression_sec']:
                        st.markdown("**Impressão:**")
                        st.markdown(f"<div class='badge-impression'>{r_row['impression_sec']}</div>", unsafe_allow_html=True)
                    if not r_row['findings_sec'] and not r_row['impression_sec']:
                        st.text(r_row['text'][:400] + "...")
                        
        with col_ds_side:
            st.markdown("#### 📝 Sumário de Alta Correspondente")
            if not ds_record.empty:
                ds_item = ds_record.iloc[0]
                st.markdown(f"**ID Sumário:** `{ds_item['note_id']}` | **Data:** `{ds_item['charttime']}`")
                
                if ds_item['discharge_diagnosis']:
                    st.markdown("**Diagnóstico Final de Alta:**")
                    st.markdown(f"<div class='badge-impression'>{ds_item['discharge_diagnosis']}</div>", unsafe_allow_html=True)
                    
                if ds_item['brief_hospital_course']:
                    st.markdown("**Evolução e Curso Hospitalar (Brief Hospital Course):**")
                    st.markdown(f"<div class='badge-course'>{ds_item['brief_hospital_course']}</div>", unsafe_allow_html=True)
                else:
                    st.code(ds_item['text'][:1500] + "...", language='text')
            else:
                st.warning("Sumário de alta não localizado para esta internação.")

# ==========================================
# ABA 5: GUIA DO PROJETO & 4 CAMINHOS (45 DIAS)
# ==========================================
with tab_academic:
    st.subheader("🎓 Guia Estratégico para o Projeto Final de Mestrado (Prazo: 45 Dias)")
    st.markdown("""
    De acordo com o arquivo `projeto.md`, o objetivo é:
    > *"Empregar modelos de LLM abertos para construir um pipeline de qualidade dos laudos.*
    > *100% executável e aberto (preferencialmente Google Colab), repositório GitHub, referências acadêmicas e artigo formato SBC (preferencialmente LaTeX)."*
    
    Abaixo estão **4 caminhos temáticos rigorosos e perfeitamente viáveis em 45 dias**, detalhados do ponto de vista metodológico.
    """)
    
    caminho1, caminho2, caminho3, caminho4 = st.tabs([
        "⭐ Caminho 1: Consistência Interna do Laudo (Recomendado)",
        "🔍 Caminho 2: Auditoria Cruzada (Radiologia vs. Alta)",
        "🗣️ Caminho 3: Simplificação e Tradução para Pacientes",
        "📐 Caminho 4: Conformidade com Diretrizes Clínicas"
    ])
    
    with caminho1:
        st.markdown("""
        ### ⭐ Caminho 1: Detecção de Inconsistência e Alucinação entre Achados e Impressão Radiológica
        
        #### 1. Pergunta Científica
        *“Em que medida LLMs abertas (Llama-3-8B, Mistral-7B, BioMistral) conseguem detectar omissões críticas e alucinações diagnósticas na seção de Impressão quando comparadas aos Achados detalhados de um laudo radiológico?”*
        
        #### 2. Por que é ideal para o prazo de 45 dias?
        - **Dados prontos**: O banco `radiology.csv.gz` já possui milhares de laudos com seções explícitas de `FINDINGS` e `IMPRESSION`.
        - **Problema de ouro na literatura médica**: Radiologistas frequentemente enfrentam fadiga de plantão, podendo deixar de resumir um nódulo incidental ou redigir uma conclusão ambígua.
        - **100% viável no Google Colab**: Modelos de 7B/8B quantizados em 4 bits (BitsAndBytes) rodam gratuitamente na GPU T4 do Colab.
        
        #### 3. Arquitetura do Pipeline de Qualidade
        1. **Entrada**: Texto dos `FINDINGS` do laudo.
        2. **Geração / Auditoria via LLM**:
           - **Tarefa A**: Gerar uma `IMPRESSION` sintética a partir dos achados.
           - **Tarefa B (Auditor de Qualidade)**: Comparar a impressão real do médico com os achados e pontuar:
             - *Score de Completude* (Cobriu todas as anomalias?).
             - *Score de Factualidade* (Alucinou patologias inexistentes?).
             - *Score de Relevância Clínica*.
        3. **Métricas de Avaliação Objetivas**:
           - **RadGraph F1-Score**: Grafo clínico de entidades e relações médicas.
           - **ROUGE-L / BERTScore**: Similaridade semântica com a impressão de referência.
           - **Taxa de Alucinação (Hallucination Rate)**.
           
        #### 4. Modelos Abertos Sugeridos
        - `BioMistral-7B` (BioNLP lab / HuggingFace)
        - `Llama-3-8B-Instruct` (Meta)
        - `Qwen2.5-7B-Instruct` (Alibaba)
        """)
        
    with caminho2:
        st.markdown("""
        ### 🔍 Caminho 2: Auditoria Cruzada entre Laudos de Imagem e o Sumário de Alta
        
        #### 1. Pergunta Científica
        *“Sumários de alta hospitalar preservam fielmente as conclusões críticas dos exames de imagem realizados durante a internação, ou ocorrem omissões e discrepâncias factuais?”*
        
        #### 2. Metodologia
        - Utiliza as **2.190 internações conectadas** do nosso banco.
        - O pipeline extrai os achados radiológicos da internação e o trecho de *Evolução Hospitalar* ou *Exames Relevantes* do Sumário de Alta.
        - Uma LLM aberta atua como **Auditor Clínico Cruzado**, verificando se achados radiológicos graves (ex: embolia pulmonar, fratura, hemorragia) foram adequadamente citados na alta.
        """)
        
    with caminho3:
        st.markdown("""
        ### 🗣️ Caminho 3: Pipeline de Simplificação de Laudos para Pacientes com Avaliação de Qualidade
        
        #### 1. Pergunta Científica
        *“Como LLMs abertas podem traduzir laudos técnicos para linguagem leiga mantendo a precisão médica e prevenindo perda de informações críticas?”*
        
        #### 2. Metodologia
        - Pipeline de duas etapas:
          1. **Gerador**: Transforma o laudo técnico em um laudo em linguagem simples (*Patient-Friendly Summary*).
          2. **Avaliador de Qualidade (Quality Pipeline)**: Avalia a simplificação em 3 eixos:
             - **Preservação de Fatos Médicos** (não removeu alertas de risco).
             - **Índice de Legibilidade** (Flesch-Kincaid Grade Level / Dale-Chall).
             - **Ausência de Alucinações**.
        """)
        
    with caminho4:
        st.markdown("""
        ### 📐 Caminho 4: Avaliação de Conformidade Estrutural e Diretrizes Médicas
        
        #### 1. Pergunta Científica
        *“Laudos radiológicos de emergência cumprem os critérios estruturais e recomendações de comunicação preconizados pelas diretrizes do Colégio Americano de Radiologia (ACR)?”*
        
        #### 2. Metodologia
        - LLM atua como avaliadora de *checklist* clínico formal: identificação de técnica, lateralidade, comparação prévia, achados incidentais e recomendação de seguimento.
        """)
        
    st.markdown("---")
    st.subheader("📅 Cronograma Sugerido de 45 Dias (Semana a Semana)")
    cronograma_data = {
        "Semana": ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5", "Semana 6 (Final)"],
        "Etapa": [
            "Definição & Amostragem",
            "Engenharia de Prompt & Colab",
            "Execução dos Experimentos",
            "Métricas & Análise Quantitativa",
            "Escrita do Artigo SBC",
            "Revisão & Apresentação"
        ],
        "Entregáveis Concretos": [
            "Escolha do tema (ex: Caminho 1), seleção de 200 a 500 laudos anotados do MIMIC-IV.",
            "Notebook Colab funcional carregando Llama-3-8B / BioMistral via HuggingFace com 4-bit.",
            "Inferência do pipeline em lote, salvando outputs e logs de qualidade em JSON.",
            "Cálculo de RadGraph / ROUGE / BERTScore / Taxas de Alucinação e geração de gráficos.",
            "Artigo em LaTeX (template SBC: 8 a 10 páginas) com introdução, método e tabelas.",
            "Repositório GitHub organizado + gravação de vídeo de 10 min de apresentação."
        ]
    }
    st.table(pd.DataFrame(cronograma_data))

# ==========================================
# ABA 6: SANDBOX DO PIPELINE DE QUALIDADE
# ==========================================
with tab_sandbox:
    st.subheader("🧪 Simulador Interativo do Pipeline de Qualidade com LLMs")
    st.markdown("""
    Experimente os **prompts do pipeline de qualidade** em laudos reais do banco.
    Você pode copiar o prompt formatado com o laudo inserido para rodar no Google Colab, ChatGPT ou Ollama local.
    """)
    
    conn = get_connection()
    sample_notes = pd.read_sql_query("""
        SELECT note_id, exam_name, findings_sec, impression_sec
        FROM radiology_notes
        WHERE findings_sec != '' AND impression_sec != '' AND length(findings_sec) > 100
        LIMIT 15
    """, conn)
    conn.close()
    
    if sample_notes.empty:
        st.warning("Nenhum laudo com achados e impressão preenchidos.")
    else:
        sample_opts = [f"{r['note_id']} | {r['exam_name']}" for _, r in sample_notes.iterrows()]
        sel_sim_idx = st.selectbox("Selecione um caso clínico real para o teste de qualidade:", range(len(sample_opts)), format_func=lambda i: sample_opts[i])
        
        sim_note = sample_notes.iloc[sel_sim_idx]
        
        task_choice = st.radio(
            "Selecione a Tarefa do Pipeline de Qualidade:",
            [
                "1. Auditor de Alucinação e Omissão (Findings vs. Impression Check)",
                "2. Geração e Avaliação de Nova Impressão Diagnóstica",
                "3. Tradução Simplificada para Paciente com Checagem de Factualidade"
            ]
        )
        
        st.markdown("---")
        
        if "1. Auditor" in task_choice:
            prompt_template = f"""Você é um auditor médico especialista em qualidade de laudos radiológicos.
Analise os ACHADOS (Findings) e a IMPRESSÃO DIAGNÓSTICA (Impression) abaixo e emita um relatório estruturado de qualidade.

[EXAME]: {sim_note['exam_name']}

[ACHADOS (FINDINGS)]:
{sim_note['findings_sec']}

[IMPRESSÃO REAL EMITIDA]:
{sim_note['impression_sec']}

TAREFA DE AUDITORIA:
1. Houve OMISSÃO de algum achado clinicamente relevante citado nos ACHADOS que foi esquecido na IMPRESSÃO?
2. Houve ALUCINAÇÃO ou EXTRAPOLAÇÃO na IMPRESSÃO de algo que NÃO consta nos ACHADOS?
3. Atribua notas de 1 a 5 para:
   - Precisão Factual (1-5):
   - Completude Clínica (1-5):
   - Concisão e Clareza (1-5):
4. Justifique suas notas em 2 parágrafos objetivos."""
        
        elif "2. Geração" in task_choice:
            prompt_template = f"""Você é um radiologista sênior. Com base EXCLUSIVAMENTE nos ACHADOS técnicos do exame abaixo, redija uma IMPRESSÃO DIAGNÓSTICA concisa, precisa e sem alucinações.

[EXAME]: {sim_note['exam_name']}

[ACHADOS (FINDINGS)]:
{sim_note['findings_sec']}

[SUA IMPRESSÃO]:"""
        else:
            prompt_template = f"""Você é um médico comunicador empático. Traduza o laudo técnico abaixo para uma explicação clara, humana e compreensível para um paciente leigo, sem jargões indecifráveis, mantendo fidelidade aos fatos médicos e indicando quando é necessário retorno ao médico assistente.

[EXAME]: {sim_note['exam_name']}

[ACHADOS E IMPRESSÃO]:
{sim_note['findings_sec']}
{sim_note['impression_sec']}

[EXPLICAÇÃO PARA O PACIENTE]:"""

        st.subheader("📋 Prompt Gerado Pronto para o Pipeline:")
        st.text_area("Copie este prompt para testar no seu modelo no Colab / LLM:", value=prompt_template, height=320)
        
        st.info("💡 **Dica para o Google Colab**: No projeto final, o notebook Colab pode iterar automaticamente por uma lista de laudos, chamar o modelo aberto via pipeline do HuggingFace (`transformers.pipeline('text-generation')`) e salvar as respostas e notas em um DataFrame pandas para gerar os gráficos do artigo SBC!")
