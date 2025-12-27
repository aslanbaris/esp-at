import serial
import time
import sys

PORT = "COM7"
BAUD = 115200

def send_at(ser, cmd, timeout=1, wait_for=None):
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
                break
        time.sleep(0.1)
    return response

def start_server():
    try:
        print(f"Opening {PORT} at {BAUD}...")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        # Reset and ready
        send_at(ser, "AT+RST", timeout=2, wait_for="ready")
        time.sleep(1)
        send_at(ser, "AT+GMR", timeout=1)
        
        # Configure SoftAP
        send_at(ser, "AT+CWMODE=2", wait_for="OK")
        send_at(ser, 'AT+CWSAP="ESP32_Test","password123",5,3', wait_for="OK")
        
        # Enable Multiple Connections
        send_at(ser, "AT+CIPMUX=1", wait_for="OK")
        
        # Start Server on port 80
        send_at(ser, "AT+CIPSERVER=1,80", wait_for="OK")
        
        # Get IP
        send_at(ser, "AT+CIFSR", timeout=2)
        
        print("\n" + "="*40)
        print("Web Server Started!")
        print("Connect to Wi-Fi: ESP32_Test / password123")
        print("Open Browser: http://192.168.4.1")
        print("="*40 + "\n")
        
        while True:
            if ser.in_waiting:
                try:
                    data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    sys.stdout.write(data)
                    
                    if "+IPD" in data:
                        # Parse Link ID and Length roughly
                        # Format: +IPD,<id>,<len>:
                        # Example: +IPD,0,342:GET / HTTP/1.1...
                        
                        parts = data.split("+IPD,")
                        if len(parts) > 1:
                            meta = parts[1].split(',')
                            link_id = meta[0]
                            
                            print(f"\n[Incoming Request on Link ID {link_id}]")
                            
                            # Simple HTML Response
                            html = "<html><body><h1>Hello from ESP32 AT!</h1><p>Success.</p></body></html>"
                            response_headers = (
                                "HTTP/1.1 200 OK\r\n"
                                "Content-Type: text/html\r\n"
                                f"Content-Length: {len(html)}\r\n"
                                "Connection: close\r\n"
                                "\r\n"
                            )
                            full_response = response_headers + html
                            
                            # Send Data
                            send_at(ser, f"AT+CIPSEND={link_id},{len(full_response)}", wait_for=">")
                            ser.write(full_response.encode())
                            
                            time.sleep(0.5)
                            
                            # Close Connection
                            send_at(ser, f"AT+CIPCLOSE={link_id}", wait_for="OK")
                            
                except Exception as e:
                    print(f"Error reading/parsing: {e}")
                    
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nStopping server...")
        if ser.is_open:
            ser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_server()
