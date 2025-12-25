@echo off
call esp-idf\export.bat
echo ========================================================
echo CHECKING EFUSE SUMMARY (Security Status)
echo ========================================================
python -m espefuse -p COM6 summary
echo.
echo ========================================================
echo VERIFYING PARTITION TABLE (Is it readable?)
echo ========================================================
python -m esptool -p COM6 verify_flash 0x10000 build\partition_table\partition-table.bin
echo.
pause
