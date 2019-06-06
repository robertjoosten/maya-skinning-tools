from maya import OpenMaya, OpenMayaAnim


__all__ = [
    "asMObject",
    "asMDagPath",
    "asMFnSkinCluster"
]


def asMObject(path):
    """
    str -> OpenMaya.MObject

    :param str path: Path to Maya object
    :rtype: OpenMaya.MObject
    """
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(path)

    obj = OpenMaya.MObject()
    selectionList.getDependNode(0, obj)
    return obj


def asMDagPath(obj):
    """
    OpenMaya.MObject -> OpenMaya.MDagPath

    :param OpenMaya.MObject obj:
    :rtype: OpenMaya.MDagPath
    """
    return OpenMaya.MDagPath.getAPathTo(obj)


def asMFnSkinCluster(obj):
    """
    OpenMaya.MObject -> OpenMaya.MFnSkinCluster

    :param OpenMaya.MObject obj:
    :rtype: OpenMaya.MFnSkinCluster
    """
    iter = OpenMaya.MItDependencyGraph(
        obj,
        OpenMaya.MFn.kSkinClusterFilter,
        OpenMaya.MItDependencyGraph.kUpstream
    )

    while not iter.isDone():
        return OpenMayaAnim.MFnSkinCluster(iter.currentItem())