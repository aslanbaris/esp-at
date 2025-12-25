@echo off
rem Monitor ESP-AT Project
rem Usage: m.bat <COM_PORT>

if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: m.bat COMx
    exit /b 1
)

rem Set up ESP-IDF environment
call esp-idf\export.bat

rem Run monitor command
idf.py -p %1 monitor
