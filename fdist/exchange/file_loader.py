import json
import logging
import os
import shutil
import socket
import traceback
from time import sleep

from fdist.exchange import read_data_from, send_data_to
from fdist.exchange.file_store import FileStore
from fdist.globals import TMP_DIR, SHARE_DIR, md5_hash
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, file_request_message, load_failed_message, file_id_of, pip_request_message, \
    command, PIP_DATA, empty_pip_message, EMPTY_PIP_DATA


def create_file_loader(missing_file_message, parent_actor):
    return FileLoader.start(SHARE_DIR, TMP_DIR, missing_file_message, parent_actor)


def send_receive(request, remote_address, src):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(remote_address)
        send_data_to(sock, json.dumps(request), src)
        return json.loads(read_data_from(sock, src).decode(errors="ignore"))
    finally:
        sock.close()


class FileLoader(LogActor):
    def __init__(self, share_dir, tmp_dir, missing_file_message, parent_actor):
        super(FileLoader, self).__init__()

        self.missing_file_id = file_id_of(missing_file_message)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])
        self.logger = logging.getLogger(self.missing_file_id)

        self.parent = parent_actor
        self.share_dir = share_dir
        self.tmp_dir = tmp_dir

        self.cache_file_name = self.tmp_dir + "/" + md5_hash(self.missing_file_id)
        self.file_store_actor = None
        self.pip_loader_actor = PipLoader.start(self.actor_ref, self.missing_file_id, self.remote_address)
        self.hashes = []
        self.indices = []

    def on_start(self):
        super(FileLoader, self).on_start()

        file_info_message = self.request_file_info()
        if file_info_message:
            self.file_store_actor = FileStore.start(self.tmp_dir, file_info_message, self.cache_file_name)
            self.hashes = file_info_message['hashes']
            self.indices = [i for i in range(0, len(self.hashes))]

            self.request_pip()
            self.actor_ref.tell(SELF_POKE)

    def request_file_info(self):
        self.logger.debug('requesting file info.')
        file_info_request = file_request_message(self.missing_file_id)
        try:
            return send_receive(file_info_request, self.remote_address, 'file-loader')
        except StandardError as _error:
            self.handle_error(_error)

    def on_receive(self, message):
        try:
            self.ensure_pip_loader_alive()
            if message is SELF_POKE:
                sleep(1)
                self.actor_ref.tell(SELF_POKE)

            if command(message) == EMPTY_PIP_DATA:
                self.request_pip()

            if command(message) == PIP_DATA:
                pip_ix = int(message['pip_ix'])
                if pip_ix not in self.indices:
                    self.logger.warn('duplicate pip received, index [%s]', pip_ix)
                else:
                    self.file_store_actor.tell(message)
                    self.indices.remove(pip_ix)
                    if len(self.indices) > 0:
                        self.request_pip()
                    else:
                        self.handle_success()

        except StandardError as _error:
            self.handle_error(_error)

    def on_stop(self):
        super(FileLoader, self).on_stop()
        if self.pip_loader_actor.is_alive():
            self.pip_loader_actor.stop()
        if self.file_store_actor and self.file_store_actor.is_alive():
            self.file_store_actor.stop()

    def request_pip(self):
        self.pip_loader_actor.tell(pip_index(self.indices, self.hashes))

    def handle_success(self):
        self.file_store_actor.stop()
        while self.file_store_actor.is_alive():
            self.logger.debug('waiting for file store to finish...')
            sleep(1)

        file_id = self.missing_file_id
        last_slash_ix = file_id.rfind('/')

        src = self.cache_file_name
        dest_folder = self.share_dir + file_id[:last_slash_ix]
        dest = self.share_dir + file_id

        self.logger.debug('moving file to [%s]', dest)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        shutil.move(src, dest)
        self.stop()

    def ensure_pip_loader_alive(self):
        if not self.pip_loader_actor.is_alive():
            self.handle_error('pip loader error.')

    def handle_error(self, description):
        self.logger.error("failed: %s", description)
        traceback.print_exc()
        self.parent.tell(load_failed_message(self.missing_file_id))
        self.stop()


def pip_index(indices, hashes): return {
    'indices': indices,
    'hashes': hashes
}


class PipLoader(LogActor):
    def __init__(self, parent_actor, file_id, remote_address):
        super(PipLoader, self).__init__(unique_name=True, level=logging.DEBUG)

        self.parent_actor = parent_actor
        self.file_id = file_id
        self.remote_address = remote_address

    def on_receive(self, message):
        pip_data = self.request_pip(message['indices'])
        hashes = message['hashes']
        if self.is_valid(pip_data, hashes):
            self.parent_actor.tell(pip_data)
        else:
            self.logger.warn('pip hash mismatch, pip-index: %s', pip_data['pip_ix'])
            self.parent_actor.tell(empty_pip_message())

    def request_pip(self, indices):
        pip_request = pip_request_message(self.file_id, indices)
        self.logger.debug('requesting pip [%s]', pip_request)
        return send_receive(pip_request, self.remote_address, 'pip-loader')

    def is_valid(self, pip_data, hashes):
        pip_ix = int(pip_data['pip_ix'])
        data_ = pip_data['data']
        pip_hash = md5_hash(data_)
        self.logger.debug('  expected hash [%s]-[%s]-[%s]', hashes[pip_ix])
        self.logger.debug('calculated hash [%s]', pip_hash)
        return hashes[pip_ix] == pip_hash
