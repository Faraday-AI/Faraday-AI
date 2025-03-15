from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    local_ip = get_ip()
    port = 3000
    
    print(f"\nTest server starting on:")
    print(f"1. http://{local_ip}:{port}")
    print(f"2. http://localhost:{port}")
    print(f"3. http://127.0.0.1:{port}\n")
    
    try:
        httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print("Server started successfully! Press Ctrl+C to stop.")
        print("If you see this message but can't connect, check your firewall settings.")
        httpd.serve_forever()
    except PermissionError:
        print("Error: Permission denied. Try running with sudo.")
    except OSError as e:
        print(f"Error: {e}")
        print("This might be due to:")
        print("1. Port already in use")
        print("2. Firewall blocking the connection")
        print("3. Security software interference") 