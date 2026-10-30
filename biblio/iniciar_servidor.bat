@echo off
chcp 65001 > nul
title Servidor de Artigos - Beth LLM
echo ======================================================================
echo  Iniciando Servidor da Biblioteca de Artigos - Beth LLM
echo  Disciplina: Modelos Generativos de Linguagem (Mestrado Computacao)
echo ======================================================================
echo.
cd /d "%~dp0"
python server.py
pause
