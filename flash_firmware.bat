@echo off
call esp-idf\export.bat
python -m esptool --chip esp32 -p COM18 -b 460800 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 16MB 0x1000 build\bootloader\bootloader.bin 0x200000 build\esp-at.bin 0x10000 build\partition_table\partition-table.bin 0x11000 build\ota_data_initial.bin 0x20000 build\at_customize.bin 0x21000 build\customized_partitions\mfg_nvs.bin 0x40000 build\customized_partitions\fatfs.bin
