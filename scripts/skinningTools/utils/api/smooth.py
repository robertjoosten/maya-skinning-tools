from .vector import getAverageVector


__all__ = [
    "laplacianSmoothing"
]


def laplacianSmoothing(vectors, connected, iterations=3):
    """
    Perform a laplacian smoothing on the provided vectors based on a
    connection mapper. The position of the new vector is set based on the
    index of that vector and its connected vectors based on the connected
    indices. The new vector position is the average position of the connected
    vectors.

    :param list vectors:
    :param dict connected:
    :param int iterations:
    :return: Smoothed vectors
    :rtype: list
    """
    # get length
    length = len(vectors)

    # copy vectors
    vectors = vectors[:]

    # loop iterations
    for i in range(iterations):
        # copy vectors again to make sure the connected information queried
        # hasn't been smoothed already
        copy = vectors[:]

        # loop vectors
        for j in range(length):
            # get connected vectors
            indices = connected.get(j)
            neighbours = [copy[i] for i in indices]

            # set average vector
            vectors[j] = getAverageVector(neighbours)

    return vectors
