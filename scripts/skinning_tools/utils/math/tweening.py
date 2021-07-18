"""
Converted to python from Easing Equations by Robert Penner
http://gizma.com/easing/#quad3
"""
from __future__ import absolute_import
import math


__all__ = [
    "ease_in_out_quadratic",
    "ease_in_out_cubic",
    "ease_in_out_quartic",
    "ease_in_out_quintic",
    "ease_in_out_sinusoidal",
    "ease_in_out_exponential",
    "ease_in_out_circular"
]


def ease_in_out_quadratic(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return 0.5 * n**2
    else:
        n -= 1
        return -0.5 * (n*(n-2) - 1)


def ease_in_out_cubic(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)


def ease_in_out_quartic(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


def ease_in_out_quintic(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


def ease_in_out_sinusoidal(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    return -0.5 * (math.cos(math.pi * n) - 1)


def ease_in_out_exponential(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return 0.5 * math.pow(2, 10 * (n - 1))
    else:
        n -= 1
        return -math.pow( 2, -10 * n) + 2


def ease_in_out_circular(n):
    """
    :param float n: 0-1
    :return: Tweened value
    """
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n = n - 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)
