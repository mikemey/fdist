import os
import shutil
import tempfile
from time import sleep

from mock import MagicMock
from pykka.actor import ActorRef

from fdist.local_files import LocalFiles
from fdist.messages import local_files_message
from test.helpers import LogTestCase, AllItemsIn

TEST_RELOAD_LOCAL_FILES_SEC = 0.2
TEST_WAIT = TEST_RELOAD_LOCAL_FILES_SEC * 2


class LocalFilesTest(LogTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.receiver = MagicMock(spec=ActorRef)
        self.lfs = LocalFiles.start([self.receiver], self.tmpdir, TEST_RELOAD_LOCAL_FILES_SEC)

    def tearDown(self):
        self.lfs.stop()
        shutil.rmtree(self.tmpdir)

    def addFiles(self, filenames):
        for filename in filenames:
            with open(self.tmpdir + filename, "w") as f:
                f.write("FOOBAR")

    def test_add_files_in_folder(self):
        new_files = ['/some_file_test2.txt', '/some_file2_test2.txt', '/some_file3_test2.txt']
        self.addFiles(new_files)

        sleep(TEST_WAIT)
        self.receiver.tell.assert_called_with(local_files_message(AllItemsIn(new_files)))

    def test_call_all_receivers(self):
        first_receiver = MagicMock(spec=ActorRef)
        second_receiver = MagicMock(spec=ActorRef)
        self.lfs = LocalFiles.start([first_receiver, second_receiver],
                                    self.tmpdir, TEST_RELOAD_LOCAL_FILES_SEC)

        new_files = ['/some_file_test1.txt']
        self.addFiles(new_files)
        sleep(TEST_WAIT)

        first_receiver.tell.assert_called_once_with(local_files_message(new_files))
        second_receiver.tell.assert_called_once_with(local_files_message(new_files))

    def test_dont_report_hidden_files(self):
        new_file = ['/.some_file_test1.txt']
        self.addFiles(new_file)
        sleep(TEST_WAIT)

        self.receiver.tell.assert_not_called()

    def test_report_files_in_subdirectory(self):
        os.makedirs(self.tmpdir + "/sub_dir")
        new_files = ['/sub_dir/sub_file']
        self.addFiles(new_files)
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_once_with(local_files_message(new_files))

    def test_dont_report_empty_subdirectory(self):
        os.makedirs(self.tmpdir + "/empty_dir")
        sleep(TEST_WAIT)

        self.receiver.tell.assert_not_called()

    def test_dont_report_hidden_files_in_subdirectory(self):
        os.makedirs(self.tmpdir + "/sub_dir")
        self.addFiles(["/sub_dir/.hidden_file"])
        sleep(TEST_WAIT)

        self.receiver.tell.assert_not_called()
