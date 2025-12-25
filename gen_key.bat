@echo off
call esp-idf\export.bat
idf.py secure-generate-signing-key secure_boot_signing_key.pem
