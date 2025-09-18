@echo off
echo Bootstrapping machine...
powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://raw.githubusercontent.com/turningpointstudio/zephyr-provision/main/bootsrap/ConfigureWindowsForAnsible.ps1 | iex"
pause