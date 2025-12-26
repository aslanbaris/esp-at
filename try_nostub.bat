@echo off
echo Flashing Bootloader No Stub Force...
call esp-idf\export.bat
python -m esptool -p COM18 --chip esp32 -b 460800 --no-stub write_flash --force 0x1000 build\bootloader\bootloader.bin
if %errorlevel% neq 0 (
    echo FAILURE: Write failed.
) else (
    echo SUCCESS: Write No Stub Complete.
)
pause
