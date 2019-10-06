"""
Manual mem test.
1. Make a virtual env and install all deps
2. run `python setup.py install`
3. run `python mem_test.py`
4. Watch memory usage and make sure it doesn't get out of control
"""
from gossh_python import create_session
from gossh_python.common import GoRuntimeError
import traceback
import time
from guppy import hpy


print(hpy().heap())

err_count = 0
while True:
    try:
        # This will just fail to connect over and over
        # which can make memory leak
        session = create_session(hostname='doesnotexist',
                                 username='test',
                                 password='pass',
                                 timeout=1, port=1234)
        session.connect()
    except KeyboardInterrupt:
        break
    except (RuntimeError, GoRuntimeError):
        err_count += 1

print(hpy().heap())

print('done')


