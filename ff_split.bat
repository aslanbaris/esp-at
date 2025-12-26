@echo off
if "%1"=="" (
    echo Error: Please specify the COM port.
    echo Usage: ff_split.bat COMx
    exit /b 1
)

rem Set up ESP-IDF environment
call esp-idf\export.bat

echo ========================================================
echo STEP 1: Flashing Bootloader (Protected Region)
echo Using --no-stub and --force to unlock bootloader partition.
echo ========================================================
python -m esptool -p %1 --chip esp32 -b 460800 --no-stub write_flash --force --flash_mode dout --flash_size 16MB --flash_freq 40m ^
0x1000 build\bootloader\bootloader.bin

if %errorlevel% neq 0 (
    echo FAILURE: Bootloader flash failed.
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo STEP 2: Flashing Application & Partitions (Standard Mode)
echo ========================================================
python -m esptool -p %1 --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash --flash_mode dout --flash_size 16MB --flash_freq 40m ^
0x10000 build\partition_table\partition-table.bin ^
0x11000 build\ota_data_initial.bin ^
0x20000 build\at_customize.bin ^
0x21000 build\customized_partitions\mfg_nvs.bin ^
0x200000 build\esp-at.bin

if %errorlevel% neq 0 (
    echo FAILURE: App flash failed.
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo SUCCESS: All partitions flashed. Monitoring...
echo ========================================================
idf.py -p %1 monitor
