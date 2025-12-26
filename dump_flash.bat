@echo off
echo Dumping Flash 0x0 - 0x10000...
call esp-idf\export.bat
python -m esptool -p COM18 --chip esp32 -b 460800 read_flash 0x0 0x10000 dump_0_to_64k.bin
if %errorlevel% neq 0 (
    echo FAILURE: Read failed.
) else (
    echo SUCCESS: Read complete.
)
pause
