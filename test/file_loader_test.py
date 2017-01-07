import json
import os
import shutil
import tempfile
from SocketServer import TCPServer, BaseRequestHandler
from time import sleep

from mock.mock import MagicMock
from pykka.actor import ActorRef
from pykka.registry import ActorRegistry

from fdist.file_loader import FileLoader
from fdist.messages import *
from fdist.rsync_wrapper import RsyncWrapper
from helpers import free_port
from mock_socket import MockServer
from test.helpers import LogTestCase

TEST_TIMEOUT = 0.5
TEST_WAIT = TEST_TIMEOUT * 2
TEST_FILE = '/file_load_test.txt'
TEST_FILE_ID = '/dir/subdir' + TEST_FILE

TEST_FILE_LOCATION_MESSAGE = file_location_message(TEST_FILE_ID, 'someone@somewhere:~/dir/file_load_test.txt')


class FileRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.data_records.append(json.loads(data))
        self.request.sendall(json.dumps(TEST_FILE_LOCATION_MESSAGE))


class FileRequestServer(MockServer):
    server_type = TCPServer
    handler_type = FileRequestHandler


def setup_rsync_response_with(ret_val):
    rsync_mock = MagicMock(ref=ActorRef)
    rsync_mock.ask = MagicMock(return_value=ret_val)
    RsyncWrapper.start = MagicMock(return_value=rsync_mock)
    return rsync_mock


class FileLoaderTest(LogTestCase):
    def setUp(self):
        self.remote_fe_port = free_port()
        self.share_dir = tempfile.mkdtemp()
        self.tmp_dir = tempfile.mkdtemp()
        self.mocked_server = FileRequestServer(self.remote_fe_port)

        self.parent_actor = MagicMock(ref=ActorRef)
        self.rsync_start_bak = RsyncWrapper.start

    def tearDown(self):
        RsyncWrapper.start = self.rsync_start_bak
        self.mocked_server.stop()
        ActorRegistry.stop_all()
        shutil.rmtree(self.share_dir)
        shutil.rmtree(self.tmp_dir)

    def start_file_loader(self):
        file_message = missing_file_message('localhost', self.remote_fe_port, TEST_FILE_ID)
        FileLoader.start(self.share_dir, self.tmp_dir, file_message, self.parent_actor, TEST_TIMEOUT)
        sleep(TEST_WAIT)

    def test_receive_file_request(self):
        self.start_file_loader()

        received = self.mocked_server.received_data()[0]
        expected = file_request_message(TEST_FILE_ID)
        self.quickEquals(received, expected)

    def test_send_incomplete_message_on_failure(self):
        self.mocked_server.stop()
        self.start_file_loader()

        self.parent_actor.tell.assert_called_once_with(load_failed_message(TEST_FILE_ID))

    def test_start_and_stop_rsync(self):
        rsync_mock = setup_rsync_response_with(SUCCESS_MESSAGE)
        self.start_file_loader()

        rsync_mock.ask.assert_called_once_with(TEST_FILE_LOCATION_MESSAGE)
        rsync_mock.stop.assert_called_once()

    def test_send_incomplete_message_on_rsync_failure(self):
        setup_rsync_response_with(FAILURE_MESSAGE)
        self.start_file_loader()

        self.parent_actor.tell.assert_called_once_with(load_failed_message(TEST_FILE_ID))

    def test_move_completed_file_to_destination(self):
        with open(self.tmp_dir + TEST_FILE, "w") as f:
            f.write("FOOBAR")

        setup_rsync_response_with(SUCCESS_MESSAGE)
        self.start_file_loader()

        self.assertTrue(os.path.exists(self.share_dir + TEST_FILE_ID))
