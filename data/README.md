# Diretório de Dados (MIMIC-IV-Note)

Devido às restrições do termo de uso de dados (Data Use Agreement - DUA) do **PhysioNet** e ao pedido dos autores do **MIMIC-IV-Note**, os dados clínicos brutos e bancos de dados derivados **não são versionados no repositório**.

## Como obter os dados:

1. Obtenha a credencial de acesso no PhysioNet:
   - [MIMIC-IV-Note no PhysioNet](https://physionet.org/content/mimic-iv-note/2.2/)
2. Baixe os seguintes arquivos e coloque-os nesta pasta (`data/`):
   - `discharge.csv.gz`
   - `discharge_detail.csv.gz`
   - `radiology.csv.gz`
   - `radiology_detail.csv.gz`
3. Na raiz do projeto, execute o script de preparação para indexar o banco local SQLite:
   ```bash
   python prepare_db.py
   ```
4. O arquivo `data/explorer.db` será criado automaticamente para uso pelo `app.py`.
