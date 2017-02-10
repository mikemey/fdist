import hashlib
import logging
import os

LOG_LEVEL = logging.INFO
BROADCAST_PORT = 18010
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 18000
LOCAL_FILES_INTERVAL_SEC = 5

FILE_REQUEST_TIMEOUT = 2.0
SHARE_DIR = "tmp"
RECEIVER_ONLY = False

PIP_SIZE = 1024 * 1024


def hashed_file_path(share_dir, file_id):
    dir_part = os.path.dirname(share_dir + file_id)
    file_part = os.path.basename(file_id)
    return dir_part + '/.' + file_part + '.' + md5_hash(file_id, 6)


def md5_hash(data, max_length=-1):
    m = hashlib.md5()
    m.update(data)
    md5 = m.hexdigest()
    if max_length > 0:
        return md5[0:max_length]
    return md5
