from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import gc
import unittest
from builtins import *

from hamcrest import assert_that, equal_to, greater_than_or_equal_to
from mock import call, patch

from future import standard_library

from .rpc_session import RPCSession, create_session

standard_library.install_aliases()


class SessionTest(unittest.TestCase):
    def setUp(self):
        self._subject = RPCSession(
            session_id=0,
        )

    @patch('gossh_python.rpc_session.RPCConnect')
    def test_connect(self, rpc_call):
        rpc_call.return_value = None

        assert_that(
            self._subject.connect(),
            equal_to(None)
        )

        assert_that(
            rpc_call.mock_calls,
            equal_to([
                call(0)
            ])
        )

    @patch('gossh_python.rpc_session.RPCGetShell')
    def test_get_shell(self, rpc_call):
        rpc_call.return_value = None

        assert_that(
            self._subject.get_shell(),
            equal_to(None)
        )

        assert_that(
            rpc_call.mock_calls,
            equal_to([
                call(0, 'dumb', 65536, 65536)
            ])
        )

    @patch('gossh_python.rpc_session.RPCRead')
    def test_read(self, rpc_call):
        rpc_call.return_value = 'some data'

        assert_that(
            self._subject.read(1024),
            equal_to('some data')
        )

        assert_that(
            rpc_call.mock_calls,
            equal_to([
                call(0, 1024)
            ])
        )

    @patch('gossh_python.rpc_session.RPCWrite')
    def test_write(self, rpc_call):
        rpc_call.return_value = None

        assert_that(
            self._subject.write('some data'),
            equal_to(None)
        )

        assert_that(
            rpc_call.mock_calls,
            equal_to([
                call(0, 'some data')
            ])
        )

    @patch('gossh_python.rpc_session.RPCClose')
    def test_close(self, rpc_call):
        rpc_call.return_value = None

        assert_that(
            self._subject.close(),
            equal_to(None)
        )

        assert_that(
            rpc_call.mock_calls,
            equal_to([
                call(0)
            ])
        )

    @patch('gossh_python.rpc_session.RPCClose')
    def test_del(self, rpc_call):
        rpc_call.return_value = None

        del(self._subject)

        gc.collect()

        assert_that(
            len(rpc_call.mock_calls),
            greater_than_or_equal_to(1)
        )


class ConstructorsTest(unittest.TestCase):
    @patch('gossh_python.rpc_session.RPCSession')
    @patch('gossh_python.rpc_session._new_session')
    def test_create_session(self, go_session_constructor, py_session_constructor):
        go_session_constructor.return_value = -1

        subject = create_session(
            hostname=u'some_hostname',
            username='some_username',
            password='some_password',
            port='22',
            timeout='5',
        )

        assert_that(
            go_session_constructor.mock_calls,
            equal_to([
                call('some_hostname', 'some_username', 'some_password', 22, 5)
            ])
        )

        assert_that(
            py_session_constructor.mock_calls,
            equal_to([
                call(
                    hostname=u'some_hostname',
                    password='some_password',
                    port='22',
                    session_id=-1,
                    timeout='5',
                    username='some_username')
            ])
        )

        assert_that(
            subject,
            equal_to(
                py_session_constructor()
            )
        )
