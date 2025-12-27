@echo off
echo ========================================================
echo Flashing Valid FATFS Image (PLAINTEXT)...
echo ========================================================
call esp-idf\export.bat

rem Flash Image PLAINTEXT (Force)
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force ^
0x40000 build\customized_partitions\fatfs_valid.bin

if %errorlevel% neq 0 (
    echo FAILURE: Flash Failed.
) else (
    echo SUCCESS: FATFS Flashed (Plaintext). Device rebooting...
)
pause
