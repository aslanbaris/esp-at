@echo off
echo Setting up ESP-AT Environment...
set ESP_AT_PROJECT_PLATFORM=PLATFORM_ESP32
set ESP_AT_MODULE_NAME=WROOM-32
set SILENCE=1
set IDF_TARGET=esp32

echo Setting up ESP-IDF toolchain...
call esp-idf\export.bat

echo.
echo Building project (PRESERVING verified sdkconfig)...
idf.py -DIDF_TARGET=esp32 build
if %errorlevel% neq 0 (
    echo FAILURE: Build failed.
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo SUCCESS: Build complete!
echo You can now proceed to flash.
echo ========================================================
