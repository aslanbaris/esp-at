@echo off
call esp-idf\export.bat
python esp-idf\components\fatfs\wl_fatfsgen.py --help
pause
