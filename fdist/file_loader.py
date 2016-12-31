import json
import logging
import socket

from log_actor import LogActor
from messages import SELF_POKE, file_request_message


class FileLoaderProvider(object):
    @staticmethod
    def create_file_loader(missing_file_message):
        return FileLoader.start(missing_file_message)


class FileLoader(LogActor):
    def __init__(self, missing_file_message):
        super(FileLoader, self).__init__()

        missing_file = missing_file_message['file']
        self.logger = logging.getLogger(missing_file)
        self.request_message = file_request_message(missing_file)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])

    def on_start(self):
        super(FileLoader, self).on_start()
        self.actor_ref.tell(SELF_POKE)

    def on_receive(self, message):
        if message is SELF_POKE:
            self.send_file_request()

    def send_file_request(self):
        self.logger.info('requesting file location.')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        sock.connect(self.remote_address)
        sock.sendall(json.dumps(self.request_message))
        sock.close()
