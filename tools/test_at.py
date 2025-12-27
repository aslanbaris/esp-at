import serial
import time
import sys

PORT = "COM7"
BAUD = 115200

def _send(ser, cmd):
    print(f"CMD: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(1) # Wait for response
    print(ser.read_all().decode(errors='ignore'))
    print("-" * 20)

def test_at():
    try:
        print(f"Opening {PORT} at {BAUD}...")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        print("Sending 'AT' command...")
        _send(ser, "AT")
        
        print("Checking Flash Partitions...")
        _send(ser, "AT+SYSFLASH?")
        
        print("Erasing FATFS to trigger Auto-Format...")
        _send(ser, 'AT+SYSFLASH=0,"fatfs"')
        
        print("Setting SoftAP Mode...")
        _send(ser, "AT+CWMODE=2")
        
        print("Trying to Enable Web Server (trigger mount)...")
        _send(ser, "AT+WEBSERVER=1,80,30")
        
        print("Checking File System...")
        _send(ser, "AT+FSL")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_at()
