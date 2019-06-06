from maya import cmds


__all__ = [
    "addInfluences"
]


def addInfluences(skinCluster, influences):
    """
    Add influences to the skin cluster. Expects full path influences. Will
    try to reach the bind pose before attached the new influences to the skin
    cluster.

    :param str skinCluster:
    :param list influences:
    """
    # get existing influences
    existing = cmds.skinCluster(skinCluster, query=True, influence=True)
    existing = cmds.ls(existing, l=True)

    # try restoring dag pose
    try:
        cmds.dagPose(existing, restore=True, g=True, bindPose=True)
    except:
        cmds.warning("Unable to reach dagPose!")

    # add influences
    for influence in influences:
        if influence not in existing:
            cmds.skinCluster(
                skinCluster,
                edit=True,
                addInfluence=influence,
                weight=0.0
            )


def splitByInfluences(weights, num):
    """
    Split a list of weights into the size of the number of influences.

    :param list weights: List of weights
    :param int num: Size of split
    :return: Index of component string
    :rtype: int
    """
    chunks = []
    for i in xrange(0, len(weights), num):
        chunks.append(weights[i:i + num])

    return chunks