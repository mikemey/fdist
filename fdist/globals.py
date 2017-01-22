import hashlib
import logging

LOG_LEVEL = logging.DEBUG
BROADCAST_PORT = 18010
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 18000
LOCAL_FILES_INTERVAL_SEC = 5

FILE_REQUEST_TIMEOUT = 2.0
SHARE_DIR = "/Users/michael/Movies"
TMP_DIR = "/Users/michael/Movies/.tmp"
RSYNC_PREFIX = "michael@haumea:~/Movies"
RECEIVER_ONLY = True


def md5_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()
