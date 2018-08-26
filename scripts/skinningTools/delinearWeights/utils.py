from maya import cmds

from . import tweening
from .. import utils


# ----------------------------------------------------------------------------


def getTweeningMethod(method):
    """
    Get the tweening method from a string, if the function doesn't exists
    None will be returned.

    :return: Tweening function
    :rtype: func/None
    """
    if method in dir(tweening):
        return getattr(tweening, method)


# ----------------------------------------------------------------------------


def getSelectedVertices():
    """
    Get all of the selected vertices. If no component mode selection is made
    all vertices of a selected mesh will be appended to the selection. 
    
    :return: List of selected vertices
    :rtype: list of strings
    """
    # get vertices
    vertices = [
        vtx 
        for vtx in cmds.ls(sl=True, fl=True, l=True) 
        if vtx.count(".vtx")
    ]

    # append meshes
    meshes = utils.getMeshesFromSelection()
    for mesh in meshes:
        vertices.extend(
            cmds.ls(
            "{0}.vtx[*]".format(mesh),
            fl=True,
            l=True
        )
    )

    return vertices


# ----------------------------------------------------------------------------


def getIndexFromString(vtx):
    """
    Get the index from a component string.
    
    :param str vtx: Path to component
    :return: Index of component string
    :rtype: int
    """
    return int(vtx.split("[")[-1][:-1])


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
