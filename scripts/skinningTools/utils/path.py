def asChunks(l, num):
    """
    Split a list into chunks of the provided num

    :param list l:
    :param int num: Size of split
    :return: Split list
    :rtype: list
    """
    chunks = []
    for i in xrange(0, len(l), num):
        chunks.append(l[i:i + num])

    return chunks
