import json
import logging
import socket
from _socket import timeout, error
from time import sleep

from fdist.exchange.file_info_server import FileInfoServer
from fdist.exchange.pip_server import PipServer
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, command, FILE_REQUEST


def setup_socket(port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.settimeout(1.0)
    sck.bind(('', port))
    sck.listen(1)
    return sck


class FileExchangeServer(LogActor):
    def __init__(self, fe_port, local_dir, pip_size):
        super(FileExchangeServer, self).__init__()
        self.socket = setup_socket(fe_port)

        self.router = FileExchangeRouter.start(local_dir, pip_size)

    def on_start(self):
        super(FileExchangeServer, self).on_start()
        self.actor_ref.tell(SELF_POKE)

    def on_stop(self):
        self.socket.close()

    def on_receive(self, message):
        try:
            if message is SELF_POKE:
                self.server_read()
        except timeout:
            pass
        except StandardError as _error:
            self.logger.error("failed: %s", _error)
        finally:
            self.actor_ref.tell(SELF_POKE)

    def server_read(self):
        connection, (ip, _) = self.socket.accept()
        self.router.tell(accept_message(connection, ip))


def read_data_from(connection):
    tries = 3
    while tries:
        tries -= 1
        try:
            return connection.recv(1024)
        except error:
            sleep(0.1)
    return None


def accept_message(connection, ip, parsed_message=''): return {
    'connection': connection,
    'ip': ip,
    'parsed': parsed_message
}


class FileExchangeRouter(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileExchangeRouter, self).__init__(logging.DEBUG)
        self.info_actor = FileInfoServer.start(local_dir, pip_size)
        self.pip_actors = [PipServer.start() for i in range(0, 4)]

    def on_receive(self, connection_message):
        connection = connection_message['connection']
        ip = connection_message['ip']

        data = read_data_from(connection)
        request_message = json.loads(data)
        if command(request_message) == FILE_REQUEST:
            self.info_actor.tell(accept_message(connection, ip, request_message))
