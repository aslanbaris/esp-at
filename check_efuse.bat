@echo off
call esp-idf\export.bat
python esp-idf\components\esptool_py\esptool\espefuse.py -p COM18 summary
