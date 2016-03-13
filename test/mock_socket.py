import SocketServer
import json
import socket
from SocketServer import TCPServer
from _socket import timeout
from thread import start_new_thread
from time import sleep


class MockTCPServer(object):
    def __init__(self, server_address):
        self.server_address = server_address
        SocketServer.TCPServer.allow_reuse_address = True
        self.server = TCPServer(self.server_address, RecorderHandler)
        self.server.data_records = []

        def start_listening(server):
            server.serve_forever()

        start_new_thread(start_listening, (self.server,))
        sleep(0.1)

    def received(self):
        return self.server.data_records

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class RecorderHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.data_records.append(json.loads(data))


class MockUDPServer(object):
    def __init__(self, server_port):
        self.running = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(1.0)
        self.socket.bind(('', server_port))

        self.data_records = []
        start_new_thread(self.run, ())

    def run(self):
        while self.running:
            try:
                message, address = self.socket.recvfrom(1024)
                self.data_records.append(json.loads(message))
            except timeout:
                pass
        self.socket.close()

    def received(self):
        return self.data_records

    def stop(self):
        self.running = False
