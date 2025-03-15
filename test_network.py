from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import time

def run_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Test server is running...")
    print("Opening Chrome to http://localhost:3000")
    time.sleep(1)
    webbrowser.get('chrome').open('http://localhost:3000')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 