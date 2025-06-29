from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler, HTTPServer
import json
from command_handler import Command
from response import Response

post_path = ['get','exists','alias','find', 'clear']
get_path = ['keys','values',
                 'items','size','help',
                 'show-alias',
                 'begin','commit','rollback']
put_path = ['put', 'batch']
delete_path = ['delete', 'reset-alias']
command = Command()

class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.server = server
        self.client_address = client_address
        self.type = None
        print(f"New request from {client_address}")

    def do_GET(self):
        self.type = self._path_branch()
        if self.type is None or self.type != 'GET':
            self.send_error(404, "Path not found")
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = self._return_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        self.type = self._path_branch()
        if self.type is None or self.type != 'POST':
            self.send_error(404, "Path not found")
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = self._return_response(data)
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_PUT(self):
        self.type = self._path_branch()
        if self.type is None or self.type != 'PUT':
            self.send_error(404, "Path not found")
            return
        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)
        data = json.loads(put_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = self._return_response(data)
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_DELETE(self):
        self.type = self._path_branch()
        if self.type is None or self.type != 'DELETE':
            self.send_error(404, "Path not found")
            return
        content_length = int(self.headers['Content-Length'])
        delete_data = self.rfile.read(content_length)
        data = json.loads(delete_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = self._return_response(data)
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def _path_branch(self):
        # This method can be used to handle different paths if needed
        path = self.path.strip('/')
        if path in post_path:
            return 'POST'
        elif path in get_path:
            return 'GET'
        elif path in put_path:
            return 'PUT'
        elif path in delete_path:
            return 'DELETE'
        else:
            self.send_error(404, "Path not found")
            return None

    def _return_response(self, request_data = None):
        command_string = self.path.strip("/") + " " + request_data['command'] if request_data else self.path.strip("/")
        session_id = self.client_address[1]
        response_obj = command.execute(command_string, session_id)
        response = {
            'received': request_data,
            'status': response_obj.status_code,
            'message': response_obj.message,
            'data': response_obj.data
        }
        return response

if __name__ == '__main__':
    server_address = ('localhost', 8080)
    httpd = ThreadingHTTPServer(server_address, HttpHandler)
    print('Starting HTTP server on port 8080...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping HTTP server...')
        httpd.server_close()
        print('HTTP server stopped.')
