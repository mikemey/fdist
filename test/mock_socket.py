import json
from SocketServer import TCPServer, UDPServer, BaseRequestHandler
from thread import start_new_thread


class MockServer(object):
    server_type = None
    handler_type = None

    def __init__(self, server_port):
        self.server = self.server_type(('', server_port), self.handler_type)
        self.server.data_records = []

        def start_listening(server):
            server.serve_forever()

        start_new_thread(start_listening, (self.server,))

    def received_data(self):
        return self.server.data_records

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class UDPHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        self.server.data_records.append(json.loads(data))


class MockUDPServer(MockServer):
    server_type = UDPServer
    handler_type = UDPHandler


class TCPHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.data_records.append(json.loads(data))


class MockTCPServer(MockServer):
    server_type = TCPServer
    handler_type = TCPHandler
