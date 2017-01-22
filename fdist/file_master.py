from log_actor import LogActor
from messages import MISSING_FILE, command, LOAD_FAILED_MESSAGE


class FileMaster(LogActor):
    def __init__(self, create_file_loader):
        super(FileMaster, self).__init__()

        self.create_file_loader = create_file_loader
        self.in_progress = []

    def on_receive(self, message):
        if command(message) == MISSING_FILE:
            missing_file = message['file']

            if missing_file not in self.in_progress:
                self.logger.info('loading file: [%s] from: [%s]', missing_file, message['ip'])
                self.start_file_loader(message)

        if command(message) == LOAD_FAILED_MESSAGE:
            self.in_progress.remove(message['file'])

    def start_file_loader(self, message):
        self.create_file_loader(message, self.actor_ref)
        self.in_progress.append(message['file'])
