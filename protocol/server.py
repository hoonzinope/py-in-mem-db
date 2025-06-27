import socket
import threading
from codec import encode, decode
from command_handler import Command

class Server:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.command = Command()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,addr)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, addr):
        try:
            request = client_socket.recv(1024).decode('utf-8')
            request = decode(request)  # Decode the request using the codec
            print(f"Received request: {request} from {addr}")

            response = self.process_request(request)
            response = encode(response)  # Encode the response using the codec
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def process_request(self, request):
        # Here you would process the request and return a response.
        # For simplicity, we just echo back the request.
        response = ""
        if request.strip() == "":
            response = "No command received"
        else:
            response =  self.command.execute(request.strip())
        return str(response) if response is not None else "Command executed successfully"

if __name__ == "__main__":
    server = Server()
    server.start()