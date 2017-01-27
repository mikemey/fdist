import json
import os
from io import FileIO
from math import ceil

from fdist.globals import md5_hash
from fdist.log_actor import LogActor
from fdist.messages import file_info_message, file_id_of


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
        try:
            file_id = file_id_of(request_message)
            hashes = self.hashes(file_id)
            info_response = file_info_message(file_id, self.pip_size, hashes)
            connection.sendall(json.dumps(info_response))
        finally:
            connection.close()

    def hashes(self, file_id):
        self.logger.debug("calculating hashes")
        full_path = self.local_dir + file_id
        pieces = int(ceil(os.path.getsize(full_path)) / float(self.pip_size))

        hashes = []
        with FileIO(self.local_dir + file_id, 'r+') as fin:
            pip = fin.read(self.pip_size)
            curr = 0
            while pip:
                curr += 1
                self.logger.debug("calculating %2s of %s", curr, pieces)
                hashes.append(md5_hash(pip))
                pip = fin.read(self.pip_size)
        return hashes
