"""
Converted to python from Easing Equations by Robert Penner
http://gizma.com/easing/#quad3
"""

import math
from functools import wraps

# ----------------------------------------------------------------------------

def nValidate(func):
    @wraps(func)
    def wrapper(n):
        if not 0.0 <= n <= 1.0:
            raise ValueError("Value must be between 0.0 and 1.0.")

        return func(n)
    return wrapper
    
# ----------------------------------------------------------------------------

@nValidate
def easeInOutQuadratic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**2
    else:
        n -= 1
        return -0.5 * (n*(n-2) - 1)

@nValidate
def easeInOutCubic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)

@nValidate
def easeInOutQuartic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)

@nValidate
def easeInOutQuintic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)

@nValidate
def easeInOutSinusoidal(n):
    return -0.5 * (math.cos(math.pi * n) - 1)

@nValidate
def easeInOutExponential(n):
    n *= 2
    if n < 1:
        return 0.5 * math.pow(2, 10 * (n - 1))
    else:
        n -= 1
        return -math.pow( 2, -10 * n) + 2

@nValidate
def easeInOutCircular(n):
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n = n - 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)
