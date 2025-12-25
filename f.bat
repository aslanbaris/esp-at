@echo off
rem Flash ESP-AT Project
rem Usage: f.bat <COM_PORT>

if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: f.bat COMx
    exit /b 1
)

rem Set up ESP-IDF environment
call esp-idf\export.bat

rem Run flash command
python build.py -p %1 flash
