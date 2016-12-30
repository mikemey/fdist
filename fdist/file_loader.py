import logging

from log_actor import LogActor


class ActorProvider(object):
    @staticmethod
    def create_file_loader():
        return FileLoader().start


class FileLoader(LogActor):
    def __init__(self):
        super(FileLoader, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
