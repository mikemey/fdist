import shutil
import tempfile

from pykka.registry import ActorRegistry

from fdist.exchange.file_exchange_server import FileExchangeServer
from fdist.messages import pip_request_message
from test.helpers import LogTestCase, free_port, send_request_to

TEST_PIP_SIZE = 3
PIP_1 = 'A' * TEST_PIP_SIZE
PIP_2 = 'B' * TEST_PIP_SIZE
PIP_3 = 'CC'


class PipServerTest(LogTestCase):
    def setUp(self):
        fe_port = free_port()
        self.address = ('localhost', fe_port)
        self.tmpdir = tempfile.mkdtemp()
        self.fe_port = fe_port

    def tearDown(self):
        ActorRegistry.stop_all()
        shutil.rmtree(self.tmpdir)

    def test_respond_with_first_pip(self):
        completed = [0, 1]
        self.assert_pip_response(completed, {0, 1}, {PIP_1, PIP_2})

    def test_respond_with_last_pip(self):
        completed = [2]
        self.assert_pip_response(completed, {2}, {PIP_3})

    def assert_pip_response(self, required_indices, expected_ixs, expected_datas):
        FileExchangeServer.start(self.fe_port, self.tmpdir, TEST_PIP_SIZE)
        file_id = '/pip.test'
        with open(self.tmpdir + file_id, "w") as f:
            f.write(PIP_1 + PIP_2 + PIP_3)

        pip_request = pip_request_message(file_id, required_indices)

        actual_pip_response = send_request_to(self.address, pip_request, 1024)
        actual_pip_ix = actual_pip_response['pip_ix']
        actual_pip_data = actual_pip_response['data']

        self.assertTrue(actual_pip_ix in expected_ixs,
                        "%s not in %s" % (actual_pip_ix, expected_ixs))
        self.assertTrue(actual_pip_data in expected_datas,
                        "%s not in %s" % (actual_pip_data, expected_datas))
