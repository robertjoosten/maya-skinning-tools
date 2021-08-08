from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import undo
from skinning.tools.mirror_weights import commands


WINDOW_TITLE = "Mirror Weights"
WINDOW_ICON = gui.get_icon_file_path("ST_mirrorWeights.png")


class MirrorWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MirrorWeightsWidget, self).__init__(parent)

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
        left_label = QtWidgets.QLabel(self)
        left_label.setText("Left:")
        left_label.setFixedWidth(75 * scale_factor)
        self.left = QtWidgets.QLineEdit(self)
        self.left.setPlaceholderText("L")
        layout.addWidget(left_label, 0, 0)
        layout.addWidget(self.left, 0, 1)

        right_label = QtWidgets.QLabel(self)
        right_label.setText("Right:")
        right_label.setFixedWidth(75 * scale_factor)
        self.right = QtWidgets.QLineEdit(self)
        self.right.setPlaceholderText("R")
        layout.addWidget(right_label, 1, 0)
        layout.addWidget(self.right, 1, 1)

        self.inverse = QtWidgets.QCheckBox(self)
        self.inverse.setText("Positive to negative (+X to -X)")
        self.inverse.setChecked(True)
        layout.addWidget(self.inverse, 2, 1)

        divider = gui.widgets.DividerWidget(self)
        layout.addWidget(divider, 3, 0, 1, 2)

        mirror = QtWidgets.QPushButton(self)
        mirror.setText("Mirror")
        mirror.released.connect(self.apply)
        layout.addWidget(mirror, 4, 0, 1, 2)

    @gui.display_error
    def apply(self):
        with gui.WaitCursor():
            left = self.left.text() or self.left.placeholderText()
            right = self.right.text() or self.right.placeholderText()
            inverse = not self.inverse.isChecked()

            with undo.UndoChunk():
                commands.mirror_weights_on_selection(inverse=inverse, replace=(left, right))


def show():
    parent = gui.get_main_window()
    widget = MirrorWeightsWidget(parent)
    widget.show()
