from maya import cmds, OpenMaya
from . import skin, joint
from ..utils import api, tweening


def setInitialWeights(
        mesh,
        joints,
        components=None,
        iterations=3,
        projection=0,
        blend=False,
        blendMethod=None
):
    """
    The set initial weights function will set the skin weights on a mesh and
    the isolate only the provided components of any. Each vertex will only
    have one influence, the best influence is determined by generating lines
    for each of the joints and determining the line closest to the vertex. The
    vertex points can be altered as well using laplacian smoothing operations
    to details or overlapping and the project can be used to project the point
    along its normal to get it closer to the preferred joints.

    :param str mesh:
    :param list joints:
    :param list/None components:
    :param int iterations: Number of smoothing iterations
    :param float/int projection: Value between 0-1
    """
    # get skin cluster
    sk = skin.getSkinCluster(mesh, joints)

    # to api
    obj = api.asMObject(mesh)
    dag = api.asMDagPath(obj)

    # get joint line data
    lines = joint.jointsToLines(joints)

    # get connected data
    connections = api.getConnectedVerticesMapper(dag)

    # get points
    points = api.getPoints(dag)

    # get normals
    normals = api.getNormals(dag)

    # apply smoothing
    points = api.laplacianSmoothing(points, connections, iterations)
    normals = api.laplacianSmoothing(normals, connections, iterations)

    # get components
    components = components if components else range(len(points))

    # get blend method
    blendMethod = tweening.getTweeningMethod(blendMethod) \
        if blendMethod \
        else None

    # loop components
    for i in components:
        # get component data
        point = points[i]
        normal = normals[i].normal()
        vertex = "{}.vtx[{}]".format(mesh, i)

        # get closest line
        names, closestPoints = joint.closestLineToPoint(lines, point)

        # displace the point
        if projection:
            # get data for first
            closestPoint = closestPoints[0]
            closestDistance = (point - closestPoint).length()

            # get new point moving the point along the normal using the
            # project value as a multiplier to the closest distance.
            point = point + (normal * closestDistance * projection * -1)

            # get closest line
            names, closestPoints = joint.closestLineToPoint(lines, point)

        # get influence
        influenceName = names[0]
        influenceParent, influenceChild = influenceName.split("@")

        # get default transform value
        transformValue = [[influenceParent, 1]]

        # calculate blend method
        if blend:
            # get parameter
            a, b = lines.get(influenceName)
            parameter = api.parameterOfPointOnLine(a, b, closestPoints[0])

            # run parameter through blend method
            if blendMethod:
                parameter = blendMethod(parameter)

            # set new transform value
            transformValue = [
                [influenceParent, 1 - parameter],
                [influenceChild, parameter]
            ]

        # set skinning
        cmds.skinPercent(sk, vertex, transformValue=transformValue)
