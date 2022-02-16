# python3

import unittest
import os
import socket
import getpass

from .embedded_server.openssh import OpenSSHServer
from ssh2.session import Session


BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class SSH2TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = getpass.getuser()
        cls.user_key = os.path.join(BASE_PATH, 'unit_test_key')
        cls.user_ec_key = os.path.join(BASE_PATH, 'key_ecdsa')
        os.chmod(cls.user_key, 0o600)
        os.chmod(cls.user_ec_key, 0o600)
        cls.user_pub_key = f"{cls.user_key}.pub"
        cls.user_ec_pub_key = f"{cls.user_ec_key}.pub"
        cls.server = OpenSSHServer()
        cls.server.start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        del cls.server

    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 2222
        self.cmd = 'echo me'
        self.resp = 'me'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.sock = sock
        self.session = Session()
        self.session.handshake(self.sock)

    def tearDown(self):
        del self.session
        self.sock.close()
        del self.sock

    def _auth(self):
        return self.session.userauth_publickey_fromfile(self.user, self.user_key)


class SSH2CertTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = getpass.getuser()
        cls.user_key = os.path.join(BASE_PATH, 'signed_key_ecdsa')
        cls.user_pub_key = f"{cls.user_key}.pub"
        cls.user_cert = f"{cls.user_key}-cert.pub"
        cls.server = OpenSSHServer()
        cls.server.sign_key(cls.user)
        cls.server.start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        del cls.server

    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 2222
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.sock = sock
        self.session = Session()
        self.session.handshake(self.sock)

    def tearDown(self):
        del self.session
        self.sock.close()
        del self.sock
