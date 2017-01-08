import json
import socket
from _socket import timeout

from log_actor import LogActor
from messages import SELF_POKE, command, FILE_REQUEST, file_location_message


def setup_socket(port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.settimeout(1.0)
    sck.bind(('', port))
    sck.listen(1)
    return sck


class FileInfo(LogActor):
    def __init__(self, fe_port, rsync_prefix):
        super(FileInfo, self).__init__()
        self.socket = setup_socket(fe_port)

        self.rsync_prefix = rsync_prefix

    def on_start(self):
        super(FileInfo, self).on_start()
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
        try:
            data = connection.recv(1024)
            message = json.loads(data)
            if command(message) == FILE_REQUEST:
                self.logger.info("received request from %s : %s", ip, message)
                file_id = message['file_id']
                location_message = file_location_message(file_id, self.rsync_prefix + file_id)
                connection.sendall(json.dumps(location_message))
        finally:
            connection.close()
