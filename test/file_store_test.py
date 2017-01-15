import os
import shutil
import tempfile
from time import sleep

from pykka.registry import ActorRegistry
from pytest import raises

from fdist.file_store import FileStore
from fdist.file_store import md5_hash
from fdist.messages import file_info_message, store_data_message
from helpers import LogTestCase

TEST_PIP_LENGTH = 8


def pip_hash(char):
    return md5_hash(char * TEST_PIP_LENGTH)


TEST_FILE_ID = '/test/lala.txt'
PIP_1_HASH = pip_hash('A')
PIP_2_HASH = pip_hash('b')
PIP_3_HASH = pip_hash('3')
TEST_FILE_INFO = file_info_message(TEST_FILE_ID, TEST_PIP_LENGTH, [PIP_1_HASH, PIP_2_HASH, PIP_3_HASH])


class FileStoreTest(LogTestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_store = FileStore.start(self.temp_dir, TEST_FILE_INFO)
        sleep(0.3)

    def tearDown(self):
        ActorRegistry.stop_all()
        shutil.rmtree(self.temp_dir)

    def full_file_path(self): return self.temp_dir + "/" + md5_hash(TEST_FILE_ID)

    def test_reserve_file_when_not_exists(self):
        print os.listdir(self.temp_dir)

        file_name = self.full_file_path()
        self.assertTrue(os.path.isfile(file_name))

        with open(file_name, 'r') as f:
            for char in f.read():
                self.quickEquals(char, 'X')

    def test_keep_file_when_already_exists(self):
        self.file_store.stop()
        example_pip = 'A' * TEST_PIP_LENGTH
        file_name = self.full_file_path()
        with open(file_name, 'w') as f:
            f.write(example_pip)

        self.file_store = FileStore.start(self.temp_dir, TEST_FILE_INFO)
        sleep(0.1)
        with open(file_name, 'r') as f:
            stored_pip = f.read(TEST_PIP_LENGTH)
            self.quickEquals(stored_pip, example_pip)

    def test_pip_length_too_long(self):
        too_long = 'pip_too_long'
        expected_message = 'IOError: Pip length has to be [%s]: actual: [%s]' % (TEST_PIP_LENGTH, len(too_long))
        with raises(IOError) as io_error:
            self.file_store.ask(store_data_message(0, too_long))

        self.quickEquals(io_error.exconly(), expected_message)

    def test_pip_length_too_short(self):
        too_short = 'pip_'
        expected_message = 'IOError: Pip length has to be [%s]: actual: [%s]' % (TEST_PIP_LENGTH, len(too_short))
        with raises(IOError) as io_error:
            self.file_store.ask(store_data_message(0, too_short))

        self.quickEquals(io_error.exconly(), expected_message)
