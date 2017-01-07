import json
import logging
import socket
from _socket import error

from globals import FILE_REQUEST_TIMEOUT
from log_actor import LogActor
from messages import SELF_POKE, file_request_message, load_failed_message, FAILURE_MESSAGE
from rsync_wrapper import RsyncWrapper


class FileLoaderProvider(object):
    @staticmethod
    def create_file_loader(missing_file_message, parent_actor):
        return FileLoader.start(missing_file_message, parent_actor, FILE_REQUEST_TIMEOUT)


class FileLoader(LogActor):
    def __init__(self, missing_file_message, parent_actor, timeout_sec):
        super(FileLoader, self).__init__()

        missing_file = missing_file_message['file']
        self.logger = logging.getLogger(missing_file)
        self.request_message = file_request_message(missing_file)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])

        self.parent = parent_actor
        self.timeout_sec = timeout_sec

    def on_start(self):
        super(FileLoader, self).on_start()
        self.actor_ref.tell(SELF_POKE)

    def on_receive(self, message):
        try:
            if message is SELF_POKE:
                file_location_message = self.send_file_request()
                rsync_result = self.rsync_result(file_location_message)
                if rsync_result == FAILURE_MESSAGE:
                    raise error('rsync failed')

        except error as socket_error:
            self.logger.error("failed: %s", socket_error)
            self.parent.tell(load_failed_message(self.request_message['file_id']))

    def rsync_result(self, file_location_message):
        self.logger.debug('starting file transfer.')
        rsync = RsyncWrapper.start()
        try:
            result = rsync.ask(file_location_message)
            return result
        finally:
            rsync.stop()

    def send_file_request(self):
        self.logger.debug('requesting file location.')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout_sec)
        try:
            sock.connect(self.remote_address)
            sock.sendall(json.dumps(self.request_message))
            return json.loads(sock.recv(1024))
        finally:
            sock.close()
