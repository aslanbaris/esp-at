@echo off
echo Setting up ESP-AT Environment...
set ESP_AT_PROJECT_PLATFORM=PLATFORM_ESP32
set ESP_AT_MODULE_NAME=WROOM-32
set SILENCE=1
set IDF_TARGET=esp32

echo Backing up sdkconfig (if exists)...
if exist sdkconfig copy sdkconfig sdkconfig.bak

echo Setting up ESP-IDF toolchain...
call esp-idf\export.bat

echo.
echo Cleaning project (force removing build directory)...
if exist build rmdir /s /q build
if exist sdkconfig del sdkconfig

echo.
echo Building project (Generate new sdkconfig from defaults + Build)...
echo Generating module_info.json...
python -c "import json, os; os.makedirs('build', exist_ok=True); open('build/module_info.json', 'w').write(json.dumps({'platform': 'PLATFORM_ESP32', 'module': 'WROOM-32', 'silence': 1, 'description': '4MB, Wi-Fi + BLE, OTA, TX:17 RX:16'}))"
idf.py -DIDF_TARGET=esp32 build
if %errorlevel% neq 0 (
    echo FAILURE: Build failed.
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo SUCCESS: Build complete!
echo You can now proceed to flash Step 2.
echo ========================================================
