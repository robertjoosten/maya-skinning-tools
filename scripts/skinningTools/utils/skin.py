from maya import cmds


__all__ = [
    "getSkinCluster",
    "isSkinned"
]


def getSkinCluster(mesh):
    """
    Loop over an objects history and see if a skinCluster node is part of the
    history.

    :param str mesh:
    :return: skinCluster that is attached to the parsed mesh
    :rtype: str or None
    """
    skinClusters = [
        h
        for h in cmds.listHistory(mesh) or []
        if cmds.nodeType(h) == "skinCluster"
    ]

    if skinClusters:
        return skinClusters[0]


def isSkinned(mesh):
    """
    :param str mesh:
    :return: if the parsed object is a skinned mesh.
    :rtype: bool
    """
    if not cmds.nodeType(mesh) == "mesh":
        return False

    return getSkinCluster(mesh) is not None
