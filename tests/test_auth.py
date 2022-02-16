r"""Test alternate authentication methods.

As done in the libssh2.

Only the following key types are supported by libssh2 at this time:

    - ecdsa-sha2-nistp256-cert-v01@openssh.com
    - ecdsa-sha2-nistp384-cert-v01@openssh.com
    - ecdsa-sha2-nistp521-cert-v01@openssh.com

Preferred key type:
    ecdsa-sha2-nistp384-cert-v01@openssh.com

Generate ca_ecdsa:
ssh-keygen -C CA -f embedded_server/ca -b 521 -t ecdsa

Generated the test keypair key_ecdsa, used with non-cert test, with:
ssh-keygen -t ecdsa -b 384 -f ./key_ecdsa -C ""

Generate keypair to be signed, use with cert test:
ssh-keygen -t ecdsa -b 384 -f ./signed_key_ecdsa -C ""

Sign the keypair with the CA key generated earlier:
ssh-keygen -s ./embedded_server/ca -I myidentity -n $USER -V "always:forever" -z 1 \
        ./signed_key_ecdsa.pub

NOTE: the above step must have the principle match the user logging in. The test suite will create
      the cert file.
"""

import os

from .base_test import SSH2TestCase, SSH2CertTestCase

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BasicPubkeyAuthTestCase(SSH2TestCase):

    def test_ec_auth(self):
        self.assertEqual(self.session.userauth_publickey_fromfile(
                         self.user, self.user_ec_key, passphrase="",
                         publickey=self.user_ec_pub_key), 0)


class FileCertAuthTestCase(SSH2CertTestCase):

    def _auth(self):
        return self.session.userauth_publickey_fromfile(self.user, self.user_key, passphrase="",
                                                        publickey=self.user_cert)

    def test_auth(self):
        self.assertEqual(self._auth(), 0)


class MemoryCertAuthTestCase(SSH2CertTestCase):

    def _auth(self):
        with open(self.user_key, "rb") as fo:
            privatekeyfiledata = fo.read()

        with open(self.user_cert, "rb") as fo:
            publickeyfiledata = fo.read()

        return self.session.userauth_publickey_frommemory(
            self.user, privatekeyfiledata, passphrase='', publickeyfiledata=publickeyfiledata)

    def test_auth(self):
        self.assertEqual(self._auth(), 0)
