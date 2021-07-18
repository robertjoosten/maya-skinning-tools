import maya.cmds as cmds
from functools import wraps


class UndoChunk(object):
    """
    When using QT to trigger commands, it is a known bug that the undo is
    split into individual cmds commands. Wrapping the command in this context
    will enforce that the entire action is undoable with one click.
    """
    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)


class UndoDisable(object):
    """
    This context can be used to disable the undo queue. Before this happens
    the state is stored and reset once the context is exited.
    """
    def __init__(self, flush=True):
        self.state = cmds.undoInfo(query=True, state=True)
        self.key = "state" if flush else "stateWithoutFlush"

    def __enter__(self):
        cmds.undoInfo(**{self.key: False})

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(**{self.key: self.state})


def chunk(func):
    """
    Wrap the function call in a undo chuck. When using QT all things executed
    will be separated. This undo chunk decorator will allow for these to be
    chunked as one again.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with UndoChunk():
            return func(*args, **kwargs)

    return wrapper


def disable(flush=True):
    """
    Wrap the function call in a disabling of the undo queue. The flush state
    can be provided in the decorator.

    :param bool flush:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with UndoDisable(flush=flush):
                return func(*args, **kwargs)

        return wrapper
    return decorator
