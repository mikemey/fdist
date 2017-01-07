import json
import logging
import socket
from thread import start_new_thread

from fdist.messages import remote_files_message

OWN_IP = socket.gethostbyname(socket.gethostname())


def setup_datagram_socket(port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.settimeout(1.0)
    sck.bind(('', port))
    return sck


class RemoteFiles(object):
    def __init__(self, receiver, broadcast_port):
        super(RemoteFiles, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = True

        self.socket = setup_datagram_socket(broadcast_port)
        self.logger.debug("socket opened [%s]", broadcast_port)
        self.receiver = receiver

    def start(self):
        self.logger.info('started')
        start_new_thread(self.run, ())
        return self

    def stop(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                try:
                    message, (ip, _) = self.socket.recvfrom(1024)
                    if ip != OWN_IP:
                        self.logger.debug("received from %s : %s", ip, message)

                        msg = json.loads(message)
                        port, files = msg['port'], msg['files']
                        self.receiver.tell(remote_files_message(ip, port, files))
                except StandardError:
                    pass
        finally:
            self.socket.close()
            self.logger.info('stopped')
