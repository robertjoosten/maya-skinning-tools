import logging
from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim
from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import api
from skinning.utils import skin
from skinning.utils import undo
from skinning.utils import naming
from skinning.utils import influence
from skinning.utils import conversion


log = logging.getLogger(__name__)

WINDOW_TITLE = "Soft Selection to Weights"
WINDOW_ICON = gui.get_icon_file_path("ST_softSelectionToWeights.png")
ADD_ICON = gui.get_icon_file_path("setEdAddCmd.png")
REMOVE_ICON = gui.get_icon_file_path("setEdRemoveCmd.png")
JOINT_ICON = gui.get_icon_file_path("kinJoint.png")
SOFT_SELECT_ICON = gui.get_icon_file_path("customSoftSelectFalloffCurve.png")
SELECT_ICON = gui.get_icon_file_path("redSelect.png")
INVALID_STYLESHEET = "QLabel{color: gray}"


class JointWidget(QtWidgets.QWidget):
    joint_changed = QtCore.Signal(str)

    def __init__(self, parent):
        super(JointWidget, self).__init__(parent)

        self.joint = None
        self.scale_factor = self.logicalDpiX() / 96.0

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create menu
        self.menu = QtWidgets.QMenu()

        self.select_joint_action = QtWidgets.QAction(QtGui.QIcon(SELECT_ICON), "Select joint", self)
        self.select_joint_action.triggered.connect(self.select_joint)
        self.menu.addAction(self.select_joint_action)

        # create widgets
        set_joint = QtWidgets.QPushButton(self)
        set_joint.setFlat(True)
        set_joint.setIcon(QtGui.QIcon(JOINT_ICON))
        set_joint.setIconSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        set_joint.setFixedSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        set_joint.released.connect(self.set_joint_from_selection)
        layout.addWidget(set_joint)

        self.joint_label = QtWidgets.QLabel(self)
        self.joint_label.setText("Joint")
        self.joint_label.setStyleSheet(INVALID_STYLESHEET)
        layout.addWidget(self.joint_label)

        self.customContextMenuRequested.connect(self.display_menu)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    # ------------------------------------------------------------------------

    def display_menu(self, point):
        """
        :param QtCore.QPoint point:
        """
        self.menu_about_to_show()
        self.menu.exec_(self.mapToGlobal(point))

    def menu_about_to_show(self):
        """
        This function makes sure that the menu items that are displayed are
        valid, if this is not the case they should be disabled before showing
        the menu. If any custom menu actions are added, display logic can be
        implemented here.
        """
        state = self.joint is not None and cmds.objExists(self.joint)
        self.select_joint_action.setEnabled(state)

    # ------------------------------------------------------------------------

    @gui.display_error
    def select_joint(self):
        cmds.select(self.joint)

    @gui.display_error
    def set_joint_from_selection(self):
        """
        Query the current selection filtering for joints. Set the first
        selected joint as the influence and update the UI to display this
        information to the user.

        :raise RuntimeError: When no joints are selected.
        """
        joints = cmds.ls(selection=True, type="joint")
        if not joints:
            raise RuntimeError("Influences can only be of type joint, "
                               "please select a joint.")

        influence_name = naming.get_name(joints[0])
        self.joint = joints[0]
        self.joint_label.setText(influence_name)
        self.joint_label.setStyleSheet(None)
        self.joint_changed.emit(self.joint)


class InfluenceWidget(JointWidget):
    soft_selection_changed = QtCore.Signal()

    def __init__(self, parent):
        super(InfluenceWidget, self).__init__(parent)

        self.selection = OpenMaya.MSelectionList()
        self.soft_selection = OpenMaya.MRichSelection()
        self.soft_selection_map = {}
        self.soft_selection_curve = None
        self.soft_selection_falloff = None
        self.soft_selection_distance = None

        # update menu
        self.select_soft_action = QtWidgets.QAction(QtGui.QIcon(SELECT_ICON), "Select soft", self)
        self.select_soft_action.triggered.connect(self.select_soft)
        self.menu.addAction(self.select_soft_action)

        # update widgets
        set_soft_selection = QtWidgets.QPushButton(self)
        set_soft_selection.setFlat(True)
        set_soft_selection.setIcon(QtGui.QIcon(SOFT_SELECT_ICON))
        set_soft_selection.setIconSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        set_soft_selection.setFixedSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        set_soft_selection.released.connect(self.set_soft_from_selection)
        self.layout().insertWidget(1, set_soft_selection)

        self.soft_label = QtWidgets.QLabel(self)
        self.soft_label.setText("0 Component(s)")
        self.soft_label.setStyleSheet(INVALID_STYLESHEET)
        self.layout().addWidget(self.soft_label)

        remove = QtWidgets.QPushButton(self)
        remove.setFlat(True)
        remove.setIcon(QtGui.QIcon(REMOVE_ICON))
        remove.setIconSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        remove.setFixedSize(QtCore.QSize(22 * self.scale_factor, 22 * self.scale_factor))
        remove.released.connect(self.deleteLater)
        self.layout().addWidget(remove)

    # ------------------------------------------------------------------------

    def menu_about_to_show(self):
        super(InfluenceWidget, self).menu_about_to_show()
        state = not self.selection.isEmpty()
        self.select_soft_action.setEnabled(state)

    # ------------------------------------------------------------------------

    @gui.display_error
    def select_soft(self):
        OpenMaya.MGlobal.setActiveSelectionList(self.selection)
        OpenMaya.MGlobal.setRichSelection(self.soft_selection)

    @gui.display_error
    def set_soft_from_selection(self):
        """
        Query the current soft selection and store its selection, weighting
        and settings into the class.

        :raise RuntimeError: When no soft selection is made.
        :raise RuntimeError: When no vertex component selection is made.
        """
        try:
            rich_selection = OpenMaya.MGlobal.getRichSelection(defaultToActiveSelection=False)
        except RuntimeError:
            raise RuntimeError("Please make a vertex component soft selection.")

        selection = OpenMaya.MGlobal.getActiveSelectionList()
        for i in range(selection.length()):
            dag, component = selection.getComponent(i)
            if component.hasFn(OpenMaya.MFn.kMeshVertComponent):
                break
        else:
            raise RuntimeError("Please make a vertex component soft selection.")

        self.selection = selection
        self.soft_selection = rich_selection
        self.soft_selection_map = api.selection.get_rich_selection_mapping(rich_selection)
        self.soft_selection_changed.emit()

        length = sum([len(data) for data in self.soft_selection_map.values()])
        self.soft_label.setText("{} Component(s)".format(length))
        self.soft_label.setStyleSheet(None)


class SoftSelectionWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SoftSelectionWeightsWidget, self).__init__(parent)
        scale_factor = self.logicalDpiX() / 96.0

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(300 * scale_factor, 300 * scale_factor)

        # create layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create widgets
        add_influence = QtWidgets.QPushButton(self)
        add_influence.setFlat(True)
        add_influence.setIcon(QtGui.QIcon(ADD_ICON))
        add_influence.setIconSize(QtCore.QSize(22 * scale_factor, 22 * scale_factor))
        add_influence.setFixedSize(QtCore.QSize(22 * scale_factor, 22 * scale_factor))
        add_influence.released.connect(self.add_influence)
        layout.addWidget(add_influence, 0, 0)

        add_influence_label = QtWidgets.QLabel(self)
        add_influence_label.setText("Add influence")
        layout.addWidget(add_influence_label, 0, 1)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 1, 0, 1, 2)

        self.widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 5, 0)
        self.layout.setSpacing(5)

        self.filler = JointWidget(self)
        self.filler.joint_changed.connect(self.refresh)
        self.filler.setEnabled(False)
        self.filler.setToolTip(
            "If the source mesh is not skinned the filler "
            "influence will be used to fill missing weights."
        )
        self.layout.addWidget(self.filler)

        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setWidget(self.widget)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.scroll, 2, 0, 1, 2)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 3, 0, 1, 2)

        self.apply_button = QtWidgets.QPushButton(self)
        self.apply_button.setText("Apply")
        self.apply_button.setEnabled(False)
        self.apply_button.released.connect(self.apply)
        layout.addWidget(self.apply_button, 4, 0, 1, 2)

    # ------------------------------------------------------------------------

    @property
    def influences(self):
        """
        :return: Influences
        :rtype: list[InfluenceWidget]
        """
        return [
            self.layout.itemAt(i).widget()
            for i in range(self.layout.count() - 1)
            if isinstance(self.layout.itemAt(i).widget(), InfluenceWidget)
        ]

    def add_influence(self):
        """
        Create a new influence widget and connect the soft selection changed
        signal to refresh the UI and update the filler enabled state.
        """
        widget = InfluenceWidget(self)
        widget.joint_changed.connect(self.refresh)
        widget.soft_selection_changed.connect(self.refresh)

        num = self.layout.count() - 2
        self.layout.insertWidget(num, widget)
        self.refresh()

    # ------------------------------------------------------------------------

    def set_weights(self, geometry, joints, weights):
        """
        :param str geometry:
        :param list[str] joints:
        :param dict weights:
        :raise RuntimeError: When mesh doesn't exist.
        :raise RuntimeError: When joint doesn't exist.
        """
        # validate creation
        if not cmds.objExists(geometry):
            raise RuntimeError("Unable to set soft weights, "
                               "geometry '{}' doesn't exist.".format(geometry))
        for joint in joints:
            if not cmds.objExists(joint):
                raise RuntimeError("Unable to set soft weights on geometry '{}', "
                                   "joint '{}' doesn't exist.".format(geometry, joint))

        # get skin cluster
        try:
            skin_cluster = skin.get_cluster(geometry)
        except RuntimeError:
            if not cmds.objExists(self.filler.joint):
                raise RuntimeError("Unable to set soft weights on geometry '{}', "
                                   "filler joint '{}' doesn't exist.".format(geometry, self.filler.joint))

            parent = cmds.listRelatives(geometry, parent=True)[0]
            skin_cluster_name = "{}_SK".format(naming.get_leaf_name(parent))
            skin_cluster = cmds.skinCluster(
                self.filler.joint,
                geometry,
                name=skin_cluster_name,
                toSelectedBones=True,
                removeUnusedInfluence=False,
                maximumInfluences=4,
                obeyMaxInfluences=False,
                bindMethod=0,
                skinMethod=0,  # linear
                normalizeWeights=1,  # interactive
                weightDistribution=0,  # distance
            )[0]

        # process skin cluster
        skin_cluster_obj = api.conversion.get_object(skin_cluster)
        skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)
        normalize = skin_cluster_fn.findPlug("normalizeWeights", False).asInt()
        max_influences = skin_cluster_fn.findPlug("maxInfluences", False).asInt()
        maintain_max_influences = skin_cluster_fn.findPlug("maintainMaxInfluences", False).asBool()

        # process influences
        locked_influences = {}
        indexed_influences = {}
        influence.add_influences(skin_cluster, joints)

        # store index and locked influences, any joints that are provided to
        # this function will ignore its locked state as they will have updated
        # weights.
        for i, influence_dag in enumerate(skin_cluster_fn.influenceObjects()):
            indexed_influences[influence_dag.partialPathName()] = i
            influence_dep = OpenMaya.MFnDependencyNode(influence_dag.node())
            if influence_dep.hasAttribute("liw"):
                locked_influences[i] = influence_dep.findPlug("liw", False).asBool()
            else:
                locked_influences[i] = False

        for joint in joints:
            index = indexed_influences[joint]
            locked_influences[index] = False

        num_influences = len(indexed_influences)

        # get elements
        elements = list(weights.keys())
        elements.sort()

        component_fn = OpenMaya.MFnSingleIndexedComponent()
        component = component_fn.create(OpenMaya.MFn.kMeshVertComponent)
        component_fn.addElements(elements)

        # get weights
        dag = api.conversion.get_dag(geometry)
        weights_old, _ = skin_cluster_fn.getWeights(dag, component)

        weights_split = list(weights_old)
        weights_split = conversion.as_chunks(weights_split, num_influences)

        # calculate new weights
        weights_new = OpenMaya.MDoubleArray()
        influences = OpenMaya.MIntArray(range(num_influences))

        for element, weights_array in zip(elements, weights_split):
            blend_total = sum(list(weights[element].values()))
            current_total = sum(weights_array)
            locked_total = sum([weight for i, weight in enumerate(weights_array) if locked_influences[i]])

            # scale down the new weights in the event that the free weights
            # are greater than the new weights that need to be applied.
            if blend_total > current_total - locked_total:
                factor = max([0, (current_total - locked_total) / blend_total])
                for joint, weight in weights[element].items():
                    weights[element][joint] = weight * factor

            # scale down the non-locked weights so there is room for the new
            # weights to be applied.
            factor = 0
            blend_total = sum(list(weights[element].values()))
            free_total = current_total - blend_total - locked_total

            if blend_total > 0 and locked_total < current_total:
                factor = free_total / (current_total - locked_total)

            for index, weight in enumerate(weights_array):
                if not locked_influences[index]:
                    weights_array[index] = weight * factor

            # add the newly desired weights to indices which will add up to
            # match the total calculated previously.
            for joint, weight in weights[element].items():
                index = indexed_influences[joint]
                weights_array[index] += weight

            if maintain_max_influences:
                weights_sorted = zip(range(num_influences), locked_influences.values(), weights_array)
                weights_excess = sorted(weights_sorted, key=lambda x: (-x[1], -x[2]))[max_influences:]
                for i, locked, weight in weights_excess:
                    if locked and weight:
                        log.warning("Unable to maintain max influences due to locked weights.")
                        continue

                    weights_array[i] = 0.0

            if normalize == 1:
                factor = 0
                blend_total = sum(weights_array) - locked_total

                if blend_total > 0 and locked_total < 1.0:
                    factor = (1.0 - locked_total) / blend_total

                for i, weight in enumerate(weights_array):
                    if not locked_influences[i]:
                        weights_array[i] = weight * factor

            for weight in weights_array:
                weights_new.append(weight)

        skin.set_weights(
            skin_cluster_fn,
            dag=dag,
            components=component,
            influences=influences,
            weights_old=weights_old,
            weights_new=weights_new
        )

        log.info("Successfully set soft weights for '{}'.".format(geometry))

    # ------------------------------------------------------------------------

    @gui.display_error
    def apply(self):
        """
        Combine all of the soft selection data of all of the influences and
        group them per mesh. The set weights command is called for each of
        the meshes separately.

        :raise RuntimeError: When mesh doesn't exist.
        :raise RuntimeError: When joint doesn't exist.
        """
        with gui.WaitCursor():
            data = {}
            joints = set()

            for inf in self.influences:
                joints.add(inf.joint)

                for geometry, weights in inf.soft_selection_map.items():
                    if geometry not in data:
                        data[geometry] = {}

                    for index, weight in weights.items():
                        if index not in data[geometry]:
                            data[geometry][index] = {}

                        if inf.joint not in data[geometry][index]:
                            data[geometry][index][inf.joint] = 0

                        data[geometry][index][inf.joint] += weight

            with undo.UndoChunk():
                for mesh, weights in data.items():
                    self.set_weights(mesh, list(joints), weights)

    def refresh(self):
        """
        Loop over all the influences and see if any of the soft selections
        saved contains a link to a non-skinned mesh. If that is the case the
        filler will be enabled.
        """
        self.apply_button.setEnabled(bool(len(self.influences)))
        self.filler.setEnabled(False)

        for inf in self.influences:
            if inf.joint is None or not inf.soft_selection_map:
                self.apply_button.setEnabled(False)

            for mesh in inf.soft_selection_map.keys():
                try:
                    skin.get_cluster_fn(mesh)
                except RuntimeError:
                    self.filler.setEnabled(True)

        if self.filler.isEnabled() and self.filler.joint is None:
            self.apply_button.setEnabled(False)


def show():
    parent = gui.get_main_window()
    widget = SoftSelectionWeightsWidget(parent)
    widget.show()
