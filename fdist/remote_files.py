import json
import logging
import socket
from _socket import timeout
from thread import start_new_thread

from fdist.messages import remote_files_message

BROADCAST = {'cmd': 'BROADCAST'}


class RemoteFileSystem(object):
    def __init__(self, receiver, server_port):
        super(RemoteFileSystem, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = True

        self.socket = self.setup_socket(server_port)
        self.logger.debug("socket opened [%s]", server_port)
        self.receiver = receiver
        start_new_thread(self.run, ())

    def run(self):
        try:
            def read_from_raw(raw_message):
                msg = json.loads(raw_message)
                return msg['port'], msg

            while self.running:
                try:
                    message, (ip, _) = self.socket.recvfrom(1024)
                    port, message = read_from_raw(message)

                    self.logger.debug("received from [%s]:[%s]", ip, message)
                    self.receiver.tell(remote_files_message(ip, port, message['files']))
                except timeout:
                    pass
        finally:
            self.socket.close()

    @staticmethod
    def setup_socket(server_port):
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sck.settimeout(1.0)
        sck.bind(('', server_port))
        return sck

    def stop(self):
        self.running = False
