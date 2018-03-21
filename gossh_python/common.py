class GoRuntimeError(Exception):
    pass


def handle_exception(method, args):
    try:
        return method(*args)
    except RuntimeError as e:
        raise GoRuntimeError('{0} raised on Go side while calling {1} with args {2}'.format(
            repr(e), method, repr(args),
        ))
