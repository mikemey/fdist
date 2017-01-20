import hashlib
import logging

LOG_LEVEL = logging.INFO
BROADCAST_PORT = 18010
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 18000
LOCAL_FILES_INTERVAL_SEC = 5

FILE_REQUEST_TIMEOUT = 2.0
SHARE_DIR = "tmp"
TMP_DIR = "tmp/.tmp"
RSYNC_PREFIX = "someone@somewhere:~"
RECEIVER_ONLY = False


def md5_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()
