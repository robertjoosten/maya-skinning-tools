"""
Converted to python from Easing Equations by Robert Penner
http://gizma.com/easing/#quad3
"""
import math


def easeInOutQuadratic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**2
    else:
        n -= 1
        return -0.5 * (n*(n-2) - 1)


def easeInOutCubic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)


def easeInOutQuartic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


def easeInOutQuintic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


def easeInOutSinusoidal(n):
    return -0.5 * (math.cos(math.pi * n) - 1)


def easeInOutExponential(n):
    n *= 2
    if n < 1:
        return 0.5 * math.pow(2, 10 * (n - 1))
    else:
        n -= 1
        return -math.pow( 2, -10 * n) + 2


def easeInOutCircular(n):
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n = n - 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)
