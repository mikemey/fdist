import json
import logging
import os
import shutil
import socket
from _socket import error

from fdist.exchange import read_data_from
from fdist.globals import FILE_REQUEST_TIMEOUT, TMP_DIR, SHARE_DIR
from fdist.log_actor import LogActor
from fdist.messages import SELF_POKE, file_request_message, load_failed_message, FAILURE_MESSAGE, file_id_of


def create_file_loader(missing_file_message, parent_actor):
    return FileLoader.start(SHARE_DIR, TMP_DIR, missing_file_message, parent_actor, FILE_REQUEST_TIMEOUT)


class FileLoader(LogActor):
    def __init__(self, share_dir, tmp_dir, missing_file_message, parent_actor, timeout_sec):
        super(FileLoader, self).__init__()

        missing_file = file_id_of(missing_file_message)
        self.logger = logging.getLogger(missing_file)
        self.request_message = file_request_message(missing_file)
        self.remote_address = (missing_file_message['ip'], missing_file_message['port'])

        self.share_dir = share_dir
        self.tmp_dir = tmp_dir
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
                self.move_to_target(file_location_message)
        except StandardError as _error:
            self.logger.error("failed: %s", _error)
            file_id = file_id_of(self.request_message)
            self.parent.tell(load_failed_message(file_id))
        finally:
            self.stop()

    def send_file_request(self):
        self.logger.debug('requesting file location.')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout_sec)
        try:
            sock.connect(self.remote_address)
            sock.sendall(json.dumps(self.request_message))
            return json.loads(read_data_from(sock))
        finally:
            sock.close()

    def rsync_result(self, file_location_message):
        self.logger.debug('starting file transfer.')
        # rsync = RsyncWrapper.start(self.tmp_dir)
        # try:
        #     result = rsync.ask(file_location_message)
        #     return result
        # finally:
        #     rsync.stop()

    def move_to_target(self, file_location_message):
        file_id = file_id_of(file_location_message)
        last_slash_ix = file_id.rfind('/')

        src = self.tmp_dir + file_id[last_slash_ix:]
        dest_folder = self.share_dir + file_id[:last_slash_ix]
        dest = self.share_dir + file_id

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        shutil.move(src, dest)
