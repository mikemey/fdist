from log_actor import LogActor
from messages import command, LOCAL_FILES, REMOTE_FILES, missing_file_message


class FilesDiff(LogActor):
    def __init__(self, receiver):
        super(FilesDiff, self).__init__()

        self.receiver = receiver
        self.local_files = set()

    def on_receive(self, message):
        if command(message) == LOCAL_FILES:
            self.logger.info('new local file list: %s', message['files'])
            self.local_files |= set(message['files'])
        if command(message) == REMOTE_FILES:
            self.logger.debug('remote file list: %s', message['files'])
            self.update_remote_files(message)

    def update_remote_files(self, message):
        for new_file in message['files']:
            if new_file not in self.local_files:
                self.receiver.tell(missing_file_message(message['ip'], message['port'], new_file))
