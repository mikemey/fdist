import json
import logging
import socket
from _socket import timeout, error
from time import sleep

from fdist.globals import md5_hash
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, command, FILE_REQUEST, file_info_message


def setup_socket(port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.settimeout(1.0)
    sck.bind(('', port))
    sck.listen(1)
    return sck


class FileInfoServer(LogActor):
    def __init__(self, fe_port, local_dir, pip_size):
        super(FileInfoServer, self).__init__()
        self.socket = setup_socket(fe_port)

        self.router = FileInfoRouter.start(local_dir, pip_size)

    def on_start(self):
        super(FileInfoServer, self).on_start()
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


class FileInfoRouter(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileInfoRouter, self).__init__(logging.DEBUG)
        self.info_actor = FileInfoActor.start(local_dir, pip_size)

    def on_receive(self, connection_message):
        connection = connection_message['connection']
        ip = connection_message['ip']

        data = read_data_from(connection)
        request_message = json.loads(data)
        if command(request_message) == FILE_REQUEST:
            self.info_actor.tell(accept_message(connection, ip, request_message))


class FileInfoActor(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileInfoActor, self).__init__()
        self.local_dir = local_dir
        self.pip_size = pip_size

    def on_receive(self, message):
        connection = message['connection']
        ip = message['ip']
        request_message = message['parsed']
        self.logger.info("received info request from %s : %s", ip, request_message)

        file_id = request_message['file_id']
        hashes = self.hashes(file_id)
        try:
            info_response = file_info_message(file_id, self.pip_size, hashes)
            connection.sendall(json.dumps(info_response))
        finally:
            connection.close()

    def hashes(self, file_id):
        hashes = []
        with open(self.local_dir + file_id, 'r+') as fin:
            pip = fin.read(self.pip_size)
            while pip:
                hashes.append(md5_hash(pip))
                pip = fin.read(self.pip_size)
        return hashes
