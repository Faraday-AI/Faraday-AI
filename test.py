import http.server
import socketserver
import socket

def get_network_info():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "Unable to determine"
    return hostname, local_ip

HOST = "0.0.0.0"  # Bind to all interfaces
PORT = 4000       # Try another port
Handler = http.server.SimpleHTTPRequestHandler

hostname, local_ip = get_network_info()
print(f"System hostname: {hostname}")
print(f"Local IP: {local_ip}")
print(f"Starting server on all interfaces, port {PORT}...")
print(f"Try accessing:")
print(f"1. http://localhost:{PORT}")
print(f"2. http://127.0.0.1:{PORT}")
print(f"3. http://{local_ip}:{PORT}")

with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print("Server running...")
    httpd.serve_forever() 