__all__ = [
    "closestPointOnLine",
    "parameterOfPointOnLine",
    "sortByDistance"
]


def closestPointOnLine(a, b, point):
    """
    Get the closest point on a line. The line is defined by the provided a
    and b point. The point is the point in space that is used to find the
    closest point on the line.

    :param OpenMaya.MVector a:
    :param OpenMaya.MVector b:
    :param OpenMaya.MVector point:
    :return: Closest point on line
    :rtype: OpenMaya.MVector
    """
    # get vectors
    ap = point - a
    ab = b - a

    # get distance multiplier using dot product
    length = ab.length() ** 2
    dot = ap * ab
    distance = dot / length

    if distance < 0:
        return a
    elif distance > 1:
        return b
    else:
        return a + ab * distance


def parameterOfPointOnLine(a, b, point):
    """
    Get the parameter of a point on a line. For this function to give a
    correct result it is important that the provided point already lies on the
    line. The :func:`closestPointOnLine` can be used to get that point on the
    line.

    :param OpenMaya.MVector a:
    :param OpenMaya.MVector b:
    :param OpenMaya.MVector point:
    :return: Parameter of the point on the line
    :rtype: float
    """
    # get vectors
    ap = point - a
    ab = b - a

    # get parameter
    parameter = ap.length() / ab.length()
    return parameter


def sortByDistance(nodes, point, points):
    """
    Sort the provided nodes list based on the distance between the point and
    the points. With the nodes sorted from shortest distance to longest. It
    is expected that the order of the nodes link with the order of the points.

    :param list nodes:
    :param OpenMaya.MVector point:
    :param list points:
    :return: Sorted node list and sorted points list
    :rtype: tuple(list, list)
    """
    # sort nodes
    iter = zip(nodes, points)
    iter.sort(key=lambda x: (x[1] - point).length())

    # extract
    nodes, points = zip(*iter)
    return list(nodes), list(points)
