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
    return logging.getLogger('main')


def main():
    logger = init_logging()
    logger.info("receive only: %s", RECEIVER_ONLY)

    master = FileMaster.start(FileLoaderProvider())
    file_diff = FilesDiff.start(master)

    local_file_receiver = [file_diff]
    if not RECEIVER_ONLY:
        FileInfo.start(FILE_EXCHANGE_PORT, RSYNC_PREFIX)
        file_announcer = Announcer.start(FILE_EXCHANGE_PORT, BROADCAST_PORT, BROADCAST_INTERVAL_SEC)
        local_file_receiver.append(file_announcer)

    LocalFiles.start(local_file_receiver, SHARE_DIR, LOCAL_FILES_INTERVAL_SEC)
    remote = RemoteFiles(file_diff, BROADCAST_PORT).start()

    logger.info('FDIST started')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('FDIST stopping...')
        remote.stop()
        ActorRegistry.stop_all()
