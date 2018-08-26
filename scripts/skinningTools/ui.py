import os
from maya import OpenMayaUI, cmds

# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4") or type(qtVersion) not in [str, unicode]:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken
    
    
# -----------------------------------------------------------------------------  
    
    
FONT = QFont()
FONT.setFamily("Consolas")

BOLT_FONT = QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)  


# -----------------------------------------------------------------------------    


class BlockSignals(object):
    """
    The block signals context is used to block the signals of the parsed 
    widgets while the code is being executed.
    
    with BlockSignals(*widgets):
        # code
    """
    def __init__(self, *args):
        self.widgets = args
    
    def __enter__(self):
        for widget in self.widgets:
            widget.blockSignals(True)
        
    def __exit__(self, *exc_info):
        for widget in self.widgets:
            widget.blockSignals(False)
            
            
# ----------------------------------------------------------------------------- 
       
       
def addDivider(widget, layout):
    line = QFrame(widget)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line) 

    
# -----------------------------------------------------------------------------    
    
    
def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)
    
    return window
    
    
# ----------------------------------------------------------------------------- 


def getIconPath(name):
    """
    Get an icon path based on file name. All paths in the XBMLANGPATH variable
    processed to see if the provided icon can be found.

    :param str name:
    :return: Icon path
    :rtype: str/None
    """
    for path in os.environ.get("XBMLANGPATH").split(os.pathsep):
        iconPath = os.path.join(path, name)
        if os.path.exists(iconPath):
            return iconPath.replace("\\", "/")
