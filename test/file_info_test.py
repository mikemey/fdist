import json
import socket

from pykka.registry import ActorRegistry

from fdist.file_info import FileInfo
from fdist.messages import file_request_message, file_location_message
from helpers import LogTestCase, free_port

TEST_RSYNC_PREFIX = 'someone@somewhere:~/my/stuff'


class FileInfoTest(LogTestCase):
    def setUp(self):
        fe_port = free_port()
        self.address = ('localhost', fe_port)

        FileInfo.start(fe_port, TEST_RSYNC_PREFIX)

    def send_file_request(self, request_message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.address)
            sock.sendall(json.dumps(request_message))
            return json.loads(sock.recv(1024))
        finally:
            sock.close()

    def tearDown(self):
        ActorRegistry.stop_all()

    def test_respond_with_file_info(self):
        file_id = '/dir/subdir/file_info.test'
        rsync_path = TEST_RSYNC_PREFIX + file_id
        expected_location = file_location_message(file_id, rsync_path)

        actual_location = self.send_file_request(file_request_message(file_id))
        self.quickEquals(actual_location, expected_location)
