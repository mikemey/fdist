from log_actor import LogActor
from messages import MISSING_FILE, command, LOAD_FAILED_MESSAGE, file_id_of


class FileMaster(LogActor):
    def __init__(self, create_file_loader):
        super(FileMaster, self).__init__()

        self.create_file_loader = create_file_loader
        self.in_progress = []

    def on_receive(self, message):
        if command(message) == MISSING_FILE:
            missing_file = file_id_of(message)

            if missing_file not in self.in_progress:
                self.logger.info('loading file: [%s] from: [%s]', missing_file, message['ip'])
                self.start_file_loader(message)

        if command(message) == LOAD_FAILED_MESSAGE:
            self.in_progress.remove(file_id_of(message))

    def start_file_loader(self, message):
        self.create_file_loader(message, self.actor_ref)
        self.in_progress.append(file_id_of(message))
