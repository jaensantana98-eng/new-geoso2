@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   GENERANDO EJECUTABLE DE GEOSO2...
echo ============================================

REM Ir al directorio donde está este BAT
cd /d "%~dp0"

REM Directorio actual (geoso2-web-template)
set WEB_DIR=%cd%
echo Carpeta web detectada: %WEB_DIR%

REM Script principal
set MAIN_SCRIPT=%WEB_DIR%\interfaz_ventana_principal.py

REM Validaciones
if not exist "%MAIN_SCRIPT%" (
    echo ERROR: No se encuentra interfaz_ventana_principal.py en esta carpeta.
    pause
    exit /b 1
)

echo.
echo Limpiando dist y build anteriores...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
del interfaz_ventana_principal.spec 2>nul

echo.
echo Incluyendo carpeta completa: geoso2-web-template
echo.

pyinstaller ^
 --noconsole ^
 --add-data "geoso2-web-template;geoso2-web-template" ^
 "%MAIN_SCRIPT%"

echo.
echo ============================================
echo   PROCESO COMPLETADO
echo   El ejecutable está en: dist\
echo ============================================
pause
