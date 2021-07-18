from PySide2 import QtWidgets

from skinning_tools.utils import math


__all__ = [
    "TweeningWidget"
]


class TweeningWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(TweeningWidget, self).__init__(parent)

        # get methods
        methods = [method for method in dir(math.tweening) if method.startswith("ease")]
        methods.sort()

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create widgets
        label = QtWidgets.QLabel(self)
        label.setText("De-Linearize Method:")
        layout.addWidget(label)

        # create option box
        self.combo = QtWidgets.QComboBox(self)
        self.combo.addItems(methods)
        layout.addWidget(self.combo)
