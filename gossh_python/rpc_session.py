from sys import version as python_version
from threading import RLock

from common import handle_exception

if 'pypy' not in python_version.strip().lower():
    from py2.gossh_python import SetPyPy, NewRPCSession, RPCConnect, RPCGetShell, RPCRead, RPCWrite, RPCClose
else:
    from cffi.gossh_python import SetPyPy, NewRPCSession, RPCConnect, RPCGetShell, RPCRead, RPCWrite, RPCClose

    SetPyPy()

    print 'WARNING: PyPy detected- be prepared for very odd behaviour'


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
            ', '.join('{0}={1}'.format(k, repr(v)) for k, v in self._kwargs.iteritems())
        )

    def connect(self):
        return handle_exception(
            RPCConnect, (self._session_id,)
        )

    def get_shell(self):
        return handle_exception(RPCGetShell, (self._session_id,))

    def read(self, size=1024):
        return handle_exception(RPCRead, (self._session_id, size,))

    def write(self, data):
        return handle_exception(RPCWrite, (self._session_id, data,))

    def close(self):
        return handle_exception(
            RPCClose, (self._session_id,),
        )


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
