@echo off
rem Step 1: Fix Bootloader ONLY
echo Flashing Bootloader (Safe Step 1)...
call esp-idf\export.bat
python -m esptool -p COM18 --chip esp32 -b 460800 --no-stub write_flash --force 0x1000 build\bootloader\bootloader.bin
if %errorlevel% neq 0 (
    echo FAILURE: Bootloader flash failed.
) else (
    echo SUCCESS: Step 1 Complete. Please Verify Dump.
)
pause
