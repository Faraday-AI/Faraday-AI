import socket
import requests
from urllib.error import URLError
import sys

def test_raw_socket():
    print("\nTesting raw socket connection...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 3000))
    if result == 0:
        print("✅ Socket connection successful!")
    else:
        print("❌ Socket connection failed")
        print(f"Error code: {result}")
    sock.close()

def test_http_request():
    print("\nTesting HTTP request...")
    try:
        response = requests.get('http://127.0.0.1:3000')
        print("✅ HTTP request successful!")
        print(f"Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ HTTP request failed")
        print("Could not connect to server")

if __name__ == '__main__':
    print("Network Connection Test")
    print("======================")
    
    test_raw_socket()
    test_http_request()
    
    print("\nIf both tests failed, check:")
    print("1. Is the server running?")
    print("2. Is your firewall blocking connections?")
    print("3. Is Norton or other security software interfering?")
    print("4. Try disabling your firewall temporarily for testing") 