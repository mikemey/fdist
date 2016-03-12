import shutil
import tempfile
from time import sleep

from mock import MagicMock
from pykka.actor import ActorRef

from fdist.lfs import LocalFileSystem, FileUpdater
from test.logTestCase import LogTestCase
from test.mock_socket import MockTCPServer

TEST_RELOAD_LOCAL_FILES_SEC = 0.2
TEST_WAIT = TEST_RELOAD_LOCAL_FILES_SEC * 2


class TestLocalFileSystem(LogTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.receiver = MagicMock(spec=ActorRef)
        self.lfs = LocalFileSystem.start(self.receiver, self.tmpdir, TEST_RELOAD_LOCAL_FILES_SEC)

    def tearDown(self):
        self.lfs.stop()
        shutil.rmtree(self.tmpdir)

    def addFile(self, filename):
        with open(self.tmpdir + "/" + filename, "w") as f:
            f.write("FOOBAR")

    def test_add_one_file_in_folder(self):
        self.receiver.assert_not_called()

        new_file = 'some_file.txt'
        self.addFile(new_file)
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_once_with({'files': [new_file]})

    def test_add_three_files_in_folder(self):
        new_files = ['some_file.txt', 'some_file2.txt', 'some_file3.txt']
        for new_file in new_files:
            self.addFile(new_file)

        sleep(TEST_WAIT)
        self.receiver.tell.assert_called_with({'files': new_files})


class TestFileUpdater(LogTestCase):
    def setUp(self):
        self.fileUpdater = FileUpdater.start()
        self.remote_node = ('localhost', 15000)
        self.mockedSocket = MockTCPServer(self.remote_node)

    def tearDown(self):
        self.mockedSocket.stop()

    def test_update_node(self):
        new_file_message = {'files': ["lala.txt"]}
        self.fileUpdater.tell(new_file_message)
        self.fileUpdater.tell({'nodes': [self.remote_node]})

        sleep(TEST_WAIT)
        self.assertTrue(new_file_message in self.mockedSocket.received(), self.mockedSocket.received())
