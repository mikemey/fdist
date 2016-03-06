import json
import logging
import os
import socket
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
        self.nodes = []
        self.files = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_start(self):
        self.logger.info('started')

    def on_receive(self, message):
        if 'nodes' in message:
            self.logger.info('new node list: %s', message['nodes'])
            self.update_nodes(message['nodes'])
        if 'files' in message:
            self.logger.info('new file list: %s', message['files'])
            self.update_files(message['files'])

    def update_nodes(self, nodes_update):
        for node in nodes_update:
            if node not in self.nodes:
                self.send_file_list_to(node)
        self.nodes = nodes_update

    def update_files(self, files_update):
        self.files = files_update
        for node in self.nodes:
            self.send_file_list_to(node)

    def send_file_list_to(self, node):
        self.logger.debug('send to: %s -- %s', node, self.files)
        self.socket.connect(node)
        self.socket.send(json.dumps(self.files))
        self.socket.close()
