import socket
import threading
import subprocess
import sys
import time
import struct
from pathlib import Path

_VIEW_DONE = False
_TIMEOUT = 10


def start_server():
    global _TIMEOUT, _VIEW_DONE
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 0))  # Bind to an available port
    host, port = server_socket.getsockname()

    server_socket.listen(1)
    server_socket.settimeout(_TIMEOUT)  # Set a timeout of 10 seconds

    # Start the webview subprocess and pass the port number
    root_dir = Path(__file__).resolve().parent
    webview_app_path = root_dir / "webview_app.py"
    subprocess.Popen([sys.executable, str(webview_app_path), str(port)])

    try:
        # Accept the connection from the client
        client_socket, _ = server_socket.accept()

        # Send a message to the client
        send_message(client_socket, "Hello from server")

        # Handle communication in a separate thread
        threading.Thread(
            target=handle_client, args=(client_socket,), daemon=True
        ).start()
    except socket.timeout:
        print(f"Accept timed out. No client connected within {_TIMEOUT} seconds.")
        server_socket.close()
        _VIEW_DONE = True


def send_message(sock, message):
    # Prefix each message with a 4-byte length (network byte order)
    message_bytes = message.encode()
    message_length = struct.pack("!I", len(message_bytes))
    sock.sendall(message_length + message_bytes)


def receive_all(sock, length):
    data = b""
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise ConnectionResetError("Connection closed prematurely")
        data += more
    return data


def handle_client(client_socket):
    global _VIEW_DONE
    while True:
        try:
            # Receive the message length first
            raw_msglen = receive_all(client_socket, 4)
            if not raw_msglen:
                break
            msglen = struct.unpack("!I", raw_msglen)[0]

            # Receive the actual message
            data = receive_all(client_socket, msglen)
            message = data.decode()
            print(f"Received From Client: {message}")

            if message == "exit":
                _VIEW_DONE = True
                break
        except (ConnectionResetError, struct.error):
            break
    client_socket.close()


if __name__ == "__main__":
    start_server()
    try:
        while True:
            if _VIEW_DONE:
                print("Webview is done")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
