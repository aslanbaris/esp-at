import serial
import time
import sys

def read_until(ser, markers, timeout=10):
    buffer = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting:
            c = ser.read().decode(errors='ignore')
            buffer += c
            sys.stdout.write(c)
            sys.stdout.flush()
            for m in markers:
                if m in buffer:
                    return buffer
        else:
            time.sleep(0.01)
    return buffer

def send_cmd(ser, cmd, wait_for=["OK", "ERROR"], timeout=5):
    print(f"\n>> Sending: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    return read_until(ser, wait_for, timeout)

def main():
    port = "COM7"
    baud = 115200

    print(f"Opening {port} at {baud}...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return

    # Toggle DTR/RTS to reset (Standard ESP32 Reset)
    print("Resetting board...")
    ser.dtr = False
    ser.rts = True
    time.sleep(0.1)
    ser.dtr = True
    ser.rts = True
    time.sleep(0.1)
    ser.dtr = False # Release reset
    ser.rts = False

    # Wait for ready
    print("Waiting for boot...")
    read_until(ser, ["ready"], timeout=10)

    # Disable Echo
    send_cmd(ser, "ATE0")

    # Check AT
    send_cmd(ser, "AT")

    # Set SoftAP Mode
    send_cmd(ser, "AT+CWMODE=2")

    # Configure AP
    send_cmd(ser, 'AT+CWSAP="ESP32_Test","12345678",5,3')

    # Enable Web Server (3 args!)
    resp = send_cmd(ser, "AT+WEBSERVER=1,80,60", timeout=10)
    
    if "OK" in resp:
        print("\n[SUCCESS] Web Server Enabled!")
        send_cmd(ser, "AT+CIFSR")
        print("\nPlease connect to WiFi 'ESP32_Test' (pass: 12345678) and visit the IP above.")
    else:
        print("\n[FAILURE] Could not enable Web Server.")

    ser.close()

if __name__ == "__main__":
    main()
