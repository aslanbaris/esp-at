@echo off
if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: flash_fs_plain_latest.bat COMx
    exit /b 1
)

echo ========================================================
echo Flashing Updated FATFS (Plaintext)...
echo ========================================================
call esp-idf\export.bat

rem Flash build\customized_partitions\fatfs.bin to 0x40000
rem NO ENCRYPTION
python -m esptool -p %1 -b 460800 --before default_reset --after hard_reset write_flash --force ^
0x40000 build\customized_partitions\fatfs.bin

if %errorlevel% neq 0 (
    echo FAILURE: Flash Failed.
) else (
    echo SUCCESS: FATFS Flashed. Device rebooting...
)
