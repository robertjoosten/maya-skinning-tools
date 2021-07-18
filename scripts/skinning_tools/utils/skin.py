import apiundo
from maya import cmds
from functools import partial


def get_cluster(node):
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


def set_weights(skin_cluster, dag, components, influences, weights_old, weights_new):
    """
    Set the skin weights via the API but add them to the undo queue using the
    apiundo module.

    :param OpenMayaAnim.MFnSkinCluster skin_cluster:
    :param OpenMaya.MDagPath dag:
    :param OpenMaya.MObject components:
    :param OpenMaya.MIntArray influences:
    :param OpenMaya.MDoubleArray weights_old:
    :param OpenMaya.MDoubleArray weights_new:
    """
    undo = partial(skin_cluster.setWeights, dag, components, influences, weights_old)
    redo = partial(skin_cluster.setWeights, dag, components, influences, weights_new)

    apiundo.commit(undo=undo, redo=redo)
    redo()
