import socket
from codec import encode, decode

if __name__ == "__main__":

    while True:
        # Connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8080))

        msg = input('cmd>> ')
        print(msg)
        if not msg or msg.lower() == 'exit':
            print("Exiting...")
            sock.close()
            break
        sock.send(encode(msg).encode('utf-8'))
        data = sock.recv(1024)
        data = decode(data.decode('utf-8'))
        print('Received:', data)