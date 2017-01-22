import json
import logging
import random
from io import FileIO

from fdist.log_actor import LogActor
from fdist.messages import pip_message, file_id_of


class PipServer(LogActor):
    def __init__(self, local_dir, pip_size):
        super(PipServer, self).__init__(logging.DEBUG)
        self.local_dir = local_dir
        self.pip_size = pip_size

    def on_receive(self, message):
        connection = message['connection']
        ip = message['ip']
        pip_request = message['parsed']
        file_id = file_id_of(pip_request)
        indices = pip_request['required_indices']
        self.logger.info("received pip request from %s : %s: %s pips missing.", ip, file_id, len(indices))
        try:
            pip_ix = random.choice(indices)
            response = pip_message(pip_ix, self.data(file_id, pip_ix))
            connection.sendall(json.dumps(response))
        finally:
            connection.close()

    def data(self, file_id, pip_ix):
        with FileIO(self.local_dir + file_id, 'r+') as fin:
            fin.seek(pip_ix * self.pip_size)
            return fin.read(self.pip_size)
