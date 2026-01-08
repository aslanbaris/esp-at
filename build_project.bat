@echo off
if not exist "build" mkdir build
echo {"platform": "PLATFORM_ESP32", "module": "WROOM-32", "description": "", "silence": 0} > build\module_info.json

echo ========================================================
echo Building ESP-AT Firmware (via build.py)...
echo ========================================================
call esp-idf\export.bat

python build.py build

if %errorlevel% neq 0 (
    echo FAILURE: Build Failed.
    exit /b %errorlevel%
)

echo SUCCESS: Build Complete.
