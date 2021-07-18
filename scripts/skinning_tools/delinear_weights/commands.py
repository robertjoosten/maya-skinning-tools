from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim
from collections import defaultdict

from skinning_tools.utils import api
from skinning_tools.utils import math
from skinning_tools.utils import cluster
from skinning_tools.utils import conversion
from skinning_tools.utils import decorator
from skinning_tools.utils.progress import Progress


__all__ = [
    "delinear_skin_weights",
    "delinear_skin_weights_on_selection",
]


@decorator.preserve_selection
def delinear_skin_weights(components, method):
    """
    Loop over all of the provided components and see if these components
    are deformed by a skin cluster. If this is the case, the weights will be
    de-linearized by the function provided. This function is found in the
    tweening module.

    :param list[str] components:
    :param str method:
    :raise ValueError: When tweening method is not supported.
    """
    if not hasattr(math.tweening, method):
        raise ValueError("Tweening method '{}' is not supported.".format(method))

    tween = getattr(math.tweening, method)  # type: callable
    data = defaultdict(list)

    for component in components:
        data[component.split(".")[0]].append(component)

    with Progress(len(data)) as progress:
        for node, components in data.items():
            skin_cluster = cluster.get_skin_cluster(node)

            # get api objects
            skin_cluster_obj = api.conversion.get_object(skin_cluster)
            skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)

            cmds.select(components)
            selection = OpenMaya.MGlobal.getActiveSelectionList()
            node_dag, node_components = selection.getComponent(0)

            # get weights
            weights, num = skin_cluster_fn.getWeights(node_dag, node_components)
            weights_split = conversion.as_chunks(weights, num)
            weights_elements = OpenMaya.MFnSingleIndexedComponent(node_components).getElements()

            for element, weights in zip(weights_elements, weights_split):
                # calculate per vertex weights
                weights = conversion.normalize(weights)
                weights = [tween(w) for w in weights]
                weights = conversion.normalize(weights)

                # set weights
                for index, weight in enumerate(weights):
                    cmds.setAttr("{}.weightList[{}].weights[{}]".format(skin_cluster, element, index), weight)

            progress.next()


def delinear_skin_weights_on_selection(method):
    """
    All of the selected components will be queried, these components will then
    be parsed to the :func:`delinear_skin_weights` function that will process
    the weights.
    
    :param str method:
    """
    active_selection = OpenMaya.MGlobal.getActiveSelectionList()
    if not active_selection.length():
        raise RuntimeError("No selection made, unable to de-linear weights.")

    for i in range(active_selection.length()):
        dag, component = active_selection.getComponent(i)
        if component.isNull():
            if dag.hasFn(OpenMaya.MFn.kTransform):
                dag.extendToShape()
            dag, component = api.conversion.get_component(dag.fullPathName())

        selection = OpenMaya.MSelectionList()
        selection.add((dag, component))

        components = cmds.ls(selection.getSelectionStrings(), flatten=True)
        delinear_skin_weights(components, method)
