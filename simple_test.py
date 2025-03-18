from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

port = 8000
server_address = ('', port)
ip = get_ip()

print(f"Starting server at http://{ip}:{port}")
print(f"Also try: http://localhost:{port}")
print(f"Or: http://127.0.0.1:{port}")

httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
httpd.serve_forever() 