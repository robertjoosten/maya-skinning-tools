from maya.api import OpenMaya


__all__ = [
    "average_matrix",
]


def average_matrix(matrices):
    """
    Get the average matrix of the all of the provided matrix. All matrices
    multiplier by the multiplier of matrices and multiplied.

    :param list[OpenMaya.MMatrix] matrices:
    :return: Average matrix
    :rtype: OpenMaya.MMatrix
    """
    matrix = [0.0] * 16
    multiplier = 1.0 / len(matrices)
    for m in matrices:
        for i, value in enumerate(list(m)):
            matrix[i] = matrix[i] + (value * multiplier)

    return OpenMaya.MMatrix(matrix)
