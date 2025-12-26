@echo off
if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: ff.bat COMx
    exit /b 1
)

rem Set up ESP-IDF environment
call esp-idf\export.bat

rem Flash ALL partitions in a SINGLE command.
rem We use --no-stub and --force to bypass Secure Boot protections and potential stub encryption issues.
echo Flashing All Partitions...
python -m esptool -p %1 --chip esp32 -b 460800 --no-stub --before default_reset --after hard_reset write_flash --force --flash_mode dout --flash_size 16MB --flash_freq 40m ^
0x1000 build\bootloader\bootloader.bin ^
0x10000 build\partition_table\partition-table.bin ^
0x11000 build\ota_data_initial.bin ^
0x20000 build\at_customize.bin ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x200000 build\esp-at.bin

if %errorlevel% neq 0 exit /b %errorlevel%

echo Monitoring...
idf.py -p %1 monitor
