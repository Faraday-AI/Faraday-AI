import http.server
import socketserver

PORT = 8090
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"Starting test server on strict localhost...")
print(f"Try these URLs in Chrome in this exact order:")
print(f"1. http://localhost:{PORT}")
print(f"2. http://127.0.0.1:{PORT}")

with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
    print("Server running on localhost only...")
    httpd.serve_forever() 