import logging

import pykka


class LogActor(pykka.ThreadingActor):
    def __init__(self):
        super(LogActor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_start(self):
        self.logger.info('started')

    def on_stop(self):
        self.logger.info('stopped')
