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