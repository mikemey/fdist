import logging
import os
import time

import pykka

from fdist.messages import local_files_message, SELF_POKE


class LocalFileSystem(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, receiver, local_directory, delay_seconds):
        super(LocalFileSystem, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.receiver = receiver
        self.localDirectory = local_directory
        self.pokeDelaySeconds = delay_seconds
        self.localFiles = []

    def on_start(self):
        self.logger.info('started')
        self.poke()

    def on_receive(self, message):
        if message is SELF_POKE:
            self.check_file_updates()
            time.sleep(self.pokeDelaySeconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(SELF_POKE)

    def check_file_updates(self):
        files = os.listdir(self.localDirectory)
        if cmp(files, self.localFiles):
            self.localFiles = files
            for recv in self.receiver:
                recv.tell(local_files_message(files))
