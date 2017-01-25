import json
import logging
import os
import shutil
import socket

from fdist.exchange import read_data_from
from fdist.exchange.file_store import FileStore
from fdist.globals import FILE_REQUEST_TIMEOUT, TMP_DIR, SHARE_DIR, md5_hash
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, file_request_message, load_failed_message, file_id_of, pip_request_message, \
    command, PIP_DATA


def create_file_loader(missing_file_message, parent_actor):
    return FileLoader.start(SHARE_DIR, TMP_DIR, missing_file_message, parent_actor, FILE_REQUEST_TIMEOUT)


def send_receive(request, remote_address, timeout_sec):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_sec)
    try:
        sock.connect(remote_address)
        sock.sendall(json.dumps(request))

        return json.loads(read_data_from(sock))
    finally:
        sock.close()


class FileLoader(LogActor):
    def __init__(self, share_dir, tmp_dir, missing_file_message, parent_actor, timeout_sec):
        super(FileLoader, self).__init__()

        self.missing_file_id = file_id_of(missing_file_message)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])
        self.logger = logging.getLogger(self.missing_file_id)

        self.parent = parent_actor
        self.share_dir = share_dir
        self.tmp_dir = tmp_dir
        self.timeout_sec = timeout_sec

        self.cache_file_name = self.tmp_dir + "/" + md5_hash(self.missing_file_id)
        self.file_store_actor = None
        self.pip_loader_actor = PipLoader.start(self.actor_ref, self.missing_file_id,
                                                self.remote_address, self.timeout_sec)
        self.hashes = []
        self.indices = []

    def on_start(self):
        super(FileLoader, self).on_start()
        self.actor_ref.tell(SELF_POKE)

    def on_receive(self, message):
        try:
            if message is SELF_POKE:
                self.setup_file_loading()
                self.logger.debug('starting file transfer.')
                self.ensure_work_spread()

            if command(message) == PIP_DATA:
                pip_ix = int(message['pip_ix'])
                if pip_ix not in self.indices:
                    self.logger.warn('duplicate pip received, index [%s]', pip_ix)
                else:
                    self.file_store_actor.tell(message)
                    self.indices.remove(pip_ix)
                    if len(self.indices) > 0:
                        self.ensure_work_spread()
                    else:
                        self.move_to_target()
                        self.stop()

        except StandardError as _error:
            self.logger.error("failed: %s", _error)
            self.parent.tell(load_failed_message(self.missing_file_id))

    def setup_file_loading(self):
        self.logger.debug('requesting file location.')
        file_info_request = file_request_message(self.missing_file_id)
        file_info_message = send_receive(file_info_request, self.remote_address, self.timeout_sec)

        self.file_store_actor = FileStore.start(self.tmp_dir, file_info_message, self.cache_file_name)
        self.hashes = file_info_message['hashes']
        self.indices = [i for i in range(0, len(self.hashes))]

    def ensure_work_spread(self):
        if len(self.indices) <= 0:
            return
        self.pip_loader_actor.tell(pip_index(self.indices, self.hashes))

    def move_to_target(self):
        file_id = self.missing_file_id
        last_slash_ix = file_id.rfind('/')

        src = self.cache_file_name
        dest_folder = self.share_dir + file_id[:last_slash_ix]
        dest = self.share_dir + file_id

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        shutil.move(src, dest)


def pip_index(indices, hashes): return {
    'indices': indices,
    'hashes': hashes
}


class PipLoader(LogActor):
    def __init__(self, parent_actor, file_id, remote_address, timeout_sec):
        super(PipLoader, self).__init__(logging.DEBUG)

        self.parent_actor = parent_actor
        self.file_id = file_id
        self.remote_address = remote_address
        self.timeout_sec = timeout_sec

    def on_receive(self, message):
        pip_data = self.request_pip(message['indices'])
        hashes = message['hashes']
        if is_valid(pip_data, hashes):
            self.parent_actor.tell(pip_data)
        else:
            self.logger.warn('pip hash mismatch, pip-index: %s', pip_data['pip_ix'])

    def request_pip(self, indices):
        self.logger.debug('requesting pip.')

        pip_request = pip_request_message(self.file_id, indices)
        return send_receive(pip_request, self.remote_address, self.timeout_sec)


def is_valid(pip_data, hashes):
    pip_ix = int(pip_data['pip_ix'])
    pip_hash = md5_hash(pip_data['data'])
    return hashes[pip_ix] == pip_hash
