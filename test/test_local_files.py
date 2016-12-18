import shutil
import tempfile
from time import sleep

from mock import MagicMock
from pykka.actor import ActorRef

from fdist.local_files import LocalFileSystem
from fdist.messages import local_files_message
from test.helpers import LogTestCase, AllItemsIn

TEST_RELOAD_LOCAL_FILES_SEC = 0.2
TEST_WAIT = TEST_RELOAD_LOCAL_FILES_SEC * 2


class TestLocalFileSystem(LogTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.first_receiver = MagicMock(spec=ActorRef)
        self.second_receiver = MagicMock(spec=ActorRef)
        self.lfs = LocalFileSystem.start([self.first_receiver, self.second_receiver],
                                         self.tmpdir, TEST_RELOAD_LOCAL_FILES_SEC)

    def tearDown(self):
        self.lfs.stop()
        shutil.rmtree(self.tmpdir)

    def addFile(self, filenames):
        for filename in filenames:
            with open(self.tmpdir + "/" + filename, "w") as f:
                f.write("FOOBAR")

    def test_add_one_file_in_folder(self):
        self.first_receiver.assert_not_called()
        self.second_receiver.assert_not_called()

        new_file = ['some_file_test1.txt']
        self.addFile(new_file)
        sleep(TEST_WAIT)

        self.first_receiver.tell.assert_called_once_with(local_files_message(new_file))
        self.second_receiver.tell.assert_called_once_with(local_files_message(new_file))

    def test_add_three_files_in_folder(self):
        new_files = ['some_file_test2.txt', 'some_file2_test2.txt', 'some_file3_test2.txt']
        self.addFile(new_files)

        sleep(TEST_WAIT)
        self.first_receiver.tell.assert_called_with(local_files_message(AllItemsIn(new_files)))
        self.second_receiver.tell.assert_called_with(local_files_message(AllItemsIn(new_files)))
