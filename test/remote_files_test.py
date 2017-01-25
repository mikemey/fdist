import json
import socket
from time import sleep

from mock import MagicMock
from pykka import ActorRef
from scapy import sendrecv
from scapy.layers.inet import IP, UDP

from fdist.messages import broadcast_message, remote_files_message
from fdist.remote_files import RemoteFiles
from helpers import free_port
from test.helpers import LogTestCase

TEST_WAIT = 0.5

TEST_IP = "192.168.254.254"
TEST_PORT = 12121
TEST_FILES = ["/file_a.txt", "/file_b.txt"]


class RemoteFilesTest(LogTestCase):
    def setUp(self):
        self.broadcast_port = free_port()

        self.receiver = MagicMock(spec=ActorRef)
        self.remote_files = RemoteFiles(self.receiver, self.broadcast_port).start()

    def tearDown(self):
        self.remote_files.stop()

    def send_broadcast_message(self, message, src_ip=TEST_IP):
        payload = json.dumps(message)
        udp_packet = IP(src=src_ip) / UDP(dport=self.broadcast_port) / payload
        sendrecv.send(udp_packet)

    def test_forwards_new_node(self):
        self.send_broadcast_message(broadcast_message(TEST_PORT, TEST_FILES))
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_with(remote_files_message(TEST_IP, TEST_PORT, TEST_FILES))

    def test_doesnt_report_own_node(self):
        own_ip = socket.gethostbyname(socket.gethostname())
        self.send_broadcast_message(broadcast_message(TEST_PORT, TEST_FILES), own_ip)
        sleep(TEST_WAIT)

        self.receiver.tell.assert_not_called()

    def test_forwards_two_new_nodes(self):
        test_port_2 = 32323
        test_files_2 = ["/2_file_a.txt", "/2_file_b.txt"]

        self.send_broadcast_message(broadcast_message(TEST_PORT, TEST_FILES))
        self.send_broadcast_message(broadcast_message(test_port_2, test_files_2))
        sleep(TEST_WAIT)

        self.receiver.tell.assert_any_call(remote_files_message(TEST_IP, TEST_PORT, TEST_FILES))
        self.receiver.tell.assert_any_call(remote_files_message(TEST_IP, test_port_2, test_files_2))

    def test_no_reaction_on_unknown_message(self):
        payload = 'bla bla bla'
        udp_packet = IP(src=TEST_IP) / UDP(dport=self.broadcast_port) / payload
        sendrecv.send(udp_packet)

        sleep(TEST_WAIT)
        self.receiver.tell.assert_not_called()

        self.send_broadcast_message(broadcast_message(TEST_PORT, TEST_FILES))
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_with(remote_files_message(TEST_IP, TEST_PORT, TEST_FILES))
