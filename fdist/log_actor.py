import logging

import pykka


class LogActor(pykka.ThreadingActor):
    def __init__(self, level=logging.INFO):
        super(LogActor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.level = level

    def on_start(self):
        self.logger.log(self.level, 'started')

    def on_stop(self):
        self.logger.log(self.level, 'stopped')
