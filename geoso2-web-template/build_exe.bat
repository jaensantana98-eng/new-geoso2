@echo off
echo ============================================
echo   GENERANDO EJECUTABLE DE GEOSO2...
echo ============================================

REM Elimina la carpeta dist y build anteriores
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
del interfaz_ventana_principal.spec 2>nul

echo.
echo Incluyendo carpeta completa: geoso2-web-template
echo.

pyinstaller ^
 --noconsole ^
 --onefile ^
 --add-data "geoso2-web-template;geoso2-web-template" ^
 interfaz_ventana_principal.py

echo.
echo ============================================
echo   PROCESO COMPLETADO
echo   El ejecutable está en: dist\
echo ============================================
pause
