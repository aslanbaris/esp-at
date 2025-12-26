@echo off
echo Setting up ESP-AT Environment...
set ESP_AT_PROJECT_PLATFORM=PLATFORM_ESP32
set ESP_AT_MODULE_NAME=WROOM-32
set SILENCE=1
set IDF_TARGET=esp32

echo Setting up ESP-IDF toolchain...
call esp-idf\export.bat

echo.
echo Backing up stale sdkconfig (Release Mode)...
if exist sdkconfig move sdkconfig sdkconfig.release_backup

echo Generating module_info.json...
python -c "import json, os; os.makedirs('build', exist_ok=True); open('build/module_info.json', 'w').write(json.dumps({'platform': 'PLATFORM_ESP32', 'module': 'WROOM-32', 'silence': 1, 'description': '4MB, Wi-Fi + BLE, OTA, TX:17 RX:16'}))"

echo.
echo Regenerating sdkconfig from defaults (Development Mode)...
idf.py -DIDF_TARGET=esp32 reconfigure

echo.
echo Launching Menuconfig for Verification...
echo Navigate to: "Security features" -> "Enable Flash Encryption on Boot" -> "Mode"
echo It should be: "Development (NOT RECOMMENDED)"
echo.
idf.py -DIDF_TARGET=esp32 menuconfig
