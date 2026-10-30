# Servidor e Catálogo de Artigos — Projeto Beth LLM

> **Disciplina:** Modelos Generativos de Linguagem  
> **Programa:** Mestrado em Computação Aplicada  
> **Tema Central:** *Avaliando a Qualidade de Laudos Médicos com o uso de LLMs* (MIMIC-IV-Note / PhysioNet)

---

## 📌 Visão Geral

Este diretório contém o acervo completo e estruturado dos **33 artigos e bases de dados** indicados para o projeto, organizados nos 7 eixos temáticos da disciplina:

1. **Base de dados e fundamentos** (MIMIC-III, MIMIC-IV, PhysioNet, etc.)
2. **LLMs para detecção de erros, avaliação e qualidade em textos médicos** (GPT-4, multipass LLMs, etc.)
3. **LLMs para sumários de alta, predição e tarefas de PLN clínico** (GREEN, EHRNoteQA, etc.)
4. **Codificação ICD e predição de desfecho** (CliniBench, Mimic-IV-ICD, etc.)
5. **Detecção de alucinações e taxonomia de erros em laudos** (ReXTrust, CCD, etc.)
6. **Qualidade de notas sintéticas e expansões do MIMIC** (MIMIC-III-Ext-Notes, etc.)
7. **Base derivada adicional relacionada ao trabalho anterior** (MIMIC-Ext-SynNotes, etc.)

---

## 🚀 Como Iniciar o Servidor

Você pode iniciar o servidor de duas formas muito simples:

### Opção 1: Clique Duplo no Windows
Basta dar um duplo clique no arquivo:
```cmd
iniciar_servidor.bat
```
O servidor será iniciado e abrirá automaticamente seu navegador em `http://localhost:8000` (ou na próxima porta livre, ex: `8002`).

### Opção 2: Linha de Comando (Terminal / PowerShell)
No diretório `biblio/`, execute:
```bash
python server.py
```
*Se desejar iniciar sem abrir o navegador automaticamente, adicione `--no-browser`.*

---

## 🖥️ Funcionalidades da Interface Web

A interface (`index.html`) foi construída com design acadêmico moderno e responsivo:

- **Busca em tempo real:** Pesquise instantaneamente por título, autor, ano, trecho do abstract, periódico ou DOI.
- **Filtros rápidos:**
  - **Todos (33):** Exibe o acervo completo.
  - **Com PDF Local (15):** Exibe somente os artigos de acesso aberto cujo PDF foi baixado e está pronto para leitura offline.
  - **Acesso Externo (18):** Exibe artigos em repositórios oficiais e bases de dados com acesso restrito/credenciado (PhysioNet DUA).
- **Filtro por Eixo Temático:** Filtre diretamente por qualquer um dos 7 tópicos do plano de aula.
- **Ordenação:** Ordene pela numeração original (1 a 33), ano (mais recente/mais antigo) ou título (A-Z).
- **Leitura de Abstracts:** Expansão direta no card ou abertura de modal focado em tela cheia com a descrição e abstract acadêmico completo.
- **Ações diretas:**
  - `📄 Abrir Artigo (PDF)`: Abre o PDF local baixado em nova aba do navegador.
  - `🔗 Página Oficial`: Redireciona diretamente para a publicação oficial (Nature, ACL Anthology, arXiv, JAMA, JMIR, Radiology, PhysioNet).
  - `📋 Copiar Citação ABNT`: Copia a referência formatada pronta para o artigo/relatório da disciplina.

---

## 📂 Estrutura de Arquivos

```text
biblio/
├── 001 Artigos Iniciais.txt     # Arquivo original fornecido pelo professor
├── papers/                      # Pasta contendo os PDFs baixados localmente
│   ├── 02_Johnson_2016_MIMIC_III.pdf
│   ├── 03_Johnson_2023_MIMIC_IV.pdf
│   ├── 12_Liu_2024_Synthetic_Notes_Evaluation.pdf
│   ├── 16_Hegselmann_2024_Faithful_Patient_Summaries.pdf
│   ├── 17_Kweon_2024_EHRNoteQA.pdf
│   ├── 19_Ostmeier_2024_GREEN_Radiology_Evaluation.pdf
│   ├── 20_Douglas_2025_Less_Is_More_ICD_Prediction.pdf
│   ├── 22_Grundmann_2025_CliniBench.pdf
│   ├── 23_Irany_2026_GPT_Clinical_Classification.pdf
│   ├── 24_Nguyen_2023_MIMIC4_ICD_Benchmark.pdf
│   ├── 25_Rohr_2024_Revisiting_Clinical_Outcome_Prediction.pdf
│   ├── 26_VanAken_2021_Clinical_Outcome_Admission_Notes.pdf
│   ├── 27_CCD_2026_Clinical_Contrastive_Decoding.pdf
│   ├── 29_Hardy_2024_ReXTrust_Hallucination_Detection.pdf
│   └── 32_Liu_2026_BioNLP_Synthetic_Notes.pdf
├── papers_data.json             # Catálogo estruturado em JSON com metadados e abstracts
├── index.html                   # Interface gráfica SPA completa
├── server.py                    # Servidor HTTP nativo em Python
├── iniciar_servidor.bat         # Atalho de inicialização rápida no Windows
└── README.md                    # Esta documentação
```

---

## 📊 Estatísticas do Acervo

| Categoria | Quantidade | Observações |
|---|---|---|
| **Total de Registros** | 33 | Artigos, revisões sistemáticas e repositórios de dados |
| **PDFs Locais Baixados** | 15 | Artigos científicos abertos (Nature, arXiv, ACL Anthology) |
| **Artigos em Repositórios / Datasets** | 18 | Datasets PhysioNet (requer DUA) e periódicos médicos (AHA, RSNA, JMIR) |
