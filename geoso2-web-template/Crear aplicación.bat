@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   GENERANDO EJECUTABLE DE GEOSO2...
echo ============================================

REM Ir al directorio donde está este BAT
cd /d "%~dp0"

REM Ruta del escritorio
set DESKTOP=%USERPROFILE%\Desktop

REM Script principal
set MAIN_SCRIPT=interfaz_ventana_principal.py

REM Validación
if not exist "%MAIN_SCRIPT%" (
    echo ERROR: No se encuentra interfaz_ventana_principal.py
    pause
    exit /b 1
)

echo.
echo Limpiando dist y build anteriores...
rmdir /s /q "%DESKTOP%\Editor GEOSO2" 2>nul
rmdir /s /q build 2>nul
del interfaz_ventana_principal.spec 2>nul

echo.
echo Generando ejecutable...
echo.

pyinstaller ^
 --noconsole ^
 --onedir ^
 --name "Editor GEOSO2" ^
 --distpath "%DESKTOP%" ^
 --add-data "geoso2-web-template;geoso2-web-template" ^
 "%MAIN_SCRIPT%"

echo.
echo ============================================
echo   PROCESO COMPLETADO
echo   El ejecutable está en:
echo   %DESKTOP%\Editor GEOSO2
echo ============================================
pause
