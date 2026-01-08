@echo off
echo Packaging update firmware...
python tools/pack_update.py --out build/update.pkg --app build/esp-at.bin --nvs build/customized_partitions/mfg_nvs.bin --fatfs build/customized_partitions/fatfs.bin
if %errorlevel% neq 0 (
    echo Packaging failed!
    exit /b %errorlevel%
)
echo Update package created at build/update.pkg
