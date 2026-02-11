@echo off
cd /d %~dp0
echo Iniciando CMV Hub...
streamlit run src/backend/app.py
