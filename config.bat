@echo off
rem Configure ESP-AT Project
rem Set up ESP-IDF environment
call esp-idf\export.bat

rem Run menuconfig
python build.py menuconfig
