from maya import cmds
from PySide2 import QtWidgets, QtGui, QtCore

from skinning import gui
from skinning.utils import skin
from skinning.tools.remove_weights_context import commands


WINDOW_TITLE = "Remove Weights"
WINDOW_ICON = gui.icon.get_icon_file_path("ST_paintRemoveWeightsCtx.png")


class RemoveWeightsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(RemoveWeightsWidget, self).__init__(parent)

        self.geometry = None

        scale_factor = self.logicalDpiX() / 96.0
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self.resize(250 * scale_factor, 400 * scale_factor)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # create widgets
        self.search = gui.widgets.SearchWidget(self)
        layout.addWidget(self.search)

        self.filter = gui.proxies.TreeSortFilterProxyModel(self)
        self.filter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.view = QtWidgets.QTreeView(self)
        self.view.setModel(self.filter)
        self.view.setHeaderHidden(True)
        self.view.selectionModel().selectionChanged.connect(self.paint)
        self.search.text_changed.connect(self.filter.setFilterWildcard)
        self.search.text_changed.connect(self.view.expandAll)
        layout.addWidget(self.view)

        load = QtWidgets.QPushButton(self)
        load.setText("Load")
        load.released.connect(self.load)
        layout.addWidget(load)

    @gui.display_error
    def load(self):
        """
        Load the current selection into a joint model which forces
        an update of the view.

        :raise RuntimeError: When nothing is selected.
        :raise RuntimeError: When selection has no skin cluster attached.
        """
        self.geometry = cmds.ls(selection=True)
        self.geometry = self.geometry[0] if self.geometry else None

        if self.geometry is None:
            raise RuntimeError("No selection made.")

        skin_cluster_fn = skin.get_cluster_fn(self.geometry)
        influences = skin_cluster_fn.influenceObjects()
        influences = [influence.fullPathName() for influence in influences]

        model = gui.models.SkeletonModel(self, influences)
        self.filter.setSourceModel(model)
        self.view.expandAll()

    @gui.display_error
    def paint(self, *args, **kwargs):
        """
        Call the paint method using the influence of the selected index.
        If nothing is selected the method will return early.
        """
        if not self.view.selectionModel().hasSelection():
            return

        index = self.view.selectionModel().selectedRows()[0]
        influence = self.filter.data(index, role=QtCore.Qt.DisplayRole)
        commands.paint(self.geometry, influence)


def show():
    parent = gui.get_main_window()
    widget = RemoveWeightsWidget(parent)
    widget.show()
