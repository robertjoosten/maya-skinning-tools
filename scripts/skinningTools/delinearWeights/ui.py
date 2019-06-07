from . import commands
from ..utils import tweening, ui
from ..utils.ui import Qt


# ----------------------------------------------------------------------------


WINDOW_TITLE = "De-Linearize Skin Weights"
WINDOW_ICON = "ST_delinearWeights.png"


# ----------------------------------------------------------------------------


class TweeningOptions(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)

        # create label
        label = Qt.QLabel(self)
        label.setFont(ui.FONT)
        label.setText("Easing Method:")
        layout.addWidget(label)

        # create option box
        options = tweening.getTweeningMethods()
        self.combo = Qt.QComboBox(self)
        self.combo.setFont(ui.FONT)
        self.combo.addItems(options)
        layout.addWidget(self.combo)

    # ------------------------------------------------------------------------

    def currentText(self):
        return self.combo.currentText()


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
        self.resize(300, 25)

        # set icon
        path = ui.getIconPath(WINDOW_ICON)
        self.setWindowIcon(Qt.QIcon(path))

        # create layout
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create tweening
        self.tweening = TweeningOptions(self)
        layout.addWidget(self.tweening)
        
        # create button
        apply = Qt.QPushButton(self)
        apply.setFont(ui.FONT)
        apply.setText("Apply")
        apply.released.connect(self.apply)
        layout.addWidget(apply)

    # ------------------------------------------------------------------------
    
    def apply(self):
        method = self.tweening.currentText()
        commands.deLinearSkinWeightsOnSelection(method)


# ----------------------------------------------------------------------------


def show():
    delinearWeights = DelinearWeightsWidget(ui.getMayaMainWindow())
    delinearWeights.show()
