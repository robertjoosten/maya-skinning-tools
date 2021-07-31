import logging
from maya import cmds
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtGui, QtCore
from functools import partial

from skinning import gui
from skinning.utils import skin


log = logging.getLogger(__name__)

WINDOW_TITLE = "Tweak Weights"
WINDOW_ICON = gui.get_icon_file_path("ST_tweakWeights.png")
LOCK_ON_ICON = gui.get_icon_file_path("Lock_ON.png")
LOCK_OFF_ICON = gui.get_icon_file_path("Lock_OFF.png")
LOCK_ICONS = {True: LOCK_ON_ICON, False: LOCK_OFF_ICON}

HEADER = "QLabel{color: orange; font-weight: bold}"
DISPLAY_MAXIMUM = 10


class InfluenceWidget(QtWidgets.QWidget):
    weight_changed = QtCore.Signal(float)

    def __init__(self, parent, influence, weight):
        super(InfluenceWidget, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.influence = influence
        self.weight = weight

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create widgets
        self.lock = QtWidgets.QPushButton(self)
        self.lock.setFlat(True)
        self.lock.setCheckable(True)
        self.lock.setFixedSize(QtCore.QSize(18 * scale_factor, 18 * scale_factor))
        self.lock.setIcon(QtGui.QIcon(LOCK_ICONS[self.is_locked_in_scene()]))
        self.lock.setChecked(self.is_locked_in_scene())
        self.lock.released.connect(self.refresh)
        layout.addWidget(self.lock)

        label = QtWidgets.QLabel(self)
        label.setText(influence)
        label.setFixedWidth(150 * scale_factor)
        layout.addWidget(label)

        self.slider = QtWidgets.QSlider(self)
        self.slider.setInputMethodHints(QtCore.Qt.ImhNone)
        self.slider.setMaximum(1000)
        self.slider.setSingleStep(1)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self._emit_weight_changed)
        layout.addWidget(self.slider)

        self.spinbox = QtWidgets.QDoubleSpinBox(self)
        self.spinbox.setDecimals(3)
        self.spinbox.setRange(0, 1)
        self.spinbox.setSingleStep(0.001)
        self.spinbox.setFixedWidth(60 * scale_factor)
        self.spinbox.valueChanged.connect(self._emit_weight_changed)
        layout.addWidget(self.spinbox)

        self.refresh()

    def _emit_weight_changed(self, value):
        if isinstance(value, int):
            value = value / 1000.0

        self.weight_changed.emit(value)

    # ------------------------------------------------------------------------

    def is_locked(self):
        """
        :return: Locked state
        :rtype: bool
        """
        return self.lock.isChecked()

    def is_locked_in_scene(self):
        """
        :return: Locked state in scene
        :rtype: bool
        """
        if cmds.attributeQuery("liw", node=self.influence, exists=True):
            return cmds.getAttr("{}.liw".format(self.influence))

        return False

    # ------------------------------------------------------------------------

    def set_weight(self, weight):
        """
        Block the signals of the slider and spinbox and set the values to the
        desired weight.

        :param float weight:
        """
        with gui.BlockSignals(self.slider, self.spinbox):
            self.slider.setValue(int(weight * 1000))
            self.spinbox.setValue(weight)

        self.weight = weight

    # ------------------------------------------------------------------------

    def refresh(self):
        """
        Update the widget locking slider and spin box if the influence is
        locked but also set the weight using the value stored internally.
        """
        self.slider.setEnabled(not self.is_locked())
        self.spinbox.setEnabled(not self.is_locked())
        self.set_weight(self.weight)


class ComponentWidget(QtWidgets.QWidget):
    def __init__(self, parent, dag, component_fn, skin_cluster_fn):
        super(ComponentWidget, self).__init__(parent)

        self.dag = dag
        self.influences = {}
        self.component = component_fn.object()
        self.component_fn = component_fn
        self.skin_cluster_fn = skin_cluster_fn

        self.num_influences = len(self.skin_cluster_fn.influenceObjects())
        self.normalize = self.skin_cluster_fn.findPlug("normalizeWeights", False).asInt()
        self.max_influences = self.skin_cluster_fn.findPlug("maxInfluences", False).asInt()
        self.maintain_max_influences = self.skin_cluster_fn.findPlug("maintainMaxInfluences", False).asBool()

        selection = OpenMaya.MSelectionList()
        selection.add((self.dag, self.component), mergeWithExisting=True)

        # create layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create widgets
        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 0, 0, 1, 2)

        label = QtWidgets.QLabel(self)
        label.setStyleSheet(HEADER)
        label.setText(selection.getSelectionStrings()[0])
        layout.addWidget(label, 1, 0)

        self.display = QtWidgets.QCheckBox(self)
        self.display.setText("Display all influences")
        self.display.stateChanged.connect(self.refresh)
        layout.addWidget(self.display, 1, 1, 1, 1, QtCore.Qt.AlignRight)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 2, 0, 1, 2)

        # create influences
        influences = [influence.partialPathName() for influence in self.skin_cluster_fn.influenceObjects()]
        weights, _ = self.skin_cluster_fn.getWeights(self.dag, self.component)
        for i, (influence, index, weight) in enumerate(sorted(zip(influences, range(len(weights)), weights)), 3):
            influence = InfluenceWidget(self, influence, weight)
            influence.weight_changed.connect(partial(self.set_weights, index))

            layout.addWidget(influence, i, 0, 1, 2)
            self.influences[index] = influence

        self.refresh()

    # ------------------------------------------------------------------------

    def set_weights(self, index, weight):
        """
        Calculate new weights and update all of the weight widgets with the
        newly calculated weights using the index and weight value.

        :param int index:
        :param float weight:
        """
        weights = [0.0] * self.num_influences
        locked_influences = [False] * self.num_influences

        for i, widget in self.influences.items():
            if i == index:
                weights[i] = weight
                locked_influences[i] = True
            else:
                weights[i] = widget.weight
                locked_influences[i] = widget.is_locked()

        if self.maintain_max_influences:
            weights_sorted = zip(range(self.num_influences), locked_influences, weights)
            weights_excess = sorted(weights_sorted, key=lambda x: (-x[1], -x[2]))[self.max_influences:]
            for i, locked, weight in weights_excess:
                if locked and weight:
                    log.warning("Unable to maintain max influences due to locked weights.")
                    continue

                weights[i] = 0.0

        if self.normalize == 1:
            locked_total = sum([weight for i, weight in enumerate(weights) if locked_influences[i]])
            blend_total = sum(weights) - locked_total

            if blend_total <= 0.0:
                raise RuntimeError("Unable to normalize weights, "
                                   "no influences weights are allowed to change.")

            factor = 0 if locked_total >= 1.0 else (1.0 - locked_total) / blend_total

            for i, weight in enumerate(weights):
                if not locked_influences[i]:
                    weights[i] = weight * factor

        for i, weight in enumerate(weights):
            self.influences[i].set_weight(weight)

        skin.set_weights(
            self.skin_cluster_fn,
            self.dag,
            self.component,
            OpenMaya.MIntArray(range(self.num_influences)),
            OpenMaya.MDoubleArray(weights),
        )

        self.refresh()

    def refresh(self):
        """
        Display either the influence with non-zero values or all influences
        depending on the display state.
        """
        for influence in self.influences.values():
            state = True if self.display.isChecked() else influence.weight > 0.0
            influence.setVisible(state)


class TweaksWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(TweaksWeightsWidget, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.callback = None

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(550 * scale_factor, 350 * scale_factor)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setWidget(self.widget)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.scroll)

        self.register_callback()
        self.refresh()

    # ------------------------------------------------------------------------

    def register_callback(self):
        """
        Register a callback to run the update function every time the
        selection list is modified.
        """
        self.callback = OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified,
            self.refresh
        )

    def remove_callback(self):
        """
        Remove the callback that updates the ui every time the selection
        list is modified.
        """
        if self.callback is not None:
            OpenMaya.MMessage.removeCallback(self.callback)

    # ------------------------------------------------------------------------

    def closeEvent(self, event):
        """
        Subclass the closeEvent function to first remove the callback,
        this callback shouldn't be floating around and should be deleted
        with the widget.
        """
        self.remove_callback()
        super(TweaksWeightsWidget, self).closeEvent(event)

    # ------------------------------------------------------------------------

    def refresh(self, *args):
        """
        Query the current selection and populate the widget with the component
        weight information. When the selection made is not valid rather than
        raising an error the window will simply not be populated.
        """
        gui.clear_layout(self.layout)

        # validate selection
        selection = OpenMaya.MGlobal.getActiveSelectionList()
        if selection.isEmpty():
            return

        # validate component
        dag, component = selection.getComponent(0)
        node_name = dag.partialPathName()
        if component.isNull():
            return

        # validate component type
        if component.hasFn(OpenMaya.MFn.kMeshVertComponent):
            indexed_component = OpenMaya.MFnSingleIndexedComponent
            geometry_component = OpenMaya.MFn.kMeshVertComponent
        elif component.hasFn(OpenMaya.MFn.kCurveCVComponent):
            indexed_component = OpenMaya.MFnDoubleIndexedComponent
            geometry_component = OpenMaya.MFn.kCurveCVComponent
        elif component.hasFn(OpenMaya.MFn.kSurfaceCVComponent):
            indexed_component = OpenMaya.MFnDoubleIndexedComponent
            geometry_component = OpenMaya.MFn.kSurfaceCVComponent
        else:
            return

        # validate skin cluster
        try:
            skin_cluster_fn = skin.get_cluster_fn(node_name)
        except RuntimeError:
            return

        # add component widgets
        component_fn = indexed_component(component)
        for element in component_fn.getElements()[:DISPLAY_MAXIMUM]:
            component_single_fn = indexed_component()
            component_single_fn.create(geometry_component)
            component_single_fn.addElement(element)

            widget = ComponentWidget(self, dag, component_single_fn, skin_cluster_fn)
            self.layout.addWidget(widget)

        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(spacer)


def show():
    parent = gui.get_main_window()
    widget = TweaksWeightsWidget(parent)
    widget.show()
