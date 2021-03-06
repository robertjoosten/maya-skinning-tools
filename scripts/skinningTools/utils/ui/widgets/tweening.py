from .. import Qt, font
from ... import tweening


__all__ = [
    "TweeningOptions"
]


class TweeningOptions(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create label
        label = Qt.QLabel(self)
        label.setFont(font.FONT)
        label.setText("De-Linearize Method:")
        layout.addWidget(label)

        # create option box
        options = tweening.getTweeningMethods()
        self.combo = Qt.QComboBox(self)
        self.combo.setFont(font.FONT)
        self.combo.addItems(options)
        layout.addWidget(self.combo)

    # ------------------------------------------------------------------------

    def currentMethod(self):
        """
        :return: Tweening method
        :rtype: str
        """
        return self.combo.currentText()
