from .. import Qt, font


__all__ = [
    "LabelButton",
    "LabelSpinBox"
]


class LabelButton(Qt.QWidget):
    released = Qt.Signal()

    def __init__(self, parent, label="", button=""):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create label
        self.label = Qt.QLabel(self)
        self.label.setFont(font.FONT)
        self.label.setText(label)
        layout.addWidget(self.label)

        # create button
        self.button = Qt.QPushButton(self)
        self.button.setFont(font.FONT)
        self.button.setText(button)
        layout.addWidget(self.button)


class LabelSpinBox(Qt.QWidget):
    released = Qt.Signal()

    def __init__(self, parent, label="", double=True, value=0, minValue=0, maxValue=1):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create label
        self.label = Qt.QLabel(self)
        self.label.setFont(font.FONT)
        self.label.setText(label)
        layout.addWidget(self.label)

        # get spin box widget
        widget = Qt.QDoubleSpinBox if double else Qt.QSpinBox

        # create spin box widget
        self.spinBox = widget(self)
        self.spinBox.setFont(font.FONT)
        self.spinBox.setValue(value)
        self.spinBox.setMinimum(minValue)
        self.spinBox.setMaximum(maxValue)
        layout.addWidget(self.spinBox)
