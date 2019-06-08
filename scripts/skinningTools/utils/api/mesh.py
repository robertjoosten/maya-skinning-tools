from maya import OpenMaya
from .conversion import asComponent


__all__ = [
    "getPoints",
    "getNormals",
    "getConnectedVertices",
    "getConnectedVerticesMapper"
]


def getPoints(dag):
    """
    Get the position in world space of each vertex on the provided mesh.

    :param OpenMaya.MDagPath dag:
    :return: Points
    :rtype: list
    """
    points = OpenMaya.MPointArray()
    mesh = OpenMaya.MFnMesh(dag)
    mesh.getPoints(points, OpenMaya.MSpace.kWorld)

    return [OpenMaya.MVector(points[i]) for i in range(points.length())]


def getNormals(dag):
    """
    Get the average normal in world space of each vertex on the provided mesh.
    The reason why OpenMaya.MItMeshVertex function has to be used is that the
    MFnMesh class returns incorrect normal results.

    :param OpenMaya.MDagPath dag:
    :return: Normals
    :rtype: list
    """
    # variables
    normals = []

    iter = OpenMaya.MItMeshVertex(dag)
    while not iter.isDone():
        # get normal data
        normal = OpenMaya.MVector()
        iter.getNormal(normal, OpenMaya.MSpace.kWorld)
        normals.append(normal)

        iter.next()

    return normals


def getConnectedVertices(dag, component):
    """
    index -> OpenMaya.MFn.kMeshVertComponent

    :param OpenMaya.MDagPath dag:
    :param OpenMaya.MFn.kMeshVertComponent component:
    :return: Initialized component(s), number of connected vertices
    :rtype: tuple(OpenMaya.MFn.kMeshVertComponent, int)
    """
    connected = OpenMaya.MIntArray()

    # get connected vertices
    iter = OpenMaya.MItMeshVertex(dag, component)
    iter.getConnectedVertices(connected)

    # get component of connected vertices
    component = asComponent(connected)
    return component, len(connected)


def getConnectedVerticesMapper(dag):
    """
    Create a dictionary where the keys are the indices of the vertices and the
    values a list of indices of the connected vertices.

    :param OpenMaya.MDagPath dag:
    :return: Connected vertices mapper
    :rtype: dict
    """
    # variable
    data = {}

    # get connected vertices
    connected = OpenMaya.MIntArray()
    iter = OpenMaya.MItMeshVertex(dag)

    while not iter.isDone():
        # get connected data
        iter.getConnectedVertices(connected)
        data[iter.index()] = [c for c in connected]

        # go next
        iter.next()

    return data
