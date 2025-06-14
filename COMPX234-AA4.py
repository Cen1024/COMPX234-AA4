import socket
import sys
import base64
import os

def send_and_receive(sock, message, address, port, max_retries=5, initial_timeout=1.0):
   
    current_timeout = initial_timeout
    retries = 0
    original_timeout = sock.gettimeout()  # Save original timeout
    while retries < max_retries:
        try:
            # Send message
            sock.sendto(message.encode(), (address, port))
            sock.settimeout(current_timeout)
            
            # Wait for response
            data, _ = sock.recvfrom(65536)  # Max UDP packet size
            return data.decode()
        except socket.timeout:
            retries += 1
            current_timeout *= 2  # Exponential backoff
            print(f"Timeout, retrying... (attempt {retries})")
        except Exception as e:
            print(f"Error: {e}")
            break
        finally:
            sock.settimeout(original_timeout)  # Restore original timeout
    
    raise Exception("Max retries exceeded, giving up")

def main():
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <hostname> <port> <filelist>")
        return
    
    hostname = sys.argv[1]
    server_port = int(sys.argv[2])
    filelist_name = sys.argv[3]
    
    # Read list of files to download
    try:
        with open(filelist_name, 'r') as f:
            files = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading file list: {e}")
        return
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for filename in files:
        print(f"Requesting: {filename}")
        try:
            # Send DOWNLOAD request
            response = send_and_receive(
                sock, 
                f"DOWNLOAD {filename}", 
                hostname, 
                server_port
            )
            
            # Handle server response
            if response.startswith("ERR"):
                print(f"Server error: {response}")
                continue
                
            # Parse OK response
            parts = response.split()
            if parts[0] != "OK" or parts[1] != filename:
                print(f"Invalid response: {response}")
                continue
                
            # Extract file size and data port
            file_size = int(parts[3])  # SIZE value
            data_port = int(parts[5])  # PORT value
            print(f"Downloading {filename} ({file_size} bytes)")
            