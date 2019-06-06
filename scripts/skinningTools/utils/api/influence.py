from maya import OpenMaya


__all__ = [
    "getInfluences"
]


def getInfluences(skinCluster):
    """
    Get all of the influence data connected to the skinCluster. This is a
    OpenMaya.MDagPathArray, OpenMaya.MIntArray() and a regular list of partial
    names.

    :param OpenMaya.MFnSkinCluster skinCluster:
    :return: Dag paths, integer and partial names
    :rtype: tuple(
        OpenMaya.MDagPathArray
        OpenMaya.MIntArray
        list of strings
    )
    """
    # variables
    influencesDag = OpenMaya.MDagPathArray()
    influencesI = OpenMaya.MIntArray()
    influencesN = []

    # get influences
    skinCluster.influenceObjects(influencesDag)

    # get influences data
    for i in range(influencesDag.length()):
        influencesI.append(i)
        influencesN.append(influencesDag[i].partialPathName())

    return influencesDag, influencesI, influencesN