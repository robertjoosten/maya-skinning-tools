from maya import cmds
from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import undo
from skinning.tools.projection_plane import commands


WINDOW_TITLE = "Projection Plane"
WINDOW_ICON = gui.get_icon_file_path("ST_projectionPlane.png")


class ProjectionPlaneWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ProjectionPlaneWidget, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(400 * scale_factor, 25 * scale_factor)

        # create layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create widgets
        axis_label = QtWidgets.QLabel(self)
        axis_label.setText("Axis:")
        axis_label.setToolTip("Axis on which the plane will be aligned.")
        self.axis = QtWidgets.QComboBox(self)
        self.axis.addItems(["x", "y", "z"])
        self.axis.setCurrentIndex(2)
        layout.addWidget(axis_label, 0, 0)
        layout.addWidget(self.axis, 0, 1)

        width_label = QtWidgets.QLabel(self)
        width_label.setText("Width:")
        width_label.setToolTip("Width of the plane.")
        self.width = QtWidgets.QDoubleSpinBox(self)
        self.width.setRange(0.1, 1000)
        self.width.setValue(25)
        layout.addWidget(width_label, 1, 0)
        layout.addWidget(self.width, 1, 1)

        padding_label = QtWidgets.QLabel(self)
        padding_label.setText("Padding:")
        padding_label.setToolTip("Padding of the rotational matrices to help average out the rotations.")
        self.padding = QtWidgets.QSpinBox(self)
        self.padding.setRange(0, 100)
        layout.addWidget(padding_label, 2, 0)
        layout.addWidget(self.padding, 2, 1)

        offset_label = QtWidgets.QLabel(self)
        offset_label.setText("Offset:")
        offset_label.setToolTip("Offset the skinning by adjusting the mapped influence.")
        self.offset = QtWidgets.QSpinBox(self)
        self.offset.setRange(-100, 100)
        layout.addWidget(offset_label, 3, 0)
        layout.addWidget(self.offset, 3, 1)

        # create divider
        divider = gui.widgets.DividerWidget(self)
        layout.addWidget(divider, 4, 0, 1, 2)
        
        # create button
        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply")
        apply_button.released.connect(self.apply)
        layout.addWidget(apply_button, 5, 0, 1, 2)

    @gui.display_error
    def apply(self):
        """
        raise RuntimeError: When no joints are selected
        """
        joints = cmds.ls(selection=True, type="joint")
        if not joints:
            raise RuntimeError("Unable to create projection plane, no joints selected.")

        with undo.UndoChunk():
            commands.create_projection_plane(
                joints,
                axis=self.axis.currentText(),
                width=self.width.value(),
                padding=self.padding.value(),
                offset=self.offset.value()
            )


def show():
    parent = gui.get_main_window()
    widget = ProjectionPlaneWidget(parent)
    widget.show()
