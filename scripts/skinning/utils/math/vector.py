from maya.api import OpenMaya


__all__ = [
    "average_vector",
    "smooth_vectors"
]


def average_vector(vectors):
    """
    Get the average vector of the all of the provided vectors. All vectors
    will be added up and divided by the number of the provided vectors.

    :param list[OpenMaya.MVector] vectors:
    :return: Average vector
    :rtype: OpenMaya.MVector
    """
    vector = OpenMaya.MVector()
    for v in vectors:
        vector += v

    vector /= len(vectors)
    return vector


def smooth_vectors(vectors, connections, iterations=3):
    """
    Perform smoothing on the provided vectors based on a connections mapper.
    The position of the new vector is set based on the index of that vector
    and its connected vectors based on the connected indices. The new vector
    position is the average position of the connected vectors.

    :param list[OpenMaya.MVector] vectors:
    :param dict connections:
    :param int iterations:
    :return: Smooth vectors
    :rtype: list[OpenMaya.MVector]
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
            indices = connections.get(j, [])
            neighbours = [copy[i] for i in indices]
            vectors[j] = average_vector(neighbours)

    return vectors
