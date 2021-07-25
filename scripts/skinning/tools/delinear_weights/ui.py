from PySide2 import QtWidgets, QtGui, QtCore

from skinning.tools.delinear_weights import commands
from skinning import gui
from skinning.utils import undo


WINDOW_TITLE = "De-Linearize Weights"
WINDOW_ICON = gui.get_icon_file_path("ST_delinearWeights.png")


class DelinearWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(DelinearWeightsWidget, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(400 * scale_factor, 25 * scale_factor)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create tweening
        self.tween = gui.widgets.TweeningWidget(self)
        layout.addWidget(self.tween)

        # create divider
        divider = gui.widgets.DividerWidget(self)
        layout.addWidget(divider)
        
        # create button
        apply = QtWidgets.QPushButton(self)
        apply.setText("Apply")
        apply.released.connect(self.apply)
        layout.addWidget(apply)

    @gui.display_error
    def apply(self):
        with undo.UndoChunk():
            method = self.tween.combo.currentText()
            commands.delinear_skin_weights_on_selection(method)


def show():
    parent = gui.get_main_window()
    widget = DelinearWeightsWidget(parent)
    widget.show()