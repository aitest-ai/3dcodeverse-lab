@echo off
cd /d "%~dp0"
py -3 START_STUDIO_V06.py --open
if errorlevel 1 pause
