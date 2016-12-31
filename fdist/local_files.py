import os
import time

from fdist.messages import local_files_message, SELF_POKE
from log_actor import LogActor


class LocalFiles(LogActor):
    def __init__(self, receiver, local_directory, delay_seconds):
        super(LocalFiles, self).__init__()

        self.receiver = receiver
        self.localDirectory = local_directory
        self.pokeDelaySeconds = delay_seconds
        self.cached_files = []

    def on_start(self):
        super(LocalFiles, self).on_start()
        self.poke()

    def on_receive(self, message):
        if message is SELF_POKE:
            self.check_file_updates()
            time.sleep(self.pokeDelaySeconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(SELF_POKE)

    def check_file_updates(self):
        files = self.local_files()
        if cmp(files, self.cached_files):
            self.cached_files = files
            for recv in self.receiver:
                recv.tell(local_files_message(files))

    def local_files(self):
        file_list = []
        self.flatten_files('', file_list)
        return file_list

    def flatten_files(self, relative_dir, result):
        file_list = os.listdir(self.localDirectory + '/' + relative_dir)

        for f in file_list:
            if f.startswith('.'):
                continue
            if os.path.isfile(self.localDirectory + '/' + relative_dir + '/' + f):
                result.append(relative_dir + '/' + f)
            if os.path.isdir(self.localDirectory + '/' + relative_dir + '/' + f):
                self.flatten_files(relative_dir + '/' + f, result)
