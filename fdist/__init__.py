import logging
import sys
import time

import pykka
from pykka.registry import ActorRegistry

from announcer import Announcer
from files_diff import FilesDiff
from local_files import LocalFiles
from messages import command, MISSING_FILE
from remote_files import RemoteFiles


def init_logging(level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)5s [%(name)-12s] %(message)s',
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
            self.logger.info('files missing: %s', message['file'])


FE_PORT = 18000
BC_PORT = 18010
DEFAULT_INTERVAL = 3

LOCAL_DIR = "tmp"


def main():
    init_logging()

    broadcaster = Announcer.start(FE_PORT, BC_PORT, DEFAULT_INTERVAL)

    printer = PrinterActor().start()
    file_diff = FilesDiff.start(printer)

    LocalFiles.start([broadcaster, file_diff], LOCAL_DIR, DEFAULT_INTERVAL)
    remote = RemoteFiles(file_diff, BC_PORT).start()

    logging.info('FDIST started')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('FDIST stopping...')
        remote.stop()
        ActorRegistry.stop_all()
