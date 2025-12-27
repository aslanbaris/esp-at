import serial
import time
import sys

def main():
    port = "COM7"
    baud = 115200

    print(f"Opening {port} at {baud}...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return

    # Toggle DTR/RTS to reset
    print("Resetting board to capture boot logs...")
    ser.dtr = False
    ser.rts = True
    time.sleep(0.1)
    ser.dtr = True
    ser.rts = True
    time.sleep(0.1)
    ser.dtr = False 
    ser.rts = False

    # Read logs for 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        if ser.in_waiting:
            c = ser.read(ser.in_waiting).decode(errors='ignore')
            sys.stdout.write(c)
        time.sleep(0.01)

    ser.close()

if __name__ == "__main__":
    main()
