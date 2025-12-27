import serial
import time
import sys

def read_response(ser, end_markers=["OK", "ERROR"], timeout=5):
    buffer = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += data
            sys.stdout.write(data) 
            
            for marker in end_markers:
                if marker in buffer:
                    return buffer
        time.sleep(0.1)
    return buffer

def send_at_cmd(ser, cmd, timeout=5):
    print(f"\n[Sending]: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    return read_response(ser, timeout=timeout)

def main():
    port = "COM18"
    baud = 115200
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"Error opening {port}: {e}")
        return

    print("--- Starting Web Server Test (Fixed Syntax) ---")
    
    # Enable Web Server: Enable=1, Port=80, Timeout=60
    # The source code requires the 3rd argument (reconnect_timeout)
    resp = send_at_cmd(ser, "AT+WEBSERVER=1,80,60")
    
    if "OK" in resp:
        print("\n\nSUCCESS! Web Server Enabled.")
        # Get IP Address to show user
        send_at_cmd(ser, "AT+CIFSR")
        print("\nNow connect to the SoftAP 'ESP32_Test' (password: 12345678)")
        print("And visit the IP address shown above (e.g. 192.168.4.1)")
        print("You should see the content of index.html")
    else:
        print("\n\nFAILED to enable web server.")
        
    ser.close()

if __name__ == "__main__":
    main()
