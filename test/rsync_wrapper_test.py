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


TEST_TMP_FOLDER = '/whatever'


class RsyncWrapperTest(LogTestCase):
    def setUp(self):
        self.rsync = RsyncWrapper.start(TEST_TMP_FOLDER)
        self.subprocess_popen_bak = subprocess.Popen
        self.pull_file_bak = RsyncWrapper.pull_file

    def tearDown(self):
        ActorRegistry.stop_all()
        subprocess.Popen = self.subprocess_popen_bak
        RsyncWrapper.pull_file = self.pull_file_bak

    def test_send_success_message(self):
        popen_mock = create_popen_mock(0)
        result = self.rsync.ask(file_location_message('file-id', 'whatever'))

        self.quickEquals(result, SUCCESS_MESSAGE)
        popen_mock.poll.assert_called()

    def test_send_failure_message(self):
        popen_mock = create_popen_mock(1)
        result = self.rsync.ask(file_location_message('file-id', 'whatever'))

        self.quickEquals(result, FAILURE_MESSAGE)
        popen_mock.poll.assert_called()

    def test_rsync_command_escapes_source_parameter(self):
        RsyncWrapper.pull_file = MagicMock(return_value=0)
        file_id = '/bla bla/la di.da'
        self.rsync.ask(file_location_message(file_id, 'one@where:/share' + file_id))

        escaped_cmd = 'rsync -P --progress --perms --chmod=Du=rwx,Dgo=rx,Fa=rw "one@where:/share/bla\ bla/la\ di.da" ' + TEST_TMP_FOLDER
        RsyncWrapper.pull_file.assert_called_once_with(escaped_cmd, file_id)
