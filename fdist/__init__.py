import logging
import sys
import time

import pykka
from pykka.registry import ActorRegistry

from announcer import Announcer
from files_diff import FilesDiff
from local_files import LocalFileSystem
from messages import command, MISSING_FILE
from remote_files import RemoteFileSystem


def init_logging(level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s [%(name)-15s] %(message)s',
                        stream=sys.stdout
                        )


class PrinterActor(pykka.ThreadingActor):
    def __init__(self):
        super(PrinterActor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_start(self):
        self.logger.info('started')

    def on_receive(self, message):
        if command(message) is MISSING_FILE:
            self.logger.info('files missing: ', message['file'])


FE_PORT = 18000
BC_PORT = 18010
DEFAULT_INTERVAL = 3

LOCAL_DIR = "tmp"


def start_file_check():
    broadcaster = Announcer.start(FE_PORT, BC_PORT, DEFAULT_INTERVAL)

    printer = PrinterActor().start()
    file_diff = FilesDiff.start(printer)

    LocalFileSystem.start([broadcaster, file_diff], LOCAL_DIR, DEFAULT_INTERVAL)
    remote_files = RemoteFileSystem(file_diff, FE_PORT)


def main():
    init_logging()

    start_file_check()
    logging.info('FDIST started')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('FDIST stopping...')
        ActorRegistry.stop_all()
