from PySide2 import QtWidgets, QtGui, QtCore

from skinning.gui import icon
from skinning.utils import influence


__all__ = [
    "SkeletonModel"
]


class SkeletonModel(QtCore.QAbstractItemModel):
    """
    The influences model takes in a skin cluster and create a tree model of
    all of the influences that are part of the skin cluster.
    """
    def __init__(self, parent, influences):
        super(SkeletonModel, self).__init__(parent)
        self.root = influence.Skeleton(influences)

    # ------------------------------------------------------------------------

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """
        :param int row:
        :param int column:
        :param QtCore.QModelIndex parent:
        :return: Index
        :rtype: QtCore.QModelIndex
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parent = parent.internalPointer() if parent.isValid() else self.root
        return self.createIndex(row, column, parent.children[row])

    def parent(self, index):
        """
        :param QtCore.QModelIndex index:
        :return: Parent
        :rtype: QtCore.QModelIndex
        """
        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer().parent
        if item == self.root or item.parent is None:
            return QtCore.QModelIndex()
        else:
            row = item.parent.children.index(item)
            return self.createIndex(row, 0, item)

    # ------------------------------------------------------------------------

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        :param QtCore.QModelIndex parent:
        :return: Row count
        :rtype: int
        """
        item = parent.internalPointer() if parent.isValid() else self.root
        return len(item.children)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        :param QtCore.QModelIndex parent:
        :return: Column count
        :rtype: int
        """
        return 1

    # ------------------------------------------------------------------------

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        :param QtCore.QModelIndex index:
        :param int role:
        :return: Data
        """
        if index.isValid():
            influence = index.internalPointer()
            if role == QtCore.Qt.DisplayRole:
                return influence.path
            elif role == QtCore.Qt.DecorationRole:
                icon_name = "out_{}.png".format(influence.type)
                icon_path = icon.get_icon_file_path(icon_name)
                return QtGui.QIcon(icon_path)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        :param QtCore.QModelIndex index:
        :param str value:
        :param int role:
        """
        if index.isValid() and role == QtCore.Qt.EditRole:
            influence = index.internalPointer()
            influence.rename(value)
            return True

        return False
