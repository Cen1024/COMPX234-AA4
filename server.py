import socket
import sys
import threading
import random
import base64
import os

def handle_file_transmission(filename, client_addr, client_port):
    
    try:
        # Check if file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} not found")
            
        file_size = os.path.getsize(filename)
        
        # Create dedicated socket for this transfer
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            port = random.randint(50000, 51000)
            try:
                data_sock.bind(('', port))
                break
            except:
                continue  # Try another port if binding fails
            # Send OK response with port information
        response = f"OK {filename} SIZE {file_size} PORT {port}"
        data_sock.sendto(response.encode(), (client_addr, client_port))
        
        print(f"Serving {filename} to {client_addr}:{client_port} on port {port}")
        
        # Open file for reading
        with open(filename, 'rb') as f:
            while True:
                # Wait for client request
                data_sock.settimeout(5.0)  # Set timeout for client response
                try:
                    data, addr = data_sock.recvfrom(65536)
                except socket.timeout:
                    print("Client timed out, closing connection")
                    break
                    
                message = data.decode().strip()
                tokens = message.split()

                # Validate message format
                if len(tokens) < 3 or tokens[0] != "FILE" or tokens[1] != filename:
                    continue
                    
                # Handle CLOSE request
                if tokens[2] == "CLOSE":
                    data_sock.sendto(f"FILE {filename} CLOSE_OK".encode(), addr)
                    break
                    
                # Handle data request
                if tokens[2] == "GET" and tokens[3] == "START" and tokens[5] == "END":
                    try:
                        start = int(tokens[4])
                        end = int(tokens[6])
                        block_size = end - start + 1
                        
                        # Read requested data block
                        f.seek(start)
                        file_data = f.read(block_size)
                        
                        # Base64 encode and send
                        base64_data = base64.b64encode(file_data).decode()
                        response = (
                            f"FILE {filename} OK START {start} END {end} "
                            f"DATA {base64_data}"
                        )
                        data_sock.sendto(response.encode(), addr)
                    except Exception as e:
                        print(f"Error processing request: {e}")
        
        print(f"Completed transfer of {filename} to {client_addr}")
        
    except Exception as e:
        print(f"Transfer failed: {e}")
    finally:
        data_sock.close()
def main():
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        return
        
    port = int(sys.argv[1])
    
    # Create main socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"Server listening on port {port}")
    
    while True:
        try:
            # Wait for download request
            data, addr = sock.recvfrom(65536)
            message = data.decode().strip()
            tokens = message.split()
            
            # Validate DOWNLOAD request
            if len(tokens) != 2 or tokens[0] != "DOWNLOAD":
                continue
                
            filename = tokens[1]
            client_addr, client_port = addr
            
            # Start new thread for file transfer
            threading.Thread(
                target=handle_file_transmission,
                args=(filename, client_addr, client_port)
            ).start()
            
        except Exception as e:
            print(f"Error handling request: {e}")

if __name__ == "__main__":
    main()