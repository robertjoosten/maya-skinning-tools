import logging
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from collections import OrderedDict

from skinning.utils import api
from skinning.utils import skin
from skinning.utils import conversion


__all__ = [
    "paint",
]

log = logging.getLogger(__name__)


class RemoveSkinWeights(object):
    """
    The remove skin weights class manages the paint weight context using its
    initialize, set value and clean up functions. The smooth weights are
    calculated by using values of its connected neighbouring vertices.
    """
    def __init__(self):
        self.geometry_dag = OpenMaya.MDagPath()
        self.skin_cluster_fn = OpenMayaAnim.MFnSkinCluster()
        self.num_influences = 0
        self.influence_index = -1
        self.influence_dag = OpenMaya.MDagPath()
        self.influences = OpenMaya.MIntArray()
        self.locked_influences = OrderedDict()
        self.normalize = -1
        self.before_component = None

        self.mask = None
        self.indexed_component = None
        self.geometry_component = None

    # ------------------------------------------------------------------------

    def is_valid(self):
        """
        Make sure that the geometry, skin cluster and influence still exist
        in the scene.

        :return: Valid state
        :rtype: bool
        """
        dag_handle = OpenMaya.MObjectHandle(self.geometry_dag.node())
        skin_cluster_handle = OpenMaya.MObjectHandle(self.skin_cluster_fn.object())
        influence_handle = OpenMaya.MObjectHandle(self.influence_dag.node())

        if dag_handle.isValid() and skin_cluster_handle.isValid() and influence_handle.isValid():
            return True
        else:
            return False

    # ------------------------------------------------------------------------

    def initialize(self, geometry, influence):
        """
        Query all relevant information from the provided class. This includes
        the skin cluster, and influence information.

        :param str geometry:
        :param str influence:
        :raise RuntimeError: When no skin cluster is found
        :raise RuntimeError: When geometry type is not supported
        :raise RuntimeError: When the provided influence is locked.
        """
        self.geometry_dag = api.conversion.get_dag(geometry)
        self.geometry_dag.extendToShape()

        self.skin_cluster_fn = skin.get_cluster_fn(geometry)
        self.normalize = self.skin_cluster_fn.findPlug("normalizeWeights", False).asInt()

        influences = self.skin_cluster_fn.influenceObjects()
        self.num_influences = len(influences)

        self.influence_dag = api.conversion.get_dag(influence)
        self.influences.clear()
        self.locked_influences.clear()
        for i, influence_dag in enumerate(influences):
            if influence_dag == self.influence_dag:
                self.influence_index = i

            self.influences.append(i)

            influence_dep = OpenMaya.MFnDependencyNode(influence_dag.node())
            if influence_dep.hasAttribute("liw"):
                self.locked_influences[i] = influence_dep.findPlug("liw", False).asBool()
                if self.locked_influences[i] and self.influence_index == i:
                    raise RuntimeError("Influence '{}' is locked.".format(influence))
            else:
                self.locked_influences[i] = False

        self.mask = OpenMaya.MSelectionMask(OpenMaya.MSelectionMask.kSelectObjectsMask)
        self.mask.addMask(OpenMaya.MSelectionMask.kSelectJoints)
        if self.geometry_dag.hasFn(OpenMaya.MFn.kMesh):
            self.mask.addMask(OpenMaya.MSelectionMask.kSelectVertices)
            self.indexed_component = OpenMaya.MFnSingleIndexedComponent
            self.geometry_component = OpenMaya.MFn.kMeshVertComponent
        elif self.geometry_dag.hasFn(OpenMaya.MFn.kNurbsCurve):
            self.mask.addMask(OpenMaya.MSelectionMask.kSelectCVs)
            self.indexed_component = OpenMaya.MFnDoubleIndexedComponent
            self.geometry_component = OpenMaya.MFn.kCurveCVComponent
        elif self.geometry_dag.hasFn(OpenMaya.MFn.kNurbsSurface):
            self.mask.addMask(OpenMaya.MSelectionMask.kSelectCVs)
            self.indexed_component = OpenMaya.MFnDoubleIndexedComponent
            self.geometry_component = OpenMaya.MFn.kSurfaceCVComponent
        else:
            raise RuntimeError("Geometry of type '{}' not supported.".format(self.geometry_dag.node().apiTypeStr))

        selection = OpenMaya.MSelectionList()
        selection.add(self.geometry_dag)
        selection.add(self.influence_dag)

        points, _ = self.skin_cluster_fn.getPointsAffectedByInfluence(self.influence_dag)
        if points.length():
            selection.merge(points)

        OpenMaya.MGlobal.setSelectionMode(OpenMaya.MGlobal.kSelectComponentMode)
        OpenMaya.MGlobal.setComponentSelectionMask(self.mask)
        OpenMaya.MGlobal.setActiveSelectionList(selection)

    def cache_selection(self):
        """
        Cache the selection, this cached selection will be used to retrieve
        the removed elements when the set_weights method is called.
        """
        if not self.is_valid():
            return

        selection = OpenMaya.MGlobal.getActiveSelectionList()
        if selection.isEmpty():
            return

        _, self.before_component = selection.getComponent(0)

    def set_weights(self):
        """
        Set the skin weights using the difference between the current and
        cached selection. The weights of this difference will be queried and
        adjusted to remove the influence of the selected influences.
        """
        if not self.is_valid():
            return

        selection = OpenMaya.MGlobal.getActiveSelectionList()
        if selection.isEmpty():
            return

        _, current_component = selection.getComponent(0)

        before_elements = set(self.indexed_component(self.before_component).getElements())
        current_elements = set(self.indexed_component(current_component).getElements())
        elements = before_elements - current_elements
        if not elements:
            return

        component_fn = self.indexed_component()
        component = component_fn.create(self.geometry_component)
        component_fn.addElements(elements)

        weights_new = OpenMaya.MDoubleArray()
        weights_old, _ = self.skin_cluster_fn.getWeights(self.geometry_dag, component)
        weights_chunked = conversion.as_chunks(weights_old, self.num_influences)

        for i, weights in enumerate(weights_chunked):
            weight = weights[self.influence_index]
            weight_total = sum(weights)

            if weight == weight_total:
                component_fn = self.indexed_component(component)
                element = component_fn.element(i)
                log.warning("Unable to remove weights at element {}, "
                            "it contains all the weights".format(element))
            else:
                weights[self.influence_index] = 0.0

            if self.normalize == 1:
                factor = 0
                locked_total = sum([weight for i, weight in enumerate(weights) if self.locked_influences[i]])
                blend_total = sum(weights) - locked_total

                if blend_total > 0 and locked_total < 1.0:
                    factor = (1.0 - locked_total) / blend_total
                else:
                    log.warning("Unable to maintain smooth values at element {}, "
                                "due to locked weights and normalization.".format(element))

                for j, weight in enumerate(weights):
                    if not self.locked_influences[j]:
                        weights_new.append(weight * factor)
                    else:
                        weights_new.append(weight)
            else:
                for weight in enumerate(weights):
                    weights_new.append(weight)

        skin.set_weights(
            self.skin_cluster_fn,
            dag=self.geometry_dag,
            components=component,
            influences=self.influences,
            weights_old=weights_old,
            weights_new=weights_new
        )


context = RemoveSkinWeights.__name__
manager = RemoveSkinWeights()

proc_before_stroke = conversion.as_mel_procedure(manager.cache_selection)
proc_after_stroke = conversion.as_mel_procedure(manager.set_weights)


def paint(geometry, influence):
    """
    Set the remove weights context as a tool using the current selection.
    If the context doesn't exist it will be created.

    :param str geometry:
    :param str influence:
    """
    if not cmds.artSelectCtx(context, query=True, exists=True):
        cmds.artSelectCtx(context)

    cmds.artSelectCtx(
        context,
        edit=True,
        beforeStrokeCmd=proc_before_stroke,
        afterStrokeCmd=proc_after_stroke,
        selectop="unselect",
        outwhilepaint=True,
        brushfeedback=False
    )

    manager.initialize(geometry, influence)
    cmds.setToolTo(context)

