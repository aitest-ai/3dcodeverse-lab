@echo off
cd /d "%~dp0"
py -3 START_STUDIO_V07.py --open
if errorlevel 1 pause
