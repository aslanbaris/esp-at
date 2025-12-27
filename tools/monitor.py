import serial
import time
import sys

def monitor(port='COM7', baud=115200, duration=30):
    print(f"Monitoring {port} at {baud} for {duration} seconds...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        start_time = time.time()
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(line)
                except Exception as e:
                    print(f"Error reading line: {e}")
            time.sleep(0.01)
        ser.close()
    except Exception as e:
        print(f"Failed to open serial port: {e}")

if __name__ == "__main__":
    monitor()
