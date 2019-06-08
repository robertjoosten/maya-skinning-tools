from maya import cmds, OpenMaya
from ..utils import api, path


def closestLineToPoint(lines, point):
    """
    Loop over all lines and find the closest point on the line from the
    provided point. After this is done the list of lines is sorted based on
    closest distance to the line.

    :param dict lines:
    :param OpenMaya.MVector point:
    :return: Closest lines and points ordered on distance
    :rtype: tuple
    """
    # get closest point on the line for each line
    names, closestPoints = zip(
        *[
            (name, api.closestPointOnLine(line[0], line[1], point))
            for name, line in lines.iteritems()
        ]
    )

    # sort the closest points from shortest to longest depending on the
    # distance to the vertex in world space position.
    return api.sortByDistance(names, point, closestPoints)


def jointsToLines(joints):
    """
    Filter the provided joints list and loop its children to generate lines
    between the parent and its children. It is possible that multiple children
    lie on the same line thinking twister joints for example. This function
    filters those out and creates lines between the twisters rather than lines
    overlapping each other.

    :param list joints:
    :return: Line data
    :rtype: dict
    """
    # variable
    lines = {}

    # full path joints
    joints = cmds.ls(joints, l=True)

    # store all joint positions
    positions = {
        j: OpenMaya.MVector(*cmds.xform(j, query=True, ws=True, t=True))
        for j in joints
    }

    # loop joints
    for j in joints:
        # get joint position
        point = positions.get(j)

        # get joint children
        children = cmds.listRelatives(j, c=True, type="joint", f=True) or []

        # filter children to make sure they are in the provided joints list
        # and the children are not at the same position as as its parent as
        # that would result in a 0 length line.
        childrenData = [
            (child, positions.get(child))
            for child in children
            if child in joints and
            (point - positions.get(child)).length() > 0.001
        ]

        # validate data
        if not childrenData:
            continue

        # sort children based on the distance to the parent point
        children, childrenPositions = zip(*childrenData)
        children, childrenPositions = api.sortByDistance(
            children,
            point,
            childrenPositions
        )

        # reverse the so furthest child is the first in the list
        children.reverse()
        childrenPositions.reverse()

        # add original parent point
        children.append(j)
        childrenPositions.append(point)

        # create iterator
        iter = zip(
            children[1:],
            childrenPositions[1:],
            children[:-1],
            childrenPositions[:-1]
        )

        # get joint lines
        for p, pPoint, t, tPoint in iter:
            # make sure the points are not at the same position
            if (pPoint - tPoint).length() < 0.001:
                continue

            # get names
            jName = path.getRootPath(j)
            pName = path.getRootPath(p)
            tName = path.getRootPath(t)

            # make sure the child point is on the line
            cPoint = api.closestPointOnLine(point, tPoint, pPoint)
            cLength = (cPoint - pPoint).length()

            # if the point is on the line it will the shorter section will be
            # added. If the point is not on the line a line to the parent
            # joint will be added.
            if cLength < 0.001:
                name = "{}:{}".format(pName, tName)
                lines[name] = [pPoint, tPoint]
            else:
                name = "{}:{}".format(jName, tName)
                lines[name] = [point, tPoint]

    return lines



