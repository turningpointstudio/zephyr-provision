@echo off
echo Bootstrapping machine...
powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://https://raw.githubusercontent.com/turningpointstudio/zephyr-provision/refs/heads/main/ConfigureWindowsForAnsible.ps1 | iex"
pause