@echo off
rem Combined Safe Flash Script (Bootloader + App)
echo Flashing All Images (Safe Combined)...
call esp-idf\export.bat
python -m esptool -p COM18 --chip esp32 -b 460800 --no-stub write_flash --force --flash_mode dout --flash_size 16MB --flash_freq 40m ^
0x1000 build\bootloader\bootloader.bin ^
0x10000 build\partition_table\partition-table.bin ^
0x11000 build\ota_data_initial.bin ^
0x20000 build\at_customize.bin ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x200000 build\esp-at.bin

if %errorlevel% neq 0 (
    echo FAILURE: Flash failed.
) else (
    echo SUCCESS: Flash Complete.
)
pause
