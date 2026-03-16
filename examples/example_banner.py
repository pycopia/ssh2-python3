from __future__ import print_function
import os
import socket

from ssh2.session import Session
from ssh2.utils import version

# Connection settings
host = 'localhost'
user = os.getlogin()

# Make socket, connect
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 22))

# Initialise
session = Session()
session.banner_set("SSH-2.0-Python3")
session.handshake(sock)

print(f"Remote Banner: {session.banner_get()}")

session.disconnect()
