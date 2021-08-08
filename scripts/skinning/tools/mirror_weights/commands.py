import logging
from maya.api import OpenMaya

from skinning.utils import api
from skinning.utils import skin
from skinning.utils import naming
from skinning.utils import symmetry
from skinning.utils import conversion


__all__ = [
    "mirror_weights",
    "mirror_weights_on_selection",
]
log = logging.getLogger(__name__)


def mirror_weights(geometry, edge, inverse=False, replace=("L", "R")):
    """
    Mirror the weights using the provided geometry and symmetry edge. An error
    will be raised when no skin cluster is attached to the geometry and the
    inverse variable determines which side gets new weights. The mapper is used
    to establish a mirror mapping between the influences.

    :param str geometry:
    :param int edge:
    :param bool inverse:
    :param tuple[str] replace:
    :raise RuntimeError: When symmetry cannot be established.
    :raise RuntimeError: When no skin cluster is attached.
    :raise RuntimeError: When no influences cannot be mirrored.
    """
    # get dag
    dag = api.conversion.get_dag(geometry)
    dag.extendToShape()

    # get skin cluster
    skin_cluster_fn = skin.get_cluster_fn(geometry)

    # get influences
    influences_mirror = {}
    influences_mapper = {
        naming.get_leaf_name(influence.partialPathName()): i
        for i, influence in enumerate(skin_cluster_fn.influenceObjects())
    }
    num_influences = len(influences_mapper)

    # build influences mirror map
    replacement_valid = False
    replacement_mapper = [(replace[0], replace[1], 1), (replace[1], replace[0], 1)]
    for influence, i in influences_mapper.items():
        for arguments in replacement_mapper:
            influence_mirror = influence.replace(*arguments)
            if influence != influence_mirror and influence_mirror in influences_mapper:
                influences_mirror[i] = influences_mapper[influence_mirror]
                replacement_valid = True
                break
        else:
            influences_mirror[i] = i

    if not replacement_valid:
        raise RuntimeError("No mirrored influences found using "
                           "('{}', '{}') as replacement arguments.".format(*replace))

    # create symmetry
    sym = symmetry.Symmetry(geometry)
    sym.calculate_symmetry(edge, use_cache=False)

    # get symmetry elements
    mode = symmetry.LEFT if inverse else symmetry.RIGHT
    elements = sym.filter(sym.vertices, mode)
    elements.sort()

    # calculate new weights
    weights = OpenMaya.MDoubleArray()
    influences = OpenMaya.MIntArray(range(num_influences))

    weights_complete, _ = skin_cluster_fn.getWeights(dag, OpenMaya.MObject())
    weights_complete = conversion.as_chunks(weights_complete, num_influences)

    for element in elements:
        element_mirror = sym.vertices[element]
        weights_array = weights_complete[element_mirror]

        for i in range(num_influences):
            influence_mirror = influences_mirror[i]
            weights.append(weights_array[influence_mirror])

    # set new weights
    component_fn = OpenMaya.MFnSingleIndexedComponent()
    component = component_fn.create(OpenMaya.MFn.kMeshVertComponent)
    component_fn.addElements(elements)

    skin.set_weights(
        skin_cluster_fn,
        dag,
        component,
        influences,
        weights,
    )

    log.info("Successfully mirrored weights for '{}'.".format(geometry))


def mirror_weights_on_selection(inverse=False, replace=("L", "R")):
    """
    Mirror the weights using the current selection. The selection is supposed
    to be a mesh edge which dictates the symmetry. An error will be raised
    when no skin cluster is attached to the geometry and the inverse variable
    determines which side gets new weights. The mapper is used to establish a
    mirror mapping between the influences.

    :param bool inverse:
    :param tuple[str] replace:
    :raise RuntimeError: When nothing is selected.
    :raise RuntimeError: When no edge is selected
    :raise RuntimeError: When symmetry cannot be established.
    :raise RuntimeError: When no skin cluster is attached.
    :raise RuntimeError: When no influences cannot be mirrored.
    """
    selection = OpenMaya.MGlobal.getActiveSelectionList()
    if selection.isEmpty():
        raise RuntimeError("No selection made, unable to mirror weights.")

    dag, component = selection.getComponent(0)
    if component.isNull() or not component.hasFn(OpenMaya.MFn.kMeshEdgeComponent):
        raise RuntimeError("No edge selected, unable to mirror weights.")

    geometry = dag.partialPathName()
    component_fn = OpenMaya.MFnSingleIndexedComponent(component)
    mirror_weights(geometry, component_fn.element(0), inverse=inverse, replace=replace)
