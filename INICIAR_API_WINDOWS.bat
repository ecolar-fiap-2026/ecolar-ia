@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Execute CONFIGURAR_WINDOWS.bat primeiro.
 pause
 exit /b 1
)
echo Abra http://127.0.0.1:5000 no navegador. Para encerrar: Ctrl+C.
.venv\Scripts\python.exe app.py
pause
