@echo off
chcp 65001 >nul
title MIMIC-IV-Note Explorer - Mestrado LLM
cd /d "%~dp0"

echo =====================================================================
echo    🩺 MIMIC-IV-Note Explorer - Servidor Local (Mestrado LLM)
echo =====================================================================
echo.
echo Iniciando o servidor Streamlit...
echo O navegador abrira automaticamente em: http://localhost:8501
echo.
echo (Para desligar o servidor, basta fechar esta janela do terminal)
echo =====================================================================
echo.

:: Abre o navegador em background apos 2 segundos
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8501"

:: Inicia o Streamlit
python -m streamlit run app.py --server.port 8501

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao chamar 'python'. Tentando caminho completo...
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m streamlit run app.py --server.port 8501
)

pause
