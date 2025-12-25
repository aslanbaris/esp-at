@echo off
if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: fix_flash.bat COMx
    exit /b 1
)
set ESP_AT_MODULE_NAME=WROOM-32
set ESP_AT_PROJECT_PLATFORM=PLATFORM_ESP32
call esp-idf\export.bat
python -m esptool -p %1 --chip esp32 erase_flash --force
python -m esptool -p %1 --chip esp32 -b 460800 --before default_reset --after no_reset write_flash --force --flash_mode dio --flash_size 4MB --flash_freq 40m --encrypt 0x1000 build\bootloader\bootloader.bin 0x10000 build\partition_table\partition-table.bin 0x11000 build\ota_data_initial.bin 0xA0000 build\esp-at.bin
python -m esptool -p %1 --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash --force --flash_mode dio --flash_size 4MB --flash_freq 40m 0x14000 build\customized_partitions\mfg_nvs.bin 0x20000 build\at_customize.bin
idf.py -p %1 monitor
