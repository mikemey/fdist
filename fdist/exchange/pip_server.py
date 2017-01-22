import logging

from fdist.log_actor import LogActor


class PipServer(LogActor):
    def __init__(self, local_dir, pip_size):
        super(PipServer, self).__init__(logging.DEBUG)
        self.local_dir = local_dir
        self.pip_size = pip_size

    def on_receive(self, message):
        pass
