import subprocess

from mock.mock import MagicMock
from pykka.registry import ActorRegistry

from fdist.messages import file_location_message, SUCCESS_MESSAGE, FAILURE_MESSAGE
from fdist.rsync_wrapper import RsyncWrapper
from test.helpers import LogTestCase


def create_popen_mock(return_value):
    popen_mock = MagicMock(ref=subprocess.Popen)
    popen_mock.poll = MagicMock(return_value=return_value)
    subprocess.Popen = MagicMock(return_value=popen_mock)
    return popen_mock


class RsyncWrapperTest(LogTestCase):
    def setUp(self):
        self.rsync = RsyncWrapper.start()
        self.subprocess_popen = subprocess.Popen

    def tearDown(self):
        ActorRegistry.stop_all()
        subprocess.Popen = self.subprocess_popen

    def test_send_success_message(self):
        popen_mock = create_popen_mock(0)
        result = self.rsync.ask(file_location_message("file-id", "whatever"))

        self.quickEquals(result, SUCCESS_MESSAGE)
        popen_mock.poll.assert_called()

    def test_send_failure_message(self):
        popen_mock = create_popen_mock(1)
        result = self.rsync.ask(file_location_message("file-id", "whatever"))

        self.quickEquals(result, FAILURE_MESSAGE)
        popen_mock.poll.assert_called()
