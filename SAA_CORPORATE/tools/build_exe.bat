@echo off
setlocal
cd /d "%~dp0.."

echo ==============================================
echo SAA Corporate - Build EXE (PyInstaller)
echo ==============================================

set "PYTHON_EXE=python"
if exist "runtime\winpython\python.exe" (
    set "PYTHON_EXE=runtime\winpython\python.exe"
)

echo [INFO] Python selecionado: %PYTHON_EXE%
"%PYTHON_EXE%" -m pip install -r tools\requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias para build.
    pause
    exit /b 1
)

set "ICON_ARG="
if exist "tools\icon.ico" (
    set "ICON_ARG=--icon tools\icon.ico"
)

"%PYTHON_EXE%" -m PyInstaller --onefile --name SAA_Notas --distpath dist --workpath build --specpath buildspec %ICON_ARG% app\saa_console.py
if errorlevel 1 (
    echo [ERRO] Falha no build do EXE.
    pause
    exit /b 1
)

echo [OK] EXE gerado em: dist\SAA_Notas.exe
pause
exit /b 0
