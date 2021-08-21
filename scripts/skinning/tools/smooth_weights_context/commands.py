import logging
from maya import cmds
from maya.api import OpenMaya
from collections import OrderedDict

from skinning.utils import api
from skinning.utils import skin
from skinning.utils import decorator
from skinning.utils import conversion


__all__ = [
    "paint",
]

log = logging.getLogger(__name__)


class SmoothSkinWeights(object):
    """
    The smooth skin weights class manages the paint weight context using its
    initialize, set value and clean up functions. The smooth weights are
    calculated by using values of its connected neighbouring vertices.
    """
    def __init__(self):
        self.initialized = False
        self.geometry_dag = None
        self.skin_cluster_fn = None
        self.num_influences = 0
        self.influences = OpenMaya.MIntArray()
        self.locked_influences = OrderedDict()
        self.connected_components = {}
        self.normalize = -1
        self.max_influences = -1
        self.maintain_max_influences = True

    # ------------------------------------------------------------------------

    @decorator.memoize
    def get_component(self, name, indices):
        """
        :param str name:
        :param list[int] indices:
        :return: Component
        :rtype: OpenMaya.MFnSingleIndexedComponent
        """
        component = OpenMaya.MFnSingleIndexedComponent().create(OpenMaya.MFn.kMeshVertComponent)
        OpenMaya.MFnSingleIndexedComponent(component).addElements(indices)
        return component

    @decorator.memoize
    def get_connected_component(self, name, index):
        """
        :param str name:
        :param int index:
        :return: Component connected, length connected
        :rtype: OpenMaya.MFnSingleIndexedComponent,
        """
        mesh_iterator = OpenMaya.MItMeshVertex(self.geometry_dag, self.get_component(name, [index]))
        indices = mesh_iterator.getConnectedVertices()
        return self.get_component(name, indices), len(indices)

    # ------------------------------------------------------------------------

    def initialize(self, path):
        """
        Query all relevant information from the provided class. This includes
        the skin cluster, its settings and influences.

        :param str path:
        :raise RuntimeError: When no skin cluster is found
        :raise RuntimeError: When the path is not a mesh.
        """
        self.initialized = False
        self.geometry_dag = api.conversion.get_dag(path)
        self.skin_cluster_fn = skin.get_cluster_fn(path)

        if not self.geometry_dag.hasFn(OpenMaya.MFn.kMesh):
            raise RuntimeError("Unable to paint smooth weights, "
                               "node '{}' is not a mesh.".format(self.geometry_dag.partialPathName()))

        self.normalize = self.skin_cluster_fn.findPlug("normalizeWeights", False).asInt()
        self.max_influences = self.skin_cluster_fn.findPlug("maxInfluences", False).asInt()
        self.maintain_max_influences = self.skin_cluster_fn.findPlug("maintainMaxInfluences", False).asBool()

        influences = self.skin_cluster_fn.influenceObjects()
        self.num_influences = len(influences)

        self.influences.clear()
        self.locked_influences.clear()
        for i, influence in enumerate(influences):
            self.influences.append(i)

            influence_dep = OpenMaya.MFnDependencyNode(influence.node())
            if influence_dep.hasAttribute("liw"):
                self.locked_influences[i] = influence_dep.findPlug("liw", False).asBool()
            else:
                self.locked_influences[i] = False

        self.initialized = True

    def set_weights(self, id_, index, value):
        """
        Calculate new weights for the provided index and blend value using the
        connected vertices of the index. The number of maximum influences is
        maintained and so are locked influences.

        :param str id_:
        :param str index:
        :param str value:
        """
        if not self.initialized:
            return

        name = self.geometry_dag.fullPathName()
        index, value = int(index), float(value)
        component = self.get_component(name, [index])
        component_connected, num = self.get_connected_component(name, index)

        weights_new = OpenMaya.MDoubleArray()
        weights_old, _ = self.skin_cluster_fn.getWeights(self.geometry_dag, component)
        weights_connected, _ = self.skin_cluster_fn.getWeights(self.geometry_dag, component_connected)
        weights_connected = conversion.as_chunks(weights_connected, self.num_influences)

        for i, weight in enumerate(weights_old):
            if self.locked_influences[i]:
                weights_new.append(weight)
            else:
                weights_new.append(
                    sum(
                        ((weight / num) * (1 - value)) + ((weight_connected[i] / num) * value)
                        for weight_connected in weights_connected
                    )
                )

        if self.maintain_max_influences:
            weights_sorted = zip(range(self.num_influences), self.locked_influences.values(), weights_new)
            weights_excess = sorted(weights_sorted, key=lambda x: (-x[1], -x[2]))[self.max_influences:]
            for i, locked, weight in weights_excess:
                if locked and weight:
                    log.warning("Unable to maintain influences at element {}, "
                                "due to locked weights.".format(index))
                    continue

                weights_new[i] = 0.0

        if self.normalize == 1:
            factor = 0
            locked_total = sum([weight for i, weight in enumerate(weights_new) if self.locked_influences[i]])
            blend_total = sum(weights_new) - locked_total

            if blend_total > 0 and locked_total < 1.0:
                factor = (1.0 - locked_total) / blend_total
            else:
                log.warning("Unable to maintain smooth values at element {}, "
                            "due to locked weights and normalization.".format(index))

            for i, weight in enumerate(weights_new):
                if not self.locked_influences[i]:
                    weights_new[i] = weight * factor

        skin.set_weights(
            self.skin_cluster_fn,
            dag=self.geometry_dag,
            components=component,
            influences=self.influences,
            weights_old=weights_old,
            weights_new=weights_new
        )

    def clean_up(self, name=None):
        self.initialized = False
        self.geometry_dag = None
        self.skin_cluster_fn = None
        self.num_influences = 0
        self.influences.clear()
        self.locked_influences.clear()
        self.connected_components.clear()
        self.normalize = -1
        self.max_influences = -1
        self.maintain_max_influences = True

        self.get_component.clear()
        self.get_connected_component.clear()


context = SmoothSkinWeights.__name__
manager = SmoothSkinWeights()

proc_initialize = conversion.as_mel_procedure(
    manager.initialize,
    arguments=[("string", "path")]
)
proc_set_weights = conversion.as_mel_procedure(
    manager.set_weights,
    arguments=[("int", "id_"), ("int", "index"), ("float", "value")]
)
proc_clean_up = conversion.as_mel_procedure(
    manager.clean_up,
    arguments=[("string", "name")]
)


def paint():
    """
    Set the smooth weights context as a tool using the current selection.
    If the context doesn't exist it will be created.
    """
    if not cmds.artUserPaintCtx(context, query=True, exists=True):
        cmds.artUserPaintCtx(context)

    cmds.artUserPaintCtx(
        context,
        edit=True,
        initializeCmd=proc_initialize,
        setValueCommand=proc_set_weights,
        toolCleanupCmd=proc_clean_up,
        whichTool="userPaint",
        fullpaths=True,
        outwhilepaint=True,
        brushfeedback=False,
        selectedattroper="additive"
    )

    cmds.setToolTo(context)

