@echo off
echo Full Recovery: Flashing ALL App Partitions with Encryption...
call esp-idf\export.bat
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force --encrypt ^
0x10000 build\partition_table\partition-table.bin ^
0x11000 build\ota_data_initial.bin ^
0x20000 build\at_customize.bin ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x200000 build\esp-at.bin

if %errorlevel% neq 0 (
    echo FAILURE: Encrypted flash failed.
) else (
    echo SUCCESS: Recovery Flash Complete. Please Verify Monitor.
)
pause
