import hashlib
import os
from io import FileIO

from log_actor import LogActor
from messages import command, STORE_DATA


def md5_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


class FileStore(LogActor):
    def __init__(self, temp_dir, file_info_message):
        super(FileStore, self).__init__()

        self.temp_dir = temp_dir
        self.file_cache = self.temp_dir + "/" + md5_hash(file_info_message['file_id'])
        self.file_info = file_info_message

    def pip_length(self):
        return self.file_info['pip_length']

    def pip_count(self):
        return len(self.file_info['hashes'])

    def on_start(self):
        super(FileStore, self).on_start()
        if not os.path.isfile(self.file_cache):
            self.logger.debug('reserving cache file [%s]', self.file_cache)
            with FileIO(self.file_cache, 'w') as f:
                empty = bytes('X' * self.pip_length())
                for i in range(0, self.pip_count()):
                    f.write(empty)
            self.logger.debug('reserving cache file done.')
        else:
            self.logger.debug('keeping cache file [%s]', self.file_cache)

    def on_receive(self, message):
        if command(message) == STORE_DATA:
            pip_data = message['data']
            self.logger.debug('new pip, length [%s]', len(pip_data))
            if len(pip_data) != self.pip_length():
                raise IOError('Pip length has to be [%s]: actual: [%s]' % (self.pip_length(), len(pip_data)))
            else:
                self.logger.debug('no error')
