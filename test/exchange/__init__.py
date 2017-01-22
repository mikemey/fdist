import json
import socket


def send_request_to(address, request_message, buffer_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(json.dumps(request_message))
        return sock.recv(buffer_size)
    finally:
        sock.close()
