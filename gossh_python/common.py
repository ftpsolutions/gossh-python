from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
class GoRuntimeError(Exception):
    pass


def handle_exception(method, args, other=None):
    try:
        return method(*args)
    except RuntimeError as e:
        raise GoRuntimeError(
            '{0} raised on Go side while calling {1} with args {2} from {3}'.format(
                repr(e), repr(method), repr(args), repr(other)
            )
        )
