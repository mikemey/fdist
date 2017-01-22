import json
import shutil
import socket
import tempfile

from pykka.registry import ActorRegistry

from fdist.exchange.file_exchange import FileExchangeServer
from fdist.globals import md5_hash
from fdist.messages import file_info_message, file_request_message
from fdist.messages import pip_request_message
from test.helpers import LogTestCase, free_port

TEST_PIP_SIZE = 3
PIP_1 = 'A' * TEST_PIP_SIZE
PIP_1_HASH = 'e1faffb3e614e6c2fba74296962386b7'
PIP_2 = 'B' * TEST_PIP_SIZE
PIP_2_HASH = '2bb225f0ba9a58930757a868ed57d9a3'
PIP_3 = 'CC'
PIP_3_HASH = 'aa53ca0b650dfd85c4f59fa156f7a2cc'


class PipServerTest(LogTestCase):
    def setUp(self):
        fe_port = free_port()
        self.address = ('localhost', fe_port)
        self.tmpdir = tempfile.mkdtemp()
        self.fe_port = fe_port

    def send_pip_request(self, request_message, buffer_size):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.address)
            sock.sendall(json.dumps(request_message))
            return sock.recv(buffer_size)
        finally:
            sock.close()

    def tearDown(self):
        ActorRegistry.stop_all()
        shutil.rmtree(self.tmpdir)

    def test_respond_with_pip(self):
        FileExchangeServer.start(self.fe_port, self.tmpdir, TEST_PIP_SIZE)
        file_id = '/file_info.test'
        with open(self.tmpdir + file_id, "w") as f:
            f.write(PIP_1 + PIP_2 + PIP_3)

        pip_request = pip_request_message(file_id, [False, False, False])
        pip_response = self.send_pip_request(pip_request, TEST_PIP_SIZE)

        self.quickEquals(pip_response, PIP_1)

    def test_large_file(self):
        mega = 1024 * 1024
        FileExchangeServer.start(self.fe_port, self.tmpdir, mega)

        file_id = '/large_file.test'
        one_meg = 'A' * mega
        counter = 700
        with open(self.tmpdir + file_id, "w") as f:
            while counter > 0:
                f.write(one_meg)
                counter -= 1

        one_meg_hash = md5_hash(one_meg)
        expected_info = file_info_message(file_id, mega, [one_meg_hash for i in range(0, 700)])

        actual_location = self.send_file_request(file_request_message(file_id))
        self.quickEquals(actual_location, expected_info)
