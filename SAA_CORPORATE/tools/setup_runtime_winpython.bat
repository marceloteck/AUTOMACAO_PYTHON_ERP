@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo ==============================================
echo SAA Corporate - Setup Runtime WinPython
 echo ==============================================

set "RUNTIME_DIR=runtime\winpython"
set "PYTHON_EXE=%RUNTIME_DIR%\python.exe"
set "TOOLS_DIR=tools"
set "REQ_FILE=%TOOLS_DIR%\requirements.txt"
set "ZIP_FILE=%TOOLS_DIR%\WinPython.zip"
set "DOWNLOAD_URL=https://github.com/winpython/winpython/releases/download/6.0.20240210final/Winpython64-3.11.8.0dot.exe"
set "DOWNLOADED_EXE=%TOOLS_DIR%\WinPythonSetup.exe"

if exist "%PYTHON_EXE%" (
    echo [OK] Runtime ja encontrado em %PYTHON_EXE%
    goto INSTALL_DEPS
)

if exist "%RUNTIME_DIR%" (
    echo [INFO] Pasta %RUNTIME_DIR% existe, mas python.exe nao foi encontrado.
    echo [INFO] Tentando continuar com instalacao manual.
)

if exist "%ZIP_FILE%" (
    echo [INFO] Encontrado pacote manual: %ZIP_FILE%
    echo [INFO] Extraindo para %RUNTIME_DIR% ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%RUNTIME_DIR%' -Force"
    goto FIND_PYTHON
)

if exist "%DOWNLOADED_EXE%" (
    echo [INFO] Encontrado instalador local: %DOWNLOADED_EXE%
    goto EXTRACT_EXE
)

echo [INFO] Nao foi encontrado pacote local do WinPython.
echo [INFO] Tentando baixar automaticamente...
curl -L "%DOWNLOAD_URL%" -o "%DOWNLOADED_EXE%"
if errorlevel 1 (
    echo [ERRO] Falha ao baixar WinPython automaticamente.
    echo [ACAO] Baixe manualmente o WinPython e coloque em:
    echo        %ZIP_FILE%  ou  %DOWNLOADED_EXE%
    pause
    exit /b 1
)

:EXTRACT_EXE
echo [INFO] Tentando extrair instalador WinPython para runtime\ ...
"%DOWNLOADED_EXE%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="%cd%\%RUNTIME_DIR%"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel extrair o instalador automaticamente.
    echo [ACAO] Extraia manualmente o WinPython para runtime\winpython
    pause
    exit /b 1
)

:FIND_PYTHON
if exist "%PYTHON_EXE%" goto INSTALL_DEPS
for /f "delims=" %%F in ('dir /s /b "%RUNTIME_DIR%\python.exe"') do (
    set "PYTHON_EXE=%%F"
    goto INSTALL_DEPS
)

echo [ERRO] python.exe nao encontrado dentro de %RUNTIME_DIR%.
echo [ACAO] Verifique se o WinPython foi extraido corretamente.
pause
exit /b 1

:INSTALL_DEPS
echo [INFO] Usando Python: %PYTHON_EXE%
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar pip.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo [OK] Runtime pronto para uso.
pause
exit /b 0
