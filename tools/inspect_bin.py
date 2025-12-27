
import struct
import sys
import os

def check_bin(path):
    print(f"Inspecting {path}...")
    with open(path, "rb") as f:
        data = f.read(512)
    
    # Check for WL header?
    # WL header usually starts with something. 
    # esp_idf/components/wear_levelling/WL_Flash.cpp
    # dummy_state.pos = 0;
    # dummy_state.max_pos = 0;
    # dummy_state.move_count = 0;
    # dummy_state.access_count = 0;
    # dummy_state.max_count = 0;
    # loop_state.block_size = this->cfg.page_size;
    # loop_state.version = WL_VERSION;
    # loop_state.device_id = device_id;
    
    # Or just look for strings
    print(f"Header hex: {data[:64].hex()}")
    
    if b'FAT12' in data:
        print("Found 'FAT12' string in first sector")
    if b'FAT16' in data:
        print("Found 'FAT16' string in first sector")
        
    # Check signature 0x55 0xAA at 510
    if data[510] == 0x55 and data[511] == 0xAA:
        print("Valid Boot Sector Signature (0x55AA)")
    else:
        print(f"Invalid Boot Sector Signature: {hex(data[510])} {hex(data[511])}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_bin(sys.argv[1])
    else:
        print("Usage: python inspect_bin.py <path>")
