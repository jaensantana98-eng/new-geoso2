@echo off
cd /d "%~dp0"

pyinstaller ^
 --noconsole ^
 --onedir ^
 --add-data "geoso2-web-template:geoso2-web-template" ^
 geoso2-web-template\interfaz_ventana_principal.py
