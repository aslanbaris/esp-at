@echo off
rem Compile ESP-AT Project

rem Set up ESP-IDF environment
call esp-idf\export.bat

rem Run build command
python build.py build
