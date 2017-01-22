import json
import os
import shutil
import tempfile
from SocketServer import TCPServer, BaseRequestHandler
from time import sleep

from mock.mock import MagicMock
from pykka.actor import ActorRef
from pykka.registry import ActorRegistry

from fdist.exchange.file_loader import FileLoader
from fdist.globals import md5_hash
from fdist.messages import *
from test.helpers import LogTestCase, free_port
from test.mock_socket import MockServer

TEST_TIMEOUT = 0.5
TEST_WAIT = TEST_TIMEOUT * 2
TEST_FILE = '/file_load_test.test'
TEST_FILE_ID = '/dir/subdir' + TEST_FILE
TEST_INVALID_FILE_ID = '/invalid.test'

TEST_PIP_SIZE = 3
PIP_1 = 'A' * TEST_PIP_SIZE
PIP_1_HASH = 'e1faffb3e614e6c2fba74296962386b7'
PIP_2 = 'B' * TEST_PIP_SIZE
PIP_2_HASH = '2bb225f0ba9a58930757a868ed57d9a3'
PIP_3 = 'CC'
PIP_3_HASH = 'aa53ca0b650dfd85c4f59fa156f7a2cc'
PIP_FILLER = 'X' * TEST_PIP_SIZE

TEST_FILE_INFO_RESPONSE = file_info_message(TEST_FILE_ID, TEST_PIP_SIZE, [PIP_1_HASH, PIP_2_HASH, PIP_3_HASH])
TEST_PIP_RESPONSE = pip_message('1', PIP_2)

TEST_INVALID_FILE_INFO_RESPONSE = file_info_message(TEST_INVALID_FILE_ID, TEST_PIP_SIZE,
                                                    [PIP_1_HASH, PIP_2_HASH, PIP_3_HASH])
TEST_INVALID_PIP_RESPONSE = pip_message('0', PIP_2)

switcher = {
    'curr': 0,
    0: pip_message('1', PIP_2),
    1: pip_message('2', PIP_3),
    2: pip_message('0', PIP_1)
}


def next_message():
    ix = switcher['curr'] % 3
    msg = switcher.get(ix)
    switcher['curr'] += 1
    return msg


def decide_response(request):
    if command(request) == FILE_REQUEST:
        return TEST_FILE_INFO_RESPONSE
    if command(request) == PIP_REQUEST:
        if file_id_of(request) == TEST_FILE_ID:
            return next_message()
        else:
            return TEST_INVALID_PIP_RESPONSE


class FileRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        request = json.loads(data)
        self.server.data_records.append(request)

        response_message = decide_response(request)
        self.request.sendall(json.dumps(response_message))


class FileRequestServer(MockServer):
    server_type = TCPServer
    handler_type = FileRequestHandler


class FileLoaderTest(LogTestCase):
    def setUp(self):
        self.remote_fe_port = free_port()
        self.share_dir = tempfile.mkdtemp()
        self.tmp_dir = tempfile.mkdtemp()
        self.mocked_server = FileRequestServer(self.remote_fe_port)

        self.parent_actor = MagicMock(spec=ActorRef)

    def tearDown(self):
        self.mocked_server.stop()
        ActorRegistry.stop_all()
        shutil.rmtree(self.share_dir)
        shutil.rmtree(self.tmp_dir)

    def start_file_loader(self, test_id=TEST_FILE_ID):
        file_message = missing_file_message('localhost', self.remote_fe_port, test_id)
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

    def test_creates_file_store(self):
        self.start_file_loader(TEST_INVALID_FILE_ID)
        expected_store = self.tmp_dir + '/' + md5_hash(TEST_INVALID_FILE_ID)
        self.assertTrue(os.path.exists(expected_store))

    def test_store_all_pips(self):
        self.start_file_loader()
        sleep(TEST_WAIT)

        received = self.mocked_server.received_data()[1:]
        self.assertTrue(pip_request_message(TEST_FILE_ID, [0, 1, 2]) in received)
        self.assertTrue(pip_request_message(TEST_FILE_ID, [0, 2]) in received)
        self.assertTrue(pip_request_message(TEST_FILE_ID, [0]) in received)

        expected_file = self.share_dir + TEST_FILE_ID
        with open(expected_file, 'r') as f:
            self.quickEquals(f.read(), PIP_1 + PIP_2 + PIP_3)

    def test_reject_pip_with_wrong_hash(self):
        self.start_file_loader(TEST_INVALID_FILE_ID)
        sleep(TEST_WAIT)

        expected_store = self.tmp_dir + '/' + md5_hash(TEST_INVALID_FILE_ID)
        with open(expected_store, 'r') as f:
            self.quickEquals(f.read(), PIP_FILLER + PIP_FILLER + PIP_FILLER)
