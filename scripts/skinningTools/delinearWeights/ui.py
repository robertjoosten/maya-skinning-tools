from . import commands
from ..utils import ui
from ..utils.ui import Qt, widgets


# ----------------------------------------------------------------------------


WINDOW_TITLE = "De-Linearize Skin Weights"
WINDOW_ICON = "ST_delinearWeights.png"


# ----------------------------------------------------------------------------


class DelinearWeightsWidget(Qt.QWidget):
    """
    Widget used to de-linearize all of the vertices that are currently 
    selected. 
    
    :param QWidget parent:   
    """
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # ui
        self.setParent(parent)        
        self.setWindowFlags(Qt.Qt.Window)

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(400, 25)

        # set icon
        path = ui.getIconPath(WINDOW_ICON)
        self.setWindowIcon(Qt.QIcon(path))

        # create layout
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create tweening
        self.tweening = widgets.TweeningOptions(self)
        layout.addWidget(self.tweening)

        # create divider
        divider = widgets.Divider(self)
        layout.addWidget(divider)
        
        # create button
        apply = Qt.QPushButton(self)
        apply.setFont(ui.FONT)
        apply.setText("Apply")
        apply.released.connect(self.apply)
        layout.addWidget(apply)

    # ------------------------------------------------------------------------
    
    def apply(self):
        method = self.tweening.currentMethod()
        commands.deLinearSkinWeightsOnSelection(method)


# ----------------------------------------------------------------------------


def show():
    delinearWeights = DelinearWeightsWidget(ui.getMayaMainWindow())
    delinearWeights.show()
