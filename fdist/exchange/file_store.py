import os
from io import FileIO

from fdist.globals import md5_hash
from fdist.log_actor import LogActor
from fdist.messages import command, PIP_DATA, file_id_of


class FileStore(LogActor):
    def __init__(self, temp_dir, file_info_message):
        super(FileStore, self).__init__()

        self.temp_dir = temp_dir
        self.file_cache = self.temp_dir + "/" + md5_hash(file_id_of(file_info_message))
        self.file_info = file_info_message

    def pip_default_length(self):
        return int(self.file_info['pip_length'])

    def pip_count(self):
        return len(self.file_info['hashes'])

    def on_start(self):
        super(FileStore, self).on_start()
        if not os.path.isfile(self.file_cache):
            self.logger.debug('reserving cache file [%s]', self.file_cache)
            with FileIO(self.file_cache, 'w') as f:
                empty = bytes('X' * self.pip_default_length())
                for i in range(0, self.pip_count()):
                    f.write(empty)
            self.logger.debug('reserving cache file done.')
        else:
            self.logger.debug('keeping cache file [%s]', self.file_cache)

    def on_receive(self, message):
        if command(message) == PIP_DATA:
            pip_data = message['data']
            pips_ix = int(message['pip_ix'])
            self.logger.debug('new pip, length [%s]', len(pip_data))

            self.check_pip(pips_ix, pip_data)
            self.write_pip(pips_ix, pip_data)

    def check_pip(self, ix, data):
        if ix < 0 or ix >= self.pip_count():
            raise IOError('Pip index out of bounds [%s] range: 0 and %s' % (ix, self.pip_count()))

        data_len = len(data)
        if data_len != self.pip_default_length():
            is_last_pip = ix == (self.pip_count() - 1)
            pip_too_short = data_len < self.pip_default_length()
            if not (is_last_pip and pip_too_short):
                raise IOError('Pip length has to be [%s]: actual: [%s]' % (self.pip_default_length(), len(data)))

    def write_pip(self, ix, data):
        with FileIO(self.file_cache, 'r+') as f:
            offset = ix * self.pip_default_length()
            f.seek(offset)
            f.write(data)

            is_last_pip = ix == self.pip_count() - 1
            if is_last_pip:
                f.truncate()
