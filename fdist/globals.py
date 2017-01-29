import hashlib
import logging

LOG_LEVEL = logging.DEBUG
BROADCAST_PORT = 18010
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 18000
LOCAL_FILES_INTERVAL_SEC = 5

FILE_REQUEST_TIMEOUT = 2.0
SHARE_DIR = "tmp"
TMP_DIR = "tmp/.tmp"
RECEIVER_ONLY = False

PIP_SIZE = 1024 * 1024


def md5_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

    # expected 01a2e03126f4d04129bbdb5f61f418b2
    # 76939faef536d2313a0c831663a47cf1