from maya import cmds
from functools import wraps


def loadPlugin(plugin):
    """
    This decorator can be used on functions that require a certain plugin to
    be loaded.

    :param str plugin:
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
            registered = cmds.pluginInfo(plugin, q=True, registered=True)

            if not registered or not loaded:
                cmds.loadPlugin(plugin)

            return func(*args, **kwargs)
        return inner
    return wrapper
