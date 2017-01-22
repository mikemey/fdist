import json
import logging
import socket
from _socket import timeout, error
from time import sleep

from fdist.globals import md5_hash
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, command, FILE_REQUEST, file_info_message


class FileInfoServer(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileInfoServer, self).__init__()
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
