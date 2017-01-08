import logging
import re
import subprocess
import time
from _socket import error
from string import join

import pykka

from messages import command, FILE_LOCATION, SUCCESS_MESSAGE, FAILURE_MESSAGE

rsync_params = ['rsync', '-P', '--progress', '--perms', '--chmod=Du=rwx,Dgo=rx,Fa=rw']


class RsyncWrapper(pykka.ThreadingActor):
    def __init__(self, temp_dir):
        super(RsyncWrapper, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.temp_dir = temp_dir

    def full_params(self, file_location):
        return join(rsync_params + [file_location, self.temp_dir])

    def on_receive(self, message):
        if command(message) == FILE_LOCATION:
            rsync_path = message['rsync_path']
            file_id = message['file_id']
            cmd = self.full_params(rsync_path)
            result = self.pull_file(cmd, file_id)
            return SUCCESS_MESSAGE if result == 0 else FAILURE_MESSAGE

    def pull_file(self, cmd, file_id):
        try:
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            buf = []
            latest_timestamp = 0

            while True:
                if proc.poll() is not None:
                    return proc.poll()

                output = proc.stdout.read(1)
                if output in {'\r', '\n'}:
                    current_time = time.time()
                    if current_time - latest_timestamp > 3:
                        line = join(buf, '')
                        latest_timestamp = current_time

                        matches = re.match(r'\s*(\d+)\s+(\d+)%\s+([^M]+)MB/s\s+(.*)', line)
                        if matches:
                            self.logger.info('%3s%% %6sMB/s %s', matches.group(2), matches.group(3), file_id)
                    buf = []
                else:
                    buf.append(output)
        except error as _error:
            self.logger.error("failed: %s", _error)
