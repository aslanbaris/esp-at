@echo off
echo ========================================================
echo Flashing FATFS Partition...
echo Address: 0x40000
echo File: build\customized_partitions\fatfs.bin
echo Mode: Encrypted
echo ========================================================
call esp-idf\export.bat

python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force --encrypt ^
0x40000 build\customized_partitions\fatfs.bin

if %errorlevel% neq 0 (
    echo FAILURE: FATFS Flash Failed.
) else (
    echo SUCCESS: FATFS Flashed. Device rebooting...
)
pause
