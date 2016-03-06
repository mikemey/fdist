import SocketServer
import json
from SocketServer import TCPServer
from thread import start_new_thread
from time import sleep


class MockSocket(object):
    def __init__(self, server_address):
        self.server_address = server_address
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
        self.server.data_records += json.loads(data)
        # just send back the same data, but upper-cased
        # self.request.sendall(data.upper())
