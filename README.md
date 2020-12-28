ssh2-python3
============

Super fast SSH2 protocol library.
This `ssh2-python3` package provides Python bindings for [libssh2][libssh2].

[![License](https://img.shields.io/badge/License-LGPL%20v2-blue.svg)](https://pypi.python.org/pypi/ssh2-python3)

This is a forked and modified version of the original, *ssh2-python*.

Notable changes:

- Supports Python 3 only.
- Uses exclusively the embedded libssh2 (also modified to support Unix tunnel targets).
- Compiles libbsh2 to use Python's memory allocator.
- Some new methods that support:
  - Unix domain socket tunnel target on server host.
  - The "signal" protocol message.
  - Generic message constructor.
  - Bug fixes. Notably, a segfault during garbage collection in certain situations.

Any new bugs are the result of myself and not the orignal author (Panos Kittenis).
Many thanks for his fine work to get this started.

Installation
------------

Binary wheel packages are provided for Linux, all recent Python versions. Wheel packages have **no
dependencies**.

You may need to update `pip` to install recent binary wheel packages - `pip install -U pip`.

```console
pip install ssh2-python3
```

API Feature Set
---------------

At this time all of the `libssh2` API has been implemented up to version `1.9.1-embedded`.

In addition, as `ssh2-python3` is a thin wrapper of `libssh2` with Python 3 semantics,
its [code examples](https://libssh2.org/examples/) can be ported straight over to Python with only minimal
changes.

Library Features
----------------

The library uses [Cython][Cython] based native code extensions as wrappers for `libssh2`.

Extension features:

- Thread safe - GIL is released as much as possible
- Very low overhead
- Super fast as a consequence of the excellent C library it uses and prodigious use of native code
- Object oriented - memory freed automatically and safely as objects are garbage collected by
  Python, and uses Python's memory allocator.
- Use Python semantics where applicable, such as context manager and iterator support for
  opening and reading from SFTP file handles
- Raise errors as Python exceptions
- Provide access to `libssh2` error code definitions

Quick Start
-----------

Both byte and unicode strings are accepted as arguments and encoded appropriately. To change default
encoding, `utf-8`, change the value of `ssh2.utils.ENCODING`. Output is always in byte strings.

Contributions are most welcome!

Authentication Methods
----------------------

Connect and get available authentication methods.

```python
from ssh2.session import Session

sock = <create and connect socket>

session = Session()
session.handshake(sock)
print(session.userauth_list())
```

Output will vary depending on SSH server configuration. For example:

```python
['publickey', 'password', 'keyboard-interactive']
```

Agent Authentication
--------------------

```python
session.agent_auth(user)
```

Command Execution
------------------------

```python
channel = session.open_session()
channel.execute('echo Hello')
```

Reading Output
---------------

```python
   size, data = channel.read()
   while(size > 0):
       print(data)
       size, data = channel.read()
```

```console
Hello
```

Exit Code
--------------

```python
print("Exit status: %s" % (channel.get_exit_status()))
```

```python
   Exit status: 0
```

Public Key Authentication
-------------------------

```python
session.userauth_publickey_fromfile(username, 'private_key_file')
```

Passphrase can be provided with the `passphrase` keyword param.

Password Authentication
----------------------------

```python
   session.userauth_password(username, '<my password>')
```

SFTP Read
-----------

```python
from ssh2.sftp import LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR

sftp = session.sftp_init()
with sftp.open(<remote file to read>,
      LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR) as remote_fh, \
       open(<local file to write>, 'wb') as local_fh:
   for size, data in remote_fh:
       local_fh.write(data)
```

Complete Example
----------------

A simple usage example looks very similar to
`libssh2` [usage examples](https://www.libssh2.org/examples/).

As mentioned, `ssh2-python3` is intentionally a thin wrapper over `libssh2` and directly maps most
of its API.

Clients using this library can be much simpler to use than interfacing with the `libssh2` API
directly.

```python
import os
import socket

from ssh2.session import Session

host = 'localhost'
user = os.getlogin()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 22))

session = Session()
session.handshake(sock)
session.agent_auth(user)

channel = session.open_session()
channel.execute('echo me; exit 2')
size, data = channel.read()
while size > 0:
   print(data)
   size, data = channel.read()
channel.close()
print("Exit status: %s" % channel.get_exit_status())
```

Output:

```console
me

Exit status: 2
```

SSH Functionality currently implemented
---------------------------------------

- SSH channel operations (exec,shell,subsystem) and methods
- SSH agent functionality
- Public key authentication and management
- SFTP operations
- SFTP file handles and attributes
- SSH port forwarding and tunnelling, for both TCP and Unix sockets.
- Non-blocking mode
- SCP send and receive
- Listener for port forwarding
- Subsystem support
- Host key checking and manipulation
- Signal remote process.

And more, as per [libssh2][libssh2] functionality.

[Cython]: https://www.cython.org
[libssh2]: https://www.libssh2.org
