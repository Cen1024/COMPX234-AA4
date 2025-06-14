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