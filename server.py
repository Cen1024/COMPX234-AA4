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