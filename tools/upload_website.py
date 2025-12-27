import serial
import time
import sys
import os

PORT = "COM7"
BAUD = 115200

def send_at(ser, cmd, timeout=1, wait_for="OK"):
    print(f"Sending: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    
    start = time.time()
    response = ""
    while time.time() - start < timeout:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response += chunk
            sys.stdout.write(chunk)
            if wait_for and wait_for in response:
                return True, response
        time.sleep(0.01)
    return False, response

def upload_file(ser, remote_path, content):
    size = len(content)
    print(f"\nUploading {remote_path} (Size: {size} bytes)...")
    
    # 1. Create File
    # AT+FSC=<filename>,<size>
    success, _ = send_at(ser, f'AT+FSC="{remote_path}",{size}', timeout=2, wait_for="OK")
    if not success:
        print("Failed to create file!")
        return False
        
    # 2. Write File
    # AT+FSW=<filename>,<offset>,<length>
    # Note: We write in one go for simplicity, but large files might need chunking.
    cmd = f'AT+FSW="{remote_path}",0,{size}'
    print(f"Sending: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    
    # Wait for '>' prompt
    start = time.time()
    prompt_received = False
    while time.time() - start < 2:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            sys.stdout.write(data)
            if ">" in data:
                prompt_received = True
                break
        time.sleep(0.01)
        
    if not prompt_received:
        print("Did not receive write prompt '>'")
        return False
        
    # Send Content
    print("Sending content...")
    ser.write(content.encode())
    
    # Wait for OK
    start = time.time()
    while time.time() - start < 5:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            sys.stdout.write(data)
            if "OK" in data:
                print("\nUpload Successful!")
                return True
        time.sleep(0.01)
        
    print("\nUpload Timed Out!")
    return False

def main():
    try:
        print(f"Opening {PORT} at {BAUD}...")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        # Initialize FS
        # AT+FS=0 (Init) or AT+SYSFLASH? 
        # Usually checking generic AT ready first
        # Wait for AT ready
        print("Waiting for AT ready...")
        while True:
            success, _ = send_at(ser, "AT", timeout=0.5)
            if success:
                print("Device Ready!")
                break
            print(".", end="", flush=True)
            time.sleep(0.5)
        
        # Mount/Init FS usually happens automatically or via generic FS commands
        # Let's try to list files to ensure FS works
        print("Checking File System...")
        send_at(ser, 'AT+FSL', timeout=2) # List files
        
        # HTML Content
        html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f0f0f0; }
h1 { color: #333; }
.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: inline-block; }
</style>
</head>
<body>
<div class="card">
    <h1>ESP32 FATFS Web Server</h1>
    <p>This page is served from the ESP32 File System!</p>
    <p>Upload new files via UART without recompiling!</p>
</div>
</body>
</html>
"""
        
        # Upload index.html
        # Note: Web server mounts at /www by default according to code
        upload_file(ser, "index.html", html_content) 
        # Some implementations might need /www/index.html, but usually root of FS partition is mapped.
        # at_web_server_cmd.c says: #define ESP_AT_WEB_MOUNT_POINT "/www" 
        # But VFS logic usually maps partition to a mount point.
        # If FATFS is mounted at /www, then file path is /www/index.html.
        # But if AT+FSC writes to root of FATFS, and FATFS is mounted at /www for webserver...
        # Let's try writing to "index.html" first. If it fails or web server can't find it, we might need a directory.
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
