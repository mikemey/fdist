import logging
import random

import pykka

all_rand = []


def unique_id():
    def rand(): return random.randint(0, 100)

    r = rand()

    while r in all_rand:
        r = rand()
    all_rand.append(r)


class LogActor(pykka.ThreadingActor):
    def __init__(self, unique_name=False, level=logging.INFO):
        super(LogActor, self).__init__()
        self.logger = logging.getLogger(self.logger_name(unique_name))
        self.level = level

    def logger_name(self, unique_name):
        name = self.__class__.__name__
        if unique_name:
            name += '_' + str(unique_id())
        return name

    def on_start(self):
        self.logger.log(self.level, 'started')

    def on_stop(self):
        self.logger.log(self.level, 'stopped')
