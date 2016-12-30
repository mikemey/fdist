import logging

import pykka


class ActorProvider(object):
    @staticmethod
    def create_file_loader():
        return FileLoader().start


class FileLoader(pykka.ThreadingActor):
    def __init__(self):
        super(FileLoader, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
