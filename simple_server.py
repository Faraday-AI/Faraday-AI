from http.server import HTTPServer, SimpleHTTPRequestHandler

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('127.0.0.1', 8000)
    httpd = server_class(server_address, handler_class)
    print("Server starting on http://127.0.0.1:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    run() 