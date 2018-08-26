"""
Converted to python from Easing Equations by Robert Penner
http://gizma.com/easing/#quad3
"""

import math
from functools import wraps

# ----------------------------------------------------------------------------


EPSILON = 0.0001


# ----------------------------------------------------------------------------


def validate(func):
    @wraps(func)
    def wrapper(n):
        if not 0.0-EPSILON <= n <= 1.0+EPSILON:
            raise ValueError("Value must be between 0.0 and 1.0.")

        return func(n)
    return wrapper


# ----------------------------------------------------------------------------


@validate
def easeInOutQuadratic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**2
    else:
        n -= 1
        return -0.5 * (n*(n-2) - 1)


@validate
def easeInOutCubic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)


@validate
def easeInOutQuartic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


@validate
def easeInOutQuintic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


@validate
def easeInOutSinusoidal(n):
    return -0.5 * (math.cos(math.pi * n) - 1)


@validate
def easeInOutExponential(n):
    n *= 2
    if n < 1:
        return 0.5 * math.pow(2, 10 * (n - 1))
    else:
        n -= 1
        return -math.pow( 2, -10 * n) + 2


@validate
def easeInOutCircular(n):
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n = n - 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)
