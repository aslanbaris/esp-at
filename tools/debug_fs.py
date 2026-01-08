import serial
import time
import sys

def read_until(ser, markers, timeout=5):
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

def send_cmd(ser, cmd, timeout=2):
    print(f"\n>> Sending: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    return read_until(ser, ["OK", "ERROR"], timeout)

def main():
    port = "COM7"
    baud = 115200

    print(f"Opening {port} at {baud}...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return

    # Reset to clear state
    print("Resetting device...")
    send_cmd(ser, "AT+RST", timeout=5)
    time.sleep(3) # Wait for boot

    # Check AT
    send_cmd(ser, "AT")
    
    # Check Version
    send_cmd(ser, "AT+GMR")

    # Check Partitions
    # Command to show user partitions
    send_cmd(ser, "AT+SYSFLASH?")

    # Try to enable Web Server (this triggers mount)
    print("\nAttempting to start Web Server...")
    # Disable first just in case
    send_cmd(ser, "AT+WEBSERVER=0")
    time.sleep(1)
    
    # Enable
    resp = send_cmd(ser, "AT+WEBSERVER=1,80,60")
    if "OK" in resp:
        print("\n[SUCCESS] Web Server started!")
        time.sleep(1)
        send_cmd(ser, "AT+FSL")
    else:
        print("\n[FAILURE] Web Server failed to start.")
    
    ser.close()

if __name__ == "__main__":
    main()
