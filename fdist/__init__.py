import logging
import sys
import time

from pykka.registry import ActorRegistry

from announcer import Announcer
from file_loader import ActorProvider
from file_master import FileMaster
from files_diff import FilesDiff
from local_files import LocalFiles
from remote_files import RemoteFiles


def init_logging(level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)5s [%(name)-12s] %(message)s',
                        stream=sys.stdout
                        )


FE_PORT = 18000
BC_PORT = 18010
DEFAULT_INTERVAL = 3

LOCAL_DIR = "tmp"


def main():
    init_logging()

    master = FileMaster(ActorProvider).start()
    file_diff = FilesDiff.start(master)

    broadcaster = Announcer.start(FE_PORT, BC_PORT, DEFAULT_INTERVAL)
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
