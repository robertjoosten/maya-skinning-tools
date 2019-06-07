from .. import Qt


__all__ = [
    "Divider"
]


class Divider(Qt.QFrame):
    def __init__(self, parent):
        Qt.QFrame.__init__(self, parent)
        self.setFrameShape(Qt.QFrame.HLine)
        self.setFrameShadow(Qt.QFrame.Sunken)
