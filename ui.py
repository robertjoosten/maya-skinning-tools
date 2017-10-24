import os
from maya import OpenMayaUI, cmds, mel

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

def findIcon(icon):
    """
    Loop over all icon paths registered in the XBMLANGPATH environment 
    variable ( appending the tools icon path to that list ). If the 
    icon exist a full path will be returned.

    :param str icon: icon name including extention
    :return: icon path
    :rtype: str or None
    """
    paths = []

    # get maya icon paths
    if os.environ.get("XBMLANGPATH"):     
        paths = os.environ.get("XBMLANGPATH").split(os.pathsep)                                 

    # append tool icon path
    paths.insert(
        0,
        os.path.join(
            os.path.split(__file__)[0], 
            "icons" 
        ) 
    )

    # loop all potential paths
    for path in paths:
        filepath = os.path.join(path, icon)
        if os.path.exists(filepath):
            return filepath