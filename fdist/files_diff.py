import json
import logging
import socket

import pykka


class FilesDiff(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self):
        super(FilesDiff, self).__init__()
        self.logger = logging.getLogger(FilesDiff.__name__)

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
        self.socket.send(json.dumps({"files": self.files}))
        self.socket.close()
