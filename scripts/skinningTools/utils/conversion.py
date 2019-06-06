from maya import cmds


def componentIndexFromString(vtx):
    """
    Get the index from a component string.

    :param str vtx: Path to component
    :return: Index of component string
    :rtype: int
    """
    return int(vtx.split("[")[-1][:-1])


def meshToVertices(mesh):
    """
    :param str mesh:
    :return: Mesh vertices
    :rtype: list
    """
    return cmds.ls("{}.vtx[*]".format(mesh), fl=True, l=True) or []
