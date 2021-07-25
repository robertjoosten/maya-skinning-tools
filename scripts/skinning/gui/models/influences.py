from maya import cmds
from maya.api import OpenMayaAnim
from PySide2 import QtWidgets, QtGui, QtCore

from skinning.gui import icon
from skinning.utils import api


__all__ = [
    "InfluencesModel"
]


class InfluenceNode(object):
    def __init__(self, path):
        node_type = cmds.nodeType(path)
        icon_path = icon.get_icon_file_path("out_{}.png".format(node_type))
        self.icon = QtGui.QIcon(icon_path)
        self.path = path

        self.parent = None
        self.children = []

    def child(self, row):
        """
        :param int row:
        :return: Child node
        :rtype: InfluenceNode
        """
        return self.children[row]

    def data(self, role=QtCore.Qt.DisplayRole):
        """
        :param int role:
        :return: Data
        """
        if role == QtCore.Qt.DisplayRole:
            return self.path
        elif role == QtCore.Qt.DecorationRole:
            return self.icon

    def setData(self, value, role=QtCore.Qt.EditRole):
        """
        :param str value:
        :param int role:
        """
        if role == QtCore.Qt.EditRole:
            self.path = cmds.rename(self.path, value)
            return True

        return False


class InfluencesModel(QtCore.QAbstractItemModel):
    """
    The influences model takes in a skin cluster and create a tree model of
    all of the influences that are part of the skin cluster.
    """
    def __init__(self, parent, skin_cluster):
        super(InfluencesModel, self).__init__(parent)
        self.root = InfluenceNode(None)

        mapper = {}
        skin_cluster_obj = api.conversion.get_object(skin_cluster)
        skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)
        influences = skin_cluster_fn.influenceObjects()
        influences = [(influence.fullPathName(), influence.partialPathName()) for influence in influences]
        influences.sort(key=lambda x: x[0])

        for path, path_partial in sorted(influences):
            node = InfluenceNode(path_partial)
            for i in range(1, path.count("|")):
                parent_path = path.rsplit("|", i)[0]
                if parent_path in mapper:
                    parent = mapper[parent_path]
                    break
            else:
                parent = self.root

            node.parent = parent
            parent.children.append(node)

            mapper[path] = node

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
        return self.createIndex(row, column, parent.child(row))

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
            item = index.internalPointer()
            return item.data(role=role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        :param QtCore.QModelIndex index:
        :param str value:
        :param int role:
        """
        if index.isValid():
            item = index.internalPointer()
            return item.data(value, role=role)

        return False
