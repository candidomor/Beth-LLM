# 🩺 MIMIC-IV-Note Explorer | Mestrado em Modelos Generativos e de Linguagem

Este servidor local interativo foi desenvolvido para explorar, analisar e compreender os dados clínicos da base **MIMIC-IV-Note v2.2** (`discharge.csv.gz` e `radiology.csv.gz`) de forma estruturada, visual e clinicamente inteligível, auxiliando na escolha e execução do **Projeto Final de Mestrado (prazo: 45 dias)**.

---

## 🚀 Como Iniciar e Acessar o Servidor Local

Você tem 3 formas simples de iniciar o servidor:

1. **Pelo Menu Iniciar do Windows**:
   - Pressione a tecla `Windows` no teclado e digite **`MIMIC-IV-Note Explorer`**.
   - Ao clicar, ele iniciará o servidor e abrirá o navegador automaticamente!

2. **Pelo arquivo `.bat`**:
   - Dê dois cliques em [iniciar_servidor.bat](file:///c:/Users/Cândido%20Moreira/Meu%20Drive%20(candidomor@gmail.com)/Coding02/Beth%20LLM/iniciar_servidor.bat) na pasta do projeto.

3. **Pelo Terminal**:
   ```bash
   python -m streamlit run app.py
   ```

👉 **URL de Acesso no Navegador:** [http://localhost:8501](http://localhost:8501)

---

## 🗂️ O Que Foi Estruturado

1. **`prepare_db.py`**:
   - Processou os arquivos `.csv.gz` brutos e comprimidos sem sobrecarregar a memória RAM.
   - Segmentou os laudos radiológicos em seções canônicas: `Indication`, `Technique`, `Comparison`, `Findings` e `Impression`.
   - Segmentou os sumários de alta em: `Chief Complaint`, `History of Present Illness`, `Brief Hospital Course`, `Discharge Diagnosis` e `Discharge Instructions`.
   - Gerou o banco de dados indexado `data/explorer.db` (SQLite com índices relacionais em `hadm_id`, `subject_id` e `exam_name`), permitindo buscas instantâneas (< 5 ms).

2. **`app.py`**:
   - Interface web visual desenvolvida em Streamlit contendo 6 abas principais:
     - 📊 **Visão Geral dos Dados**: Métricas de volume, palavras médias por laudo, exames mais frequentes e arquitetura relacional do MIMIC-IV.
     - 🩻 **Laudos Radiológicos (Radiology)**: Filtros por tipo de exame (Raio-X de Tórax, TC Crânio, etc.) e busca textual por patologias (pneumonia, fratura, edema), com visualização humanizada por blocos coloridos (*Findings* vs. *Impression*).
     - 📋 **Sumários de Alta (Discharge)**: Consulta aos prontuários de alta hospitalar por especialidade médica e diagnóstico.
     - 🔗 **Prontuário Integrado (Linha do Tempo)**: Visualização conectada da internação (`hadm_id`) mostrando todos os laudos de imagem realizados em conjunto com o sumário de alta correspondente (ideal para auditoria clínica cruzada).
     - 🎓 **Guia do Projeto de Mestrado & 4 Caminhos (45 dias)**: Análise detalhada dos requisitos do arquivo `projeto.md`, com 4 propostas científicas viáveis, cronograma semana a semana de 45 dias, referências bibliográficas essenciais e estrutura de artigo SBC.
     - 🧪 **Sandbox do Pipeline de Qualidade**: Simulador interativo com prompts médicos prontos para testar a avaliação de laudos usando LLMs abertas (Llama-3-8B, BioMistral-7B, Qwen2.5-7B) no Google Colab.

---

## 🔬 4 Caminhos Propostos para o Projeto Final (45 Dias)

| Caminho | Foco do Pipeline | Dados Utilizados | Execução em Colab |
| :--- | :--- | :--- | :--- |
| **⭐ Caminho 1 (Recomendado)** | **Consistência Interna do Laudo Radiológico**: Detectar se a *Impression* omitiu achados ou alucinou patologias em relação aos *Findings*. | `radiology.csv.gz` | **Alta Viabilidade** (100% no Colab com Llama-3-8B / BioMistral em 4-bit). |
| **Caminho 2** | **Auditoria Cruzada de Documentos**: Checar se o *Sumário de Alta* registrou fielmente os laudos de imagem da internação. | Pares em `paired_admissions` | **Alta Relevância** (detecção de inconsistência cross-document). |
| **Caminho 3** | **Simplificação para Pacientes**: Tradução de laudos técnicos para linguagem leiga com auditoria de preservação factual e Flesch-Kincaid. | `radiology.csv.gz` | **Forte Impacto Social** (comunicação médico-paciente). |
| **Caminho 4** | **Conformidade Estrutural e Diretrizes**: Avaliar conformidade de laudos contra checklists do American College of Radiology (ACR). | `radiology.csv.gz` | **Fácil Implementação** (avaliação de conformidade normativa). |
