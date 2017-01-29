import json
import logging
import socket
from _socket import timeout

from fdist.exchange import read_data_from
from fdist.exchange.file_info_server import FileInfoServer
from fdist.exchange.pip_server import PipServer
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, FILE_REQUEST, accept_connection_message, PIP_REQUEST, command


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
        self.logger.debug('incoming connection from [%s]', ip)
        self.router.tell(accept_connection_message(connection, ip))


class FileExchangeRouter(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileExchangeRouter, self).__init__(logging.DEBUG)
        self.info_actor = FileInfoServer.start(local_dir, pip_size)
        self.pip_actors = [PipServer.start(local_dir, pip_size) for _ in range(0, 4)]
        self.current_actor_ix = 0

    def on_receive(self, connection_message):
        connection = connection_message['connection']
        ip = connection_message['ip']

        self.logger.debug('reading request...')
        data = read_data_from(connection, 'file-exchange-server')
        request_message = json.loads(data)
        accept_message = accept_connection_message(connection, ip, request_message)

        cmd = command(request_message)
        self.logger.debug('received request [%s]', cmd)
        if cmd == FILE_REQUEST:
            self.info_actor.tell(accept_message)
        elif cmd == PIP_REQUEST:
            actor_ref = self.pip_actors[self.current_actor_ix]
            self.update_actor_index()
            actor_ref.tell(accept_message)

    def update_actor_index(self):
        self.current_actor_ix = (self.current_actor_ix + 1) % len(self.pip_actors)
