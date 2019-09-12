import unittest
import time

import os
import signal
import subprocess

from datetime import datetime

from hamcrest import assert_that, equal_to
from gossh_python import create_session

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


class SSHSimServer(object):
    """
    Calls mock_cisco in a subprocess. Run from the project root
    """

    def __init__(self):
        # You can run this command manually to start the mock ssh server
        # This is designed to be run in a docker container
        self._process = subprocess.Popen('python -m e2e_test.mock_cisco',
            shell=True,
            env=os.environ,
            cwd=os.getcwd(),
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    def close(self):
        os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False



class GoSSHBuildLibTest(unittest.TestCase):
    """
    A quick and dirty test to see the built library functioning
    """

    def test_ssh_connection(self):

        ssh_server = SSHSimServer()
        with ssh_server:
            time.sleep(2)
            session = create_session(
                hostname='127.0.0.1',
                username='testadmin',
                password='x',
                port=9999,
                timeout=1
            )
            try:
                session.connect()
                session.get_shell()
                # Wait a bit
                time.sleep(0.5)
                r0 = session.read(1024)
                assert_that(r0, equal_to('hostname>'))
                # Send a new line
                session.write('\n')
                time.sleep(0.5)
                r1 = session.read(1024)
                # The new line plus the prompt is returned
                assert_that(r1, equal_to('\r\nhostname>'))
            finally:
                session.close()