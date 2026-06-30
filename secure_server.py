import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

USERNAME = "KlimHQ"
PASSWORD = "Q3B7i5N4o2"
HOST = "127.0.0.1"
PORT = 8090

class AuthHandler(SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Textile Mill Map"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        auth_header = self.headers.get('Authorization')
        expected = 'Basic ' + base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()

        if auth_header == expected:
            super().do_GET()
        else:
            self.do_AUTHHEAD()
            self.wfile.write(b'Authentication required.')

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), AuthHandler)
    print(f'Serving with Basic Auth on http://{HOST}:{PORT}')
    print(f'Username: {USERNAME}')
    print(f'Password: {PASSWORD}')
    print('Place this file in the same folder as index.html before running.')
    server.serve_forever()
