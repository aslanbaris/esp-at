@echo off
echo ========================================================
echo Generating and Flashing Valid FATFS Image...
echo ========================================================
call esp-idf\export.bat

rem Ensure 'construct' is installed (it should be in IDF env)
python -m pip install construct

rem Generate FATFS Image with WL support
echo Generating Image...
python esp-idf\components\fatfs\wl_fatfsgen.py --partition_size 1048576 --sector_size 4096 --long_name_support --output_file build\customized_partitions\fatfs_valid.bin fatfs_content

if %errorlevel% neq 0 (
    echo FAILURE: Image Generation Failed.
    pause
    exit /b %errorlevel%
)

rem Flash Image Encrypted
echo Flashing Image...
python -m esptool -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --force --encrypt ^
0x40000 build\customized_partitions\fatfs_valid.bin

if %errorlevel% neq 0 (
    echo FAILURE: Flash Failed.
) else (
    echo SUCCESS: FATFS Flashed (Encrypted). Device rebooting...
)
pause
