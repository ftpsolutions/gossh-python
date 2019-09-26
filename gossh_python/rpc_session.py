from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *
from builtins import object, str
from sys import version as python_version
from sys import version_info
from threading import RLock

from future import standard_library

from .common import handle_exception

standard_library.install_aliases()


is_pypy = 'pypy' in python_version.lower()
version = version_info[:3]

# needed for CFFI under Python2
if version < (3, 0, 0):
    from past.types.oldstr import oldstr as str

if not is_pypy and version < (3, 0, 0):  # for Python2
    from .py2.gossh_python_go import SetPyPy, NewRPCSession, RPCConnect, RPCGetShell, RPCRead, RPCWrite, RPCClose
else:
    raise ValueError('PyPy and Python3 is not supported. Waiting for gopy CFFI support')
#     from .cffi.gossh_python import SetPyPy, NewRPCSession, RPCConnect, RPCGetShell, RPCRead, RPCWrite, RPCClose
#
#     SetPyPy()
#
#     print('WARNING: PyPy or Python3 detected, will use CFFI- be prepared for very odd behaviour')


_new_session_lock = RLock()


def _new_session(*args):
    with _new_session_lock:
        return handle_exception(
            NewRPCSession, args
        )


class RPCSession(object):
    def __init__(self, session_id, **kwargs):
        self._session_id = session_id
        self._kwargs = kwargs

    def __del__(self):
        try:
            self.close()
        except BaseException:
            pass

    def __repr__(self):
        return '{0}(session_id={1}, {2})'.format(
            self.__class__.__name__,
            repr(self._session_id),
            ', '.join('{0}={1}'.format(k, repr(v)) for k, v in list(self._kwargs.items()))
        )

    def connect(self):
        return handle_exception(
            RPCConnect, (self._session_id,), self
        )

    def get_shell(self, terminal=None, height=65536, width=65536):
        terminal = terminal if terminal is not None else 'dumb'

        return handle_exception(RPCGetShell, (self._session_id, terminal, height, width), self)

    def read(self, size=1024):
        return handle_exception(RPCRead, (self._session_id, size), self)

    def write(self, data):
        data = str(data)

        return handle_exception(RPCWrite, (self._session_id, data), self)

    def close(self):
        return handle_exception(RPCClose, (self._session_id, ), self)


def create_session(hostname, username, password, port=22, timeout=5):
    session_id = _new_session(
        str(hostname),
        str(username),
        str(password),
        int(port),
        int(timeout),
    )

    kwargs = {
        'hostname': hostname,
        'username': username,
        'password': password,
        'port': port,
        'timeout': timeout,
    }

    return RPCSession(
        session_id=session_id,
        **kwargs
    )
