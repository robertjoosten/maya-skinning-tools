from maya import cmds
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import api
from skinning.utils import undo
from skinning.tools.initialize_weights import commands


WINDOW_TITLE = "Initialize Weights"
WINDOW_ICON = gui.get_icon_file_path("ST_initializeWeights.png")


class InitializeWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(InitializeWeightsWidget, self).__init__(parent)

        self.geometry = []
        self.joints = []

        scale_factor = self.logicalDpiX() / 96.0
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(400 * scale_factor, 25 * scale_factor)

        # create layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create selection widgets
        self.geometry_status = QtWidgets.QLabel(self)
        geometry_button = QtWidgets.QPushButton(self)
        geometry_button.setText("Select mesh(es)")
        layout.addWidget(self.geometry_status, 0, 0)
        layout.addWidget(geometry_button, 0, 1)

        self.joints_status = QtWidgets.QLabel(self)
        joints_button = QtWidgets.QPushButton(self)
        joints_button.setText("Select joint(s)")
        layout.addWidget(self.joints_status, 1, 0)
        layout.addWidget(joints_button, 1, 1)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 2, 0, 1, 2)

        # create smooth widgets
        iterations_label = QtWidgets.QLabel(self)
        iterations_label.setText("Smoothing iterations:")
        self.iterations = QtWidgets.QSpinBox(self)
        self.iterations.setValue(3)
        self.iterations.setRange(0, 25)
        layout.addWidget(iterations_label, 3, 0)
        layout.addWidget(self.iterations, 3, 1)

        projection_label = QtWidgets.QLabel(self)
        projection_label.setText("Projection:")
        self.projection = QtWidgets.QDoubleSpinBox(self)
        self.projection.setValue(0.75)
        self.projection.setRange(0, 1)
        self.projection.setSingleStep(0.05)
        layout.addWidget(projection_label, 4, 0)
        layout.addWidget(self.projection, 4, 1)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 5, 0, 1, 2)

        # create weights widget
        blend_weights_label = QtWidgets.QLabel(self)
        blend_weights_label.setText("Blend weights:")
        self.blend_weights = QtWidgets.QCheckBox(self)
        layout.addWidget(blend_weights_label, 6, 0)
        layout.addWidget(self.blend_weights, 6, 1)

        delinear_label = QtWidgets.QLabel(self)
        delinear_label.setText("De-linearize weights:")
        self.delinear_weights = QtWidgets.QCheckBox(self)
        layout.addWidget(delinear_label, 7, 0)
        layout.addWidget(self.delinear_weights, 7, 1)

        delinear_method_label = QtWidgets.QLabel(self)
        delinear_method_label.setText("De-linearize method:")
        self.delinear_method = gui.widgets.EasingWidget(self)
        layout.addWidget(delinear_method_label, 8, 0)
        layout.addWidget(self.delinear_method, 8, 1)

        div = gui.widgets.DividerWidget(self)
        layout.addWidget(div, 9, 0, 1, 2)

        # create apply button
        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply")
        layout.addWidget(apply_button, 10, 0, 1, 2)

        # connect signals
        geometry_button.released.connect(self.set_selected_geometry)
        joints_button.released.connect(self.set_selected_joints)
        self.blend_weights.stateChanged.connect(self.reset)
        self.delinear_weights.stateChanged.connect(self.reset)
        apply_button.released.connect(self.apply)

        self.reset()

    # ------------------------------------------------------------------------

    def set_selected_geometry(self):
        """
        Add the currently selected geometry to the geometry variable and call
        the reset method to update the ui with this information.

        :raise RuntimeError: When selected object is not a mesh.
        """
        self.geometry = []
        active_selection = OpenMaya.MGlobal.getActiveSelectionList()
        for i in range(active_selection.length()):
            dag, component = active_selection.getComponent(i)
            if component.isNull():
                if dag.hasFn(OpenMaya.MFn.kTransform):
                    dag.extendToShape()
                dag, component = api.conversion.get_component(dag.fullPathName())

            if not dag.hasFn(OpenMaya.MFn.kMesh):
                raise RuntimeError("Unable to add node '{}' to as geometry, "
                                   "it is not a mesh.".format(dag.partialPathName()))

            selection = OpenMaya.MSelectionList()
            selection.add((dag, component))

            components = cmds.ls(selection.getSelectionStrings(), flatten=True)
            self.geometry.append((dag.partialPathName(), components))

        self.reset()

    def set_selected_joints(self):
        """
        Add the currently selected joints to the joints variable and call
        the reset method to update the ui with this information.
        """
        self.joints = cmds.ls(selection=True, type="joint") or []
        self.reset()

    # ------------------------------------------------------------------------

    @gui.display_error
    def apply(self):
        """
        Loop over all shapes and components and call the set initial weights
        command using the settings read from the ui.
        """
        with gui.WaitCursor():
            with undo.UndoChunk():
                iterations = self.iterations.value()
                projection = self.projection.value()
                blend = self.blend_weights.isChecked()
                blend_method = self.delinear_method.currentText() \
                    if self.delinear_weights.isChecked() \
                    else None

                for shape, components in self.geometry:
                    commands.initialize_weights(
                        shape,
                        self.joints,
                        components=components,
                        iterations=iterations,
                        projection=projection,
                        blend=blend,
                        blend_method=blend_method
                    )

    def reset(self):
        """
        Update the ui with the currently stored geometry and joint
        information. Also update the enabled and checked state of the
        blend weights widgets based on the settings.
        """
        num_meshes = 0
        num_components = 0

        for shape, components in self.geometry:
            num_meshes += 1
            num_components += len(components)

        self.geometry_status.setText("{} Mesh(es) with {} Component(s)".format(num_meshes, num_components))
        self.joints_status.setText("{} Joint(s)".format(len(self.joints)))

        with gui.BlockSignals(self.delinear_weights, self.delinear_method):
            blend_checked = self.blend_weights.isChecked()
            delinear_checked = self.delinear_weights.isChecked()

            if blend_checked and delinear_checked:
                self.delinear_weights.setEnabled(True)
                self.delinear_method.setEnabled(True)
            elif blend_checked:
                self.delinear_weights.setEnabled(True)
                self.delinear_method.setEnabled(False)
            else:
                self.delinear_weights.setChecked(False)
                self.delinear_weights.setEnabled(False)
                self.delinear_method.setEnabled(False)


def show():
    parent = gui.get_main_window()
    widget = InitializeWeightsWidget(parent)
    widget.show()
