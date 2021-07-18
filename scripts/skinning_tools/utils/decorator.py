from maya import cmds
from functools import wraps


def memoize(func):
    """
    The memoize decorator will cache the result of a function and store it
    in a cache dictionary using its arguments and keywords arguments as a key.
    The cache can be cleared by calling the cache_clear function on the
    decorated function.
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    def clear():
        cache.clear()

    wrapper.clear = clear
    return wrapper


def preserve_selection(func):
    """
    The preserve selection will store the maya selection before the function
    is ran and restore it once the function has executed.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # query and clear selection
        selection = cmds.ls(selection=True)
        cmds.select(clear=True)

        # execute function
        ret = func(*args, **kwargs)

        # restore selection
        if selection:
            cmds.select(selection)
        else:
            cmds.select(clear=True)

        return ret

    return wrapper
