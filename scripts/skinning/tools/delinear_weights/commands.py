from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim
from collections import defaultdict

from skinning.utils import api
from skinning.utils import math
from skinning.utils import skin
from skinning.utils import decorator
from skinning.utils import conversion
from skinning.utils.progress import Progress


__all__ = [
    "delinear_weights",
    "delinear_weights_on_selection",
]


@decorator.preserve_selection
def delinear_weights(components, method):
    """
    Loop over all of the provided components and see if these components
    are deformed by a skin cluster. If this is the case, the weights will be
    de-linearized by the function provided. This function is found in the
    tweening module.

    :param list[str] components:
    :param str method:
    :raise ValueError: When blend method is not supported.
    """
    if not hasattr(math.ease, method):
        raise ValueError("Blend method '{}' is not supported.".format(method))

    tween = getattr(math.ease, method)  # type: callable
    data = defaultdict(list)

    for component in components:
        data[component.split(".")[0]].append(component)

    with Progress(len(data)) as progress:
        for node, components in data.items():
            skin_cluster = skin.get_cluster(node)

            # get api objects
            skin_cluster_obj = api.conversion.get_object(skin_cluster)
            skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)

            cmds.select(components)
            selection = OpenMaya.MGlobal.getActiveSelectionList()
            node_dag, node_components = selection.getComponent(0)

            # get weights
            weights_old, num = skin_cluster_fn.getWeights(node_dag, node_components)
            weights_new = OpenMaya.MDoubleArray()
            influences = OpenMaya.MIntArray(range(num))

            for weights in conversion.as_chunks(weights_old, num):
                weights = conversion.normalize(weights)
                weights = [tween(w) for w in weights]
                weights = conversion.normalize(weights)

                for weight in weights:
                    weights_new.append(weight)

            # set weights - undoable
            skin.set_weights(
                skin_cluster_fn,
                dag=node_dag,
                components=node_components,
                influences=influences,
                weights_old=weights_old,
                weights_new=weights_new
            )

            progress.next()


def delinear_weights_on_selection(method):
    """
    All of the selected components will be queried, these components will then
    be parsed to the :func:`delinear_skin_weights` function that will process
    the weights.
    
    :param str method:
    """
    active_selection = OpenMaya.MGlobal.getActiveSelectionList()
    if active_selection.isEmpty():
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
        delinear_weights(components, method)
