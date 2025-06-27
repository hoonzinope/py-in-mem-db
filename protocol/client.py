import socket
from codec import encode, decode
import readline

class Client:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except socket.error as e:
            raise ConnectionError(f"Could not connect to server at {self.host}:{self.port}. Error: {e}")

    def send_command(self, command):
        if not self.sock:
            raise ConnectionError("Client is not connected to the server.")
        encoded_command = encode(command)
        self.sock.send(encoded_command.encode('utf-8'))

    def receive_response(self):
        if not self.sock:
            raise ConnectionError("Client is not connected to the server.")
        data = self.sock.recv(1024)
        return decode(data.decode('utf-8'))

    def close(self):
        if self.sock:
            self.sock.close()

    def run(self):
        self.connect()
        try:
            while True:
                command = input('cmd>> ')
                if command.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                self.send_command(command)
                response = self.receive_response()
                print('Received:', response)
        finally:
            self.close()

if __name__ == "__main__":
    client = Client()
    client.run()