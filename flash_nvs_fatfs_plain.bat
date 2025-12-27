@echo off
echo ========================================================
echo Flashing MFG_NVS and FATFS (PLAINTEXT)
echo ========================================================
call esp-idf\export.bat

rem Flash MFG_NVS and FATFS as Plaintext
rem mfg_nvs at 0x21000
rem fatfs at 0x40000
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x40000 build\customized_partitions\fatfs_valid.bin

if %errorlevel% neq 0 (
    echo FAILURE: Flash Failed.
) else (
    echo SUCCESS: Partitions Flashed (Plaintext). Device rebooting...
)
pause
