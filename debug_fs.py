import serial
import time
import sys

def send_at_cmd(ser, cmd, timeout=3):
    print(f"\n[Sending]: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    
    buffer = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += data
            sys.stdout.write(data)
        time.sleep(0.1)
    return buffer

def main():
    port = "COM18"
    baud = 115200
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"Error opening {port}: {e}")
        return

    print("--- Starting FS Debug ---")
    
    # 1. Reset
    # send_at_cmd(ser, "AT+RST", 5) 

    # 2. Check Sys
    send_at_cmd(ser, "AT")
    
    # 3. List Files (Mounts FS)
    print("\n--- Listing Files ---")
    send_at_cmd(ser, "AT+FS=ls")
    
    # 4. Try Web Server Again
    print("\n--- Enabling Web Server ---")
    send_at_cmd(ser, "AT+WEBSERVER=1,80,60")
    
    ser.close()

if __name__ == "__main__":
    main()
