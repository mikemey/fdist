import logging

import pykka

from messages import command, LOCAL_FILES, REMOTE_FILES, missing_file_message


class FilesDiff(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, receiver):
        super(FilesDiff, self).__init__()
        self.logger = logging.getLogger(FilesDiff.__name__)

        self.receiver = receiver
        self.local_files = []

    def on_start(self):
        self.logger.info('started')

    def on_receive(self, message):
        if command(message) is LOCAL_FILES:
            self.logger.info('new local file list: %s', message['files'])
            self.local_files = message['files']
        if command(message) is REMOTE_FILES:
            self.logger.info('new remote file list: %s', message['files'])
            self.update_remote_files(message)

    def update_remote_files(self, message):
        for new_file in message['files']:
            if new_file not in self.local_files:
                self.receiver.tell(missing_file_message(message['ip'], message['port'], new_file))
