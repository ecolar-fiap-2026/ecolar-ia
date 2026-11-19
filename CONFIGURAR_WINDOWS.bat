@echo off
cd /d "%~dp0"
echo EcoLar IA - criando ambiente com Python 3.12 de 64 bits.
py -3.12 -m venv .venv
if errorlevel 1 goto falha
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto falha
echo.
echo Ambiente instalado. Abra INICIAR_API_WINDOWS.bat.
pause
exit /b 0
:falha
echo.
echo Falha. Confira se Python 3.12 de 64 bits esta instalado e se ha internet.
echo Copie a mensagem acima para investigar. Nao e necessario executar como administrador.
pause
exit /b 1
