from log_actor import LogActor
from messages import MISSING_FILE, command


class FileMaster(LogActor):
    def __init__(self, actor_provider):
        super(FileMaster, self).__init__()

        self.actor_provider = actor_provider
        self.in_progress_list = []

    def on_receive(self, message):
        if command(message) is MISSING_FILE:
            f = message['file']
            if f not in self.in_progress_list:
                self.logger.info('loading file: [%s] from: [%s]', message['file'], message['ip'])
                self.actor_provider.create_file_loader()
                self.in_progress_list.append(f)
