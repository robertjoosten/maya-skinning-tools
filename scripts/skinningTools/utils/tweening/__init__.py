from . import methods


def getTweeningMethod(method):
    """
    Get the tweening method from a string, if the function doesn't exists
    None will be returned.

    :return: Tweening function
    :rtype: func/None
    """
    if method in getTweeningMethods():
        return getattr(methods, method)


def getTweeningMethods():
    """
    Get all of the available tweening methods.

    :return: Tweening methods
    :rtype: list
    """
    return [m for m in dir(methods) if m.startswith("ease")]
