from PySide2 import QtWidgets

from skinning.utils import math


__all__ = [
    "EasingWidget"
]


class EasingWidget(QtWidgets.QComboBox):
    def __init__(self, parent):
        super(EasingWidget, self).__init__(parent)

        methods = [method for method in dir(math.ease) if method.startswith("ease")]
        methods.sort()

        self.addItems(methods)
