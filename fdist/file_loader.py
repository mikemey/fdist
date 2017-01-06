import json
import logging
import socket
from _socket import error

from globals import FILE_REQUEST_TIMEOUT
from log_actor import LogActor
from messages import SELF_POKE, file_request_message, load_failed_message


class FileLoaderProvider(object):
    @staticmethod
    def create_file_loader(missing_file_message, parent_actor):
        return FileLoader.start(missing_file_message, parent_actor, FILE_REQUEST_TIMEOUT)


class FileLoader(LogActor):
    def __init__(self, missing_file_message, parent_actor, rsync_actor, timeout_sec):
        super(FileLoader, self).__init__()

        missing_file = missing_file_message['file']
        self.logger = logging.getLogger(missing_file)
        self.request_message = file_request_message(missing_file)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])

        self.parent = parent_actor
        self.rsync_actor = rsync_actor
        self.timeout_sec = timeout_sec

    def on_start(self):
        super(FileLoader, self).on_start()
        self.actor_ref.tell(SELF_POKE)

    def on_receive(self, message):
        try:
            if message is SELF_POKE:
                self.send_file_request()
        except error as socket_error:
            self.logger.error("failed: %s", socket_error)
            self.parent.tell(load_failed_message(self.request_message['file_id']))

    def send_file_request(self):
        self.logger.info('requesting file location.')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout_sec)

        sock.connect(self.remote_address)
        sock.sendall(json.dumps(self.request_message))

        self.rsync_actor.tell(json.loads(sock.recv(1024)))
        sock.close()
