from .. import Qt, font


__all__ = [
    "LabelButton",
    "LabelCheckbox",
    "LabelSpinBox"
]


class LabelCore(Qt.QWidget):
    def __init__(self, parent, label=""):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create label
        self._label = Qt.QLabel(self)
        self._label.setFont(font.FONT)
        self._label.setText(label)
        layout.addWidget(self._label)

    # ------------------------------------------------------------------------

    def setLabelText(self, text):
        """
        :param str text:
        """
        self._label.setText(text)


class LabelButton(LabelCore):
    released = Qt.Signal()

    def __init__(self, parent, label="", button=""):
        LabelCore.__init__(self, parent, label)

        # create button
        self._button = Qt.QPushButton(self)
        self._button.setFont(font.FONT)
        self._button.setText(button)
        self._button.released.connect(self.released.emit)
        self.layout().addWidget(self._button)

    # ------------------------------------------------------------------------

    def setButtonText(self, text):
        """
        :param str text:
        """
        self._button.setText(text)


class LabelCheckbox(LabelCore):
    stateChanged = Qt.Signal(int)

    def __init__(self, parent, label=""):
        LabelCore.__init__(self, parent, label)

        # create checkbox
        self._checkbox = Qt.QCheckBox(self)
        self._checkbox.setFixedHeight(18)
        self._checkbox.stateChanged.connect(self.stateChanged.emit)
        self.layout().addWidget(self._checkbox)

    # ------------------------------------------------------------------------

    def isChecked(self):
        """
        :return: Checked state
        :rtype: bool
        """
        return self._checkbox.isChecked()

    def setChecked(self, state):
        """
        :param bool state:
        """
        self._checkbox.setChecked(state)


class LabelSpinBox(LabelCore):
    def __init__(self, parent, label="", double=True, value=0, step=1, minValue=0, maxValue=1):
        LabelCore.__init__(self, parent, label)

        # get spin box widget
        widget = Qt.QDoubleSpinBox if double else Qt.QSpinBox

        # create spin box widget
        self._spinbox = widget(self)
        self._spinbox.setFont(font.FONT)
        self._spinbox.setValue(value)
        self._spinbox.setSingleStep(step)
        self._spinbox.setMinimum(minValue)
        self._spinbox.setMaximum(maxValue)
        self.layout().addWidget(self._spinbox)

    # ------------------------------------------------------------------------

    def value(self):
        """
        :return: Value
        :rtype: int/float
        """
        return self._spinbox.value()

    def setValue(self, value):
        """
        :param int/float value:
        """
        self._spinbox.setValue(value)
