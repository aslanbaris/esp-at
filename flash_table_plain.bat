@echo off
echo ========================================================
echo Flashing AT Custom Partition Table (Plaintext)...
echo Address: 0x20000
echo File: build\at_customize.bin
echo Mode: PLAINTEXT (Force)
echo ========================================================
call esp-idf\export.bat

rem Omitting --encrypt implies plaintext write
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force ^
0x20000 build\at_customize.bin

if %errorlevel% neq 0 (
    echo FAILURE: Table Flash Failed.
) else (
    echo SUCCESS: Table Flashed (Plaintext). Device rebooting...
)
pause
