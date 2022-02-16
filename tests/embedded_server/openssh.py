# This file is part of ssh2-python.
# Copyright (C) 2017 Panos Kittenis

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, version 2.1.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import os
import socket
import subprocess
from time import sleep

DIR_NAME = os.path.dirname(__file__)
PDIR_NAME = os.path.dirname(DIR_NAME)
PPDIR_NAME = os.path.dirname(PDIR_NAME)


class OpenSSHServer(object):

    def __init__(self, port=2222):
        self.port = port
        self.server_proc = None
        self.server_key = os.path.join(DIR_NAME, "rsa_host_key")
        self.sshd_config = os.path.join(DIR_NAME, "sshd_config")
        self.authorized_keys = os.path.join(DIR_NAME, "authorized_keys")
        self.ca_key = os.path.join(DIR_NAME, "ca.pub")
        self._fix_permissions()
        self.cmdline = ['/usr/sbin/sshd', '-D', '-q', '-p', str(port),
                        '-o', f'AuthorizedKeysFile={self.authorized_keys}',
                        '-o', f'TrustedUserCAKeys={self.ca_key}',
                        '-h', str(self.server_key), '-f', str(self.sshd_config)]

    def _fix_permissions(self):
        os.chmod(self.server_key, 0o600)
        for _dir in [DIR_NAME, PDIR_NAME, PPDIR_NAME]:
            os.chmod(_dir, 0o755)

    def start_server(self):
        # print("Running:", " ".join(self.cmdline), file=sys.stderr)
        server = subprocess.Popen(self.cmdline, shell=False, stdout=subprocess.DEVNULL)
        self.server_proc = server
        self._wait_for_port()

    def _wait_for_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sleep(.1)
        while sock.connect_ex(('127.0.0.1', self.port)) != 0:
            sleep(.1)
        sock.close()

    def sign_key(cls, user):
        cmd = ['ssh-keygen', '-s', f'{DIR_NAME}/ca', '-I', 'myidentity',
               '-n', user, '-V', 'always:forever', '-z', '1', f'{PDIR_NAME}/signed_key_ecdsa.pub']
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self):
        if self.server_proc is not None and self.server_proc.returncode is None:
            self.server_proc.terminate()
            return self.server_proc.wait()

    def __del__(self):
        self.stop()
