from PySide2 import QtWidgets, QtGui, QtCore

from skinning.gui import icon


__all__ = [
    "SearchWidget"
]

CLOSE_ICON = icon.get_icon_file_path("nodeGrapherClose.png")


class SearchWidget(QtWidgets.QWidget):
    """
    The search widget is a line edit that will trigger both a text changed and
    a return pressed signal with the string of the line edit. When creating
    the widget a place holder text can be provided. A clear button gets
    created to remove any text in the line edit. This will trigger the text
    changed signal as well.
    """
    text_changed = QtCore.Signal(str)
    return_pressed = QtCore.Signal(str)

    def __init__(self, parent, placeholder_text="search ..."):
        super(SearchWidget, self).__init__(parent)

        # create layout
        scale_factor = self.logicalDpiX() / 96.0
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText(placeholder_text)
        self.line_edit.textChanged.connect(self.text_changed.emit)
        self.line_edit.returnPressed.connect(self._emit_return_pressed)
        layout.addWidget(self.line_edit)

        # create button
        button = QtWidgets.QPushButton(self)
        button.setFixedSize(QtCore.QSize(22 * scale_factor, 22 * scale_factor))
        button.setFlat(True)
        button.setIcon(QtGui.QIcon(CLOSE_ICON))
        button.released.connect(self.line_edit.clear)
        layout.addWidget(button)

    def _emit_return_pressed(self):
        self.return_pressed.emit(self.line_edit.text())
