import sys
import socket
import webview
import threading
import struct


def run_webview(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", int(port)))

    class Api:
        def destroy(self):
            send_message(client_socket, "destroy")

    def on_loaded():
        print("Webview is ready")
        send_message(client_socket, "webview_ready")

    api = Api()
    window = webview.create_window(
        "Woah dude!", "https://pywebview.flowrl.com", js_api=api
    )
    window.events.loaded += on_loaded

    # Start a thread to receive messages from the server
    threading.Thread(
        target=receive_messages, args=(client_socket,), daemon=True
    ).start()

    webview.start()
    send_message(client_socket, "exit")
    client_socket.close()


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


def receive_messages(client_socket):
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
            print(f"Received from server: {message}")
        except (ConnectionResetError, struct.error):
            break


if __name__ == "__main__":
    run_webview(sys.argv[1])
