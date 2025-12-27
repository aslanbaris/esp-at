@echo off
copy sdkconfig.security_disabled sdkconfig
echo Security features disabled (Secure Boot ^& Flash Encryption OFF).
echo WARNING: Do NOT flash this to a production device with eFuses burned!
