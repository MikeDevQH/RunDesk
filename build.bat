@echo off
REM ============================================
REM  Build script para RunDesk
REM  Genera RunDesk.exe en dist/
REM ============================================

echo.
echo === RunDesk - Build ===
echo.

REM Verificar que estamos en el directorio correcto
if not exist "app\__main__.py" (
    echo ERROR: Ejecuta este script desde la raiz del proyecto.
    exit /b 1
)

REM Verificar PyInstaller
.venv\Scripts\python.exe -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller no esta instalado.
    echo Ejecuta: uv pip install pyinstaller
    exit /b 1
)

REM Limpiar build anterior
echo [1/4] Limpiando build anterior...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Ejecutar tests
echo [2/4] Ejecutando tests...
.venv\Scripts\python.exe -m pytest tests\ -q
if errorlevel 1 (
    echo ERROR: Los tests fallaron. Corrige antes de empaquetar.
    exit /b 1
)

REM Lint check
echo [3/4] Verificando lint...
.venv\Scripts\python.exe -m ruff check app\ --select E,F,I -q
if errorlevel 1 (
    echo ERROR: Errores de lint encontrados.
    exit /b 1
)

REM Build
echo [4/4] Empaquetando con PyInstaller...
.venv\Scripts\python.exe -m PyInstaller rundesk.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller fallo.
    exit /b 1
)

echo.
echo === Build completado ===
echo Ejecutable: dist\RunDesk.exe
echo.

REM Mostrar tamano
for %%I in (dist\RunDesk.exe) do echo Tamano: %%~zI bytes
echo.
