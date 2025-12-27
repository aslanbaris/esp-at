@echo off
echo ========================================================
echo SAFE UPDATE: Programming App & Web Server ONLY
echo This script will NOT touch the Bootloader (Safe for Encrypted Devices)
echo ========================================================
call esp-idf\export.bat

rem Flash Application, Partition Table, and Web Data
rem Using --encrypt to ensure compatibility with Release mode
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force --encrypt ^
0x10000 build\partition_table\partition-table.bin ^
0x11000 build\ota_data_initial.bin ^
0x20000 build\at_customize.bin ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x200000 build\esp-at.bin

if %errorlevel% neq 0 (
    echo FAILURE: Firmware update failed.
) else (
    echo SUCCESS: Firmware updated. Device is rebooting...
)
pause
