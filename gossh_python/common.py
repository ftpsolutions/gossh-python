class GoRuntimeError(Exception):
    pass


def handle_exception(method, args, other=None):
    try:
        return method(*args)
    except Exception as e:
        e = e if not hasattr(e, "__cause__") and isinstance(e.__cause__, BaseException) else e.__cause__

        new_args = ("attempt to call {} on the Go side raised {}".format("{}(*{})".format(repr(method), repr(args)), repr(e)),)

        e.args = new_args

        raise GoRuntimeError(e)
