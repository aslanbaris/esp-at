@echo off
echo Generating Bootloader Reflash Digest...
call esp-idf\export.bat
python esp-idf\components\esptool_py\esptool\espsecure.py digest_secure_bootloader --keyfile secure_boot_signing_key.pem --output build\bootloader\bootloader-reflash-digest.bin build\bootloader\bootloader.bin
echo Done.
if exist build\bootloader\bootloader-reflash-digest.bin (
    echo SUCCESS: Digest file created.
) else (
    echo FAILURE: Digest file NOT created.
)
pause
