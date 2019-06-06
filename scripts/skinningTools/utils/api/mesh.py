from maya import OpenMaya
from .conversion import asComponent


__all__ = [
    "getConnectedVertices"
]


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
