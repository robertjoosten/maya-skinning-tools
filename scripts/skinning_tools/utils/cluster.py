from maya import cmds


def get_skin_cluster(node):
    """
    Loop over an objects history and return the skin cluster node that is part
    of the history. The geometry provided will be extended to its shapes.

    :param str node:
    :return: Skin cluster
    :rtype: str/None
    """
    shapes = cmds.listRelatives(node, shapes=True) or []
    shapes.append(node)

    for node in cmds.listHistory(shapes) or []:
        if cmds.nodeType(node) == "skinCluster":
            return node
    else:
        raise RuntimeError("Node '{}' has no skin cluster in its history.".format(node))
