from PySide2 import QtCore


__all__ = [
    "TreeSortFilterProxyModel"
]


class TreeSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    """
    In earlier versions of Qt it is not possible to automatically un-hide
    parents of a matching row.
    """

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Subclass the filter state to also check all of its parents and
        children when searching for a match. This comes in handy in tree
        views so the parents don't hide if the children match.

        :param int source_row:
        :param QtCore.QModelIndex source_parent:
        :return: Accepts state
        :rtype: bool
        """
        model = self.sourceModel()
        parent = source_parent

        def has_accepted_children(row, item):
            index = model.index(row, 0, item)
            if not index.isValid() or not model.rowCount(index):
                return False

            for row in range(model.rowCount(index)):
                if super(TreeSortFilterProxyModel, self).filterAcceptsRow(row, index):
                    return True
                elif has_accepted_children(row, index):
                    return True

        if super(TreeSortFilterProxyModel, self).filterAcceptsRow(source_row, source_parent):
            return True
        elif has_accepted_children(source_row, source_parent):
            return True

        return False
