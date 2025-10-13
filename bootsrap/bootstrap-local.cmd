@echo off
echo Bootstrapping machine...
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0ConfigureWindowsForAnsible.ps1"
pause