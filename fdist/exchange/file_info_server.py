import json
import os
from io import FileIO
from math import ceil

from fdist.exchange import send_data_to
from fdist.globals import md5_hash
from fdist.log_actor import LogActor
from fdist.messages import file_info_message, file_id_of


class FileInfoServer(LogActor):
    def __init__(self, local_dir, pip_size):
        super(FileInfoServer, self).__init__()
        self.local_dir = local_dir
        self.pip_size = pip_size
        self.hash_cache = {}

    def on_receive(self, message):
        connection = message['connection']
        ip = message['ip']
        request_message = message['parsed']
        self.logger.info("received info request from %s : %s", ip, request_message)
        try:
            file_id = file_id_of(request_message)
            hashes = self.hashes(file_id)
            info_response = file_info_message(file_id, self.pip_size, hashes)
            send_data_to(connection, json.dumps(info_response), 'file-info-server')
        finally:
            connection.close()

    def hashes(self, file_id):
        if file_id in self.hash_cache:
            self.logger.debug('cache hit [%s]', file_id)
        else:
            full_path = self.local_dir + file_id
            pieces = int(ceil(os.path.getsize(full_path)) / float(self.pip_size))
            self.logger.debug("%4s pieces, calculating hashes...", pieces)
            self.hash_cache[file_id] = self.calculate_hash(full_path)
            self.logger.debug("done")

        return self.hash_cache[file_id]

    def calculate_hash(self, full_path):
        hashes = []
        with FileIO(full_path, 'r+') as fin:
            pip = fin.read(self.pip_size)
            curr = 0
            while pip:
                curr += 1
                hashes.append(md5_hash(pip))
                pip = fin.read(self.pip_size)
        return hashes
