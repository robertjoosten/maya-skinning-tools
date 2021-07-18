def as_chunks(l, num):
    """
    :param list l:
    :param int num: Size of split
    :return: Split list
    :rtype: list
    """
    chunks = []
    for i in xrange(0, len(l), num):
        chunks.append(l[i:i + num])
    return chunks


def normalize(l):
    """
    :param list[float] l:
    :return: Normalized values
    :rtype: list[float]
    """
    multiplier = 1.0 / sum(l)
    return [value * multiplier for value in l]