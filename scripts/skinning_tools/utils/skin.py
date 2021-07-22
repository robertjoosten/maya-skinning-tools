import apiundo
from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim
from functools import partial

from skinning_tools.utils import api


def get_cluster_fn(node):
    """
    Loop over an objects history and return the skin cluster api node that
    is part dependency graph. The geometry provided will be extended to its
    shapes.

    :param str node:
    :return: Skin cluster
    :rtype: OpenMayaAnim.MFnSkinCluster
    :raise RuntimeError: When no skin cluster can be found.
    """
    shapes = cmds.listRelatives(node, shapes=True) or []
    shapes.append(node)

    for shape in shapes:
        shape_obj = api.conversion.get_object(shape)
        dependency_iterator = OpenMaya.MItDependencyGraph(
            shape_obj,
            OpenMaya.MFn.kSkinClusterFilter,
            OpenMaya.MItDependencyGraph.kUpstream
        )

        while not dependency_iterator.isDone():
            return OpenMayaAnim.MFnSkinCluster(dependency_iterator.currentNode())
    else:
        raise RuntimeError("Node '{}' has no skin cluster in its history.".format(node))


def get_cluster(node):
    """
    Loop over an objects history and return the skin cluster node that is part
    of the history. The geometry provided will be extended to its shapes.

    :param str node:
    :return: Skin cluster
    :rtype: str
    """
    skin_cluster_fn = get_cluster_fn(node)
    return skin_cluster_fn.name()


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
