import sys
import time

from pykka.registry import ActorRegistry

from announcer import Announcer
from file_info import FileInfo
from file_loader import FileLoaderProvider
from file_master import FileMaster
from files_diff import FilesDiff
from globals import *
from local_files import LocalFiles
from remote_files import RemoteFiles


def init_logging(level=LOG_LEVEL):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)5s [%(name)-12s] %(message)s',
                        stream=sys.stdout
                        )


def main():
    init_logging()

    FileInfo.start(FILE_EXCHANGE_PORT, RSYNC_PREFIX)
    master = FileMaster.start(FileLoaderProvider())
    file_diff = FilesDiff.start(master)

    broadcaster = Announcer.start(FILE_EXCHANGE_PORT, BROADCAST_PORT, BROADCAST_INTERVAL_SEC)
    LocalFiles.start([broadcaster, file_diff], SHARE_DIR, LOCAL_FILES_INTERVAL_SEC)
    remote = RemoteFiles(file_diff, BROADCAST_PORT).start()

    logging.info('FDIST started')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('FDIST stopping...')
        remote.stop()
        ActorRegistry.stop_all()
