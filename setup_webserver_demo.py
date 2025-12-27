import serial
import time
import sys

def send_at_cmd(ser, cmd, timeout=2):
    print(f"Sending: {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(timeout)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response:\n{response}")
    return response

def main():
    port = "COM18"
    baud = 115200
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print(f"Error opening {port}: {e}")
        return

    print("--- Starting Web Server Test ---")
    
    # Reset to known state
    send_at_cmd(ser, "AT+RST", 5)
    send_at_cmd(ser, "AT")
    
    # Set to SoftAP mode
    send_at_cmd(ser, "AT+CWMODE=2")
    
    # Configure SoftAP: SSID, Password, Channel, Security
    send_at_cmd(ser, 'AT+CWSAP="ESP32_Test","12345678",5,3')
    
    # Enable Web Server on port 80
    send_at_cmd(ser, "AT+WEBSERVER=1,80")
    
    # Get IP Address
    send_at_cmd(ser, "AT+CIFSR")
    
    print("\n--- Test Configuration Complete ---")
    print("Please connect your Wi-Fi to 'ESP32_Test' with password '12345678'.")
    print("Then visit the IP address shown above (usually 192.168.4.1) in your browser.")

    ser.close()

if __name__ == "__main__":
    main()
