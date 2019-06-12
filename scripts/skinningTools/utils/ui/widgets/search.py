from .. import Qt
from .. import FONT


__all__ = [
    "Search"
]

REMOVE_ICON = ":/setEdRemoveCmd.png"


class Search(Qt.QWidget):
    searchChanged = Qt.Signal(str)

    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # search field
        self.le = Qt.QLineEdit(self)
        self.le.setFont(FONT)
        self.le.setPlaceholderText("search...")
        self.le.textChanged.connect(self.searchChanged.emit)
        layout.addWidget(self.le)

        # clear button
        button = Qt.QPushButton(self)
        button.setFlat(True)
        button.setIcon(Qt.QIcon(REMOVE_ICON))
        button.setFixedSize(Qt.QSize(18, 18))
        button.released.connect(self.clear)
        layout.addWidget(button)

    # ------------------------------------------------------------------------

    @property
    def text(self):
        """
        :return: Text
        :rtype: str
        """
        return self.le.text()

    # ------------------------------------------------------------------------

    def clear(self):
        self.le.setText(None)
