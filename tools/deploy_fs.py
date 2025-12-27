import os
import subprocess
import sys

# Configuration
PROJECT_ROOT = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at"
INPUT_DIR = os.path.join(PROJECT_ROOT, "web_preview", "admin_one")
OUTPUT_BIN = os.path.join(PROJECT_ROOT, "web_fs.bin")
PARTITION_SIZE = 1048576  # 1MB
FLASH_ADDRESS = "0x40000"
COM_PORT = "COM18"
BAUD_RATE = "921600"

# Tools
FATFSGEN = os.path.join(PROJECT_ROOT, "esp-idf", "components", "fatfs", "wl_fatfsgen.py")
ESPTOOL = os.path.join(PROJECT_ROOT, "esp-idf", "components", "esptool_py", "esptool", "esptool.py")

def main():
    print("--- ESP32 Web FS Deployer ---")
    
    # 1. Generate FATFS Image
    print(f"\n[1/2] Generating FATFS image from {INPUT_DIR}...")
    if os.path.exists(OUTPUT_BIN):
        os.remove(OUTPUT_BIN)
        
    cmd_gen = [
        sys.executable,
        FATFSGEN,
        "--partition_size", str(PARTITION_SIZE),
        "--sector_size", "512",
        "--fat_type", "12",
        "--wl_mode", "safe",
        "--long_name_support",
        "--output_file", OUTPUT_BIN,
        INPUT_DIR
    ]
    
    try:
        subprocess.check_call(cmd_gen)
        print(f"Success: Created {OUTPUT_BIN}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating image: {e}")
        return

    # 2. Flash Images
    print(f"\n[2/2] Flashing images to {COM_PORT}...")
    
    AT_CUSTOMIZE_BIN = os.path.join(PROJECT_ROOT, "build", "at_customize.bin")
    
    cmd_flash = [
        sys.executable,
        ESPTOOL,
        "--chip", "esp32",
        "--port", COM_PORT,
        "--baud", BAUD_RATE,
        "write_flash",
        "0x20000", AT_CUSTOMIZE_BIN,
        FLASH_ADDRESS, OUTPUT_BIN
    ]
    
    try:
        subprocess.check_call(cmd_flash)
        print("\n[SUCCESS] Deployment complete! Please reset the board if it doesn't auto-reset.")
    except subprocess.CalledProcessError as e:
        print(f"Error flashing: {e}")
        return

if __name__ == "__main__":
    main()
