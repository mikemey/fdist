import logging
import os
import time

import pykka

CHECK = {'cmd': 'CHECK'}


class LocalFileSystem(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, receiver, directory, delay_seconds):
        super(LocalFileSystem, self).__init__()

        self.logger = logging.getLogger("fdist.fs.check")
        self.receiver = receiver
        self.directory = directory
        self.delay_seconds = delay_seconds
        self.file_message = {'files': []}

    def on_start(self):
        self.logger.info('started')
        self.poke()

    def on_receive(self, message):
        if message is CHECK:
            self.check_file_updates()
            time.sleep(self.delay_seconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(CHECK)

    def check_file_updates(self):
        files = os.listdir(self.directory)
        if cmp(files, self.file_message['files']):
            self.file_message['files'] = files
            self.receiver.tell(self.file_message)


class FileUpdater(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self):
        super(FileUpdater, self).__init__()
        self.logger = logging.getLogger("fdist.fs.update")

    def on_start(self):
        self.logger.info('started')

    def on_receive(self, message):
        if message['nodes']:
            self.logger.info('received new node list: %s', message['nodes'])
            self.update_nodes(message['nodes'])

    def update_nodes(self, nodes):
        pass
