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
FILLER_PIP = 'X' * TEST_PIP_LENGTH
PIP_1 = 'A' * TEST_PIP_LENGTH
PIP_2 = 'b' * TEST_PIP_LENGTH
PIP_3 = '3' * TEST_PIP_LENGTH

TEST_FILE_ID = '/test/lala.txt'
PIP_1_HASH = md5_hash(PIP_1)
PIP_2_HASH = md5_hash(PIP_2)
PIP_3_HASH = md5_hash(PIP_3)
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

    def assert_file_cache(self, expected_data):
        with open(self.full_file_path(), 'r') as f:
            self.quickEquals(f.read(), expected_data)

    def test_reserve_file_when_not_exists(self):
        print os.listdir(self.temp_dir)

        file_name = self.full_file_path()
        self.assertTrue(os.path.isfile(file_name))

        self.assert_file_cache(FILLER_PIP * 3)

    def test_keep_file_when_already_exists(self):
        self.file_store.stop()
        with open(self.full_file_path(), 'r+') as f:
            f.seek(0)
            f.write(PIP_1)

        self.file_store = FileStore.start(self.temp_dir, TEST_FILE_INFO)
        self.assert_file_cache(PIP_1 + FILLER_PIP * 2)

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

    def test_store_pip(self):
        self.file_store.ask(store_data_message(0, PIP_1))
        self.file_store.ask(store_data_message(2, PIP_3))
        self.assert_file_cache(PIP_1 + FILLER_PIP + PIP_3)

    def test_pip_ix_out_of_bounds(self):
        expected_message = 'IOError: Pip index out of bounds [3]'
        with raises(IOError) as io_error:
            self.file_store.ask(store_data_message(3, PIP_3))
        self.quickEquals(io_error.exconly(), expected_message)

    def test_truncate_last_pip(self):
        end_pip = "last"
        self.file_store.ask(store_data_message(0, PIP_1))
        self.file_store.ask(store_data_message(2, end_pip))
        self.file_store.ask(store_data_message(1, PIP_2))
        self.assert_file_cache(PIP_1 + PIP_2 + end_pip)
