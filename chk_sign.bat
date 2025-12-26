@echo off
echo Verifying Bootloader Signature...
call esp-idf\export.bat
python esp-idf\components\esptool_py\esptool\espsecure.py verify_signature --version 2 --keyfile secure_boot_signing_key.pem build\bootloader\bootloader.bin
if %errorlevel% neq 0 (
    echo FAILURE: Signature verification FAILED.
) else (
    echo SUCCESS: Signature verification PASS.
)
pause
