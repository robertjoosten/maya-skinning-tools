from maya import OpenMayaUI
from . import Qt


__all__ = [
    "getMayaMainWindow"
]


def getMayaMainWindow():
    """
    Get Maya's main window.

    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = Qt.shiboken.wrapInstance(long(window), Qt.QMainWindow)

    return window
