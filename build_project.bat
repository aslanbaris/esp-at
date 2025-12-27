@echo off
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
