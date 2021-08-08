from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import undo
from skinning.tools.delinear_weights import commands


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
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create tweening
        delinear_method_label = QtWidgets.QLabel(self)
        delinear_method_label.setText("De-linearize method:")
        self.delinear_method = gui.widgets.EasingWidget(self)
        layout.addWidget(delinear_method_label, 0, 0)
        layout.addWidget(self.delinear_method, 0, 1)

        # create divider
        divider = gui.widgets.DividerWidget(self)
        layout.addWidget(divider, 1, 0, 1, 2)
        
        # create button
        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply")
        apply_button.released.connect(self.apply)
        layout.addWidget(apply_button, 2, 0, 1, 2)

    @gui.display_error
    def apply(self):
        with gui.WaitCursor():
            with undo.UndoChunk():
                method = self.delinear_method.currentText()
                commands.delinear_weights_on_selection(method)


def show():
    parent = gui.get_main_window()
    widget = DelinearWeightsWidget(parent)
    widget.show()
