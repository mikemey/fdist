import shutil
import tempfile
from time import sleep

from mock import MagicMock
from mocket.mocket import mocketize, Mocket, MocketEntry
from pykka.actor import ActorRef

from fdist.lfs import LocalFileSystem, FileUpdater
from test.logTestCase import LogTestCase

TEST_RELOAD_LOCAL_FILES_SEC = 0.2


class TestLocalFileSystem(LogTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.receiver = MagicMock(spec=ActorRef)
        LocalFileSystem.start(self.receiver, self.tmpdir, TEST_RELOAD_LOCAL_FILES_SEC)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def addFile(self, filename):
        with open(self.tmpdir + "/" + filename, "w") as f:
            f.write("FOOBAR")

    def test_add_one_file_in_folder(self):
        self.receiver.assert_not_called()

        new_file = 'some_file.txt'
        self.addFile(new_file)
        sleep(TEST_RELOAD_LOCAL_FILES_SEC * 2)

        self.receiver.tell.assert_called_once_with({'files': [new_file]})

    def test_add_three_files_in_folder(self):
        new_files = ['some_file.txt', 'some_file2.txt', 'some_file3.txt']
        for new_file in new_files:
            self.addFile(new_file)

        sleep(TEST_RELOAD_LOCAL_FILES_SEC * 2)
        self.receiver.tell.assert_called_with({'files': new_files})


class TestFileUpdater(LogTestCase):
    def setUp(self):
        self.fileUpdater = FileUpdater.start()

    @mocketize
    def test_update_node(self):
        host = 'localhost'
        port = 15000

        Mocket.register(MocketEntry('{}:{}'.format(host, port), 'received some'))

        self.fileUpdater.tell({'nodes': [(host, port)]})

        sleep(0.3)
        print "received:", Mocket._requests
        #
        # self.fileUpdate.tell({'nodes': ['']})
        #
        # new_files = ['some_file.txt', 'some_file2.txt', 'some_file3.txt']
        # for new_file in new_files:
        #     self.addFile(new_file)
        #
        # sleep(TEST_RELOAD_LOCAL_FILES_SEC * 2)
        # self.receiver.tell.assert_called_with({'files': new_files})
