from maya import OpenMaya


__all__ = [
    "getAverageVector"
]


def getAverageVector(vectors):
    """
    Get the average vector of the all of the provided vectors. All vectors
    will be added up and divided by the number of the provided vectors.

    :param list vectors:
    :return: Average vector
    :rtype: OpenMaya.MVector
    """
    vector = OpenMaya.MVector()
    for v in vectors:
        vector += v

    vector /= len(vectors)
    return vector
