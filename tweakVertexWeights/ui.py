import sys

from maya import OpenMaya, OpenMayaUI, cmds
from rjSkinningTools import ui, utils
from .. import tweakVertexWeights

# ----------------------------------------------------------------------------

WINDOW_TITLE = "Tweak Vertex Weights"
WINDOW_ICON = "tweakVertexWeights.png"

ORANGE_STYLESHEET = "QLabel{color: orange}"
RED_STYLESHEET = "QLabel{color: red}"

LOCK_ICON = {
    True:":/Lock_ON.png",
    False:":/Lock_OFF.png"
}

DISPLAY_MAXIMUM = 10

# ----------------------------------------------------------------------------

class VertexLabelWidget(ui.QWidget):
    """
    Widget used to manage the vertex that is parsed. Will create a label, 
    warning label and checkbox to display.

    :param QWidget parent:   
    :param str vertex:   
    """
    signal = ui.Signal(bool)
    
    def __init__(self, parent, vertex):
        ui.QWidget.__init__(self, parent)
        
        # create layout
        layout = ui.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(10)
        
        # create label
        name = ui.QLabel(self)
        name.setText(vertex.split("|")[-1])
        name.setFont(ui.BOLT_FONT)
        name.setStyleSheet(ORANGE_STYLESHEET)
        
        # set label size policy
        sizePolicy = ui.QSizePolicy(
            ui.QSizePolicy.Preferred, 
            ui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            name.sizePolicy().hasHeightForWidth()
        )
        name.setSizePolicy(sizePolicy)
        layout.addWidget(name)
        
        # create warning
        self.warning = ui.QLabel(self)
        self.warning.setText("Exceeded Maximum Influences")
        self.warning.setFont(ui.FONT)
        self.warning.setStyleSheet(RED_STYLESHEET)
        self.warning.setVisible(False)
        layout.addWidget(self.warning)
        
        # create checkbox
        self.checkbox = ui.QCheckBox(self)
        self.checkbox.setText("Display All Influences")
        self.checkbox.setFont(ui.FONT)
        self.checkbox.stateChanged.connect(self.checkboxStateChanged)
        layout.addWidget(self.checkbox)
        
    # ------------------------------------------------------------------------
    
    def displayWarning(self, state):
        """
        Update the visibility of the warning based on the input. Shows that 
        the user has exceeded the maximum allowed influences.
        
        :param bool state: Visible state of the warning
        """
        self.warning.setVisible(state)
        
    # ------------------------------------------------------------------------
        
    def checkboxStateChanged(self):
        self.signal.emit(self.checkbox.isChecked())
        
class VertexInfluenceWidget(ui.QWidget):
    """
    Widget used to manage the influence weight. A label, slider and spinbox
    are created that can be manipulated by the user. Also can an influence be
    locked so its values cannot be changed.

    :param QWidget parent:   
    :param str influence:   
    :param float value:
    """
    signal = ui.Signal(str, float)
    
    def __init__(self, parent, influence, value):
        ui.QWidget.__init__(self, parent)
        
        # variables
        self.influence = influence
        self.value = value
        
        isLocked = cmds.getAttr("{0}.liw".format(influence))
        
        # create layout
        layout = ui.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)
        
        # create lock
        self.lock = ui.QPushButton(self)
        self.lock.setFlat(True)
        self.lock.setCheckable(True)
        self.lock.setIcon(ui.QIcon(LOCK_ICON.get(isLocked)))
        self.lock.setFixedSize(ui.QSize(18, 18))
        self.lock.released.connect(self.toggleLocked)
        layout.addWidget(self.lock)
        
        # create label
        name = ui.QLabel(self)
        name.setText(influence)
        name.setFont(ui.FONT)
        name.setMinimumWidth(150)
        layout.addWidget(name)
        
        # create slider
        self.slider = ui.QSlider(self)
        self.slider.setInputMethodHints(ui.Qt.ImhNone)
        self.slider.setMaximum(1000)
        self.slider.setSingleStep(1)
        self.slider.setOrientation(ui.Qt.Horizontal)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        layout.addWidget(self.slider)
        
        # create label
        self.spinbox = ui.QDoubleSpinBox(self)
        self.spinbox.setFont(ui.FONT)
        self.spinbox.setDecimals(3)
        self.spinbox.setRange(0, 1)
        self.spinbox.setSingleStep(0.001)
        self.spinbox.valueChanged.connect(self.spinboxValueChanged)
        layout.addWidget(self.spinbox)
        
        # set ui
        self.setValue(value)
        
        if isLocked:
            self.lock.setChecked(True)
            self.spinbox.setEnabled(False)
            self.slider.setEnabled(False)
        
    # ------------------------------------------------------------------------
        
    def isLocked(self):
        """
        :return: Locked state of the influence
        :rtype: bool
        """
        return self.lock.isChecked()
        
    def toggleLocked(self):
        """
        Toggle the locked state of the influence. Will enable or disable the
        input fields of the influence and update the lock icon.
        """
        isLocked = self.isLocked()
    
        self.lock.setIcon(LOCK_ICON.get(isLocked))
        self.spinbox.setEnabled(not isLocked)
        self.slider.setEnabled(not isLocked)
        
    # ------------------------------------------------------------------------
        
    def getSliderValue(self):
        """
        :return: Weight value read from the slider.
        :rtype: float
        """
        return float(self.slider.value()) / 1000
        
    def getSpinboxValue(self):
        """
        :return: Weight value read from the spinbox.
        :rtype: float
        """
        return self.spinbox.value()
        
    def setValue(self, value):
        """
        Set the value of the influence. Will block the signals as the 
        valueChanged callback shouldn't be triggered.
        
        :param float value: Influence weight value
        """
        self.value = value
        
        with ui.BlockSignals(self.spinbox, self.slider):
            self.spinbox.setValue(value) 
            self.slider.setValue(int(value*1000))
            
    # ------------------------------------------------------------------------
    
    def spinboxValueChanged(self):
        self.signal.emit(self.influence, self.getSpinboxValue())
    
    def sliderValueChanged(self):
        self.signal.emit(self.influence, self.getSliderValue())
        
class VertexInfluencesWidget(ui.QWidget):
    """
    Widget used to manage the collection of influences. Will loop over all of 
    the influences and instance widgets :class:`VertexInfluenceWidget`.

    :param QWidget parent:   
    :param list data: Sorted list of values and influences
    """
    signal = ui.Signal(list)
    warningSignal = ui.Signal(bool)
    
    def __init__(self, parent, skinCluster, data):
        ui.QWidget.__init__(self, parent)
        
        #self.setFrameShape(ui.QFrame.StyledPanel)
        #self.setFrameShadow(ui.QFrame.Sunken)
        
        # variables
        self.widgets = []
        
        # skin cluster data
        self.normalizeWeights = cmds.getAttr(
            "{0}.normalizeWeights".format(skinCluster)
        )
        self.maxInfluences = cmds.getAttr(
            "{0}.maxInfluences".format(skinCluster)
        )
        self.maintainMaxInfluences = cmds.getAttr(
            "{0}.maintainMaxInfluences".format(skinCluster)
        )
        
        # create layout
        layout = ui.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        
        # create widgets
        for value, influence in data:
            widget = VertexInfluenceWidget(self, influence, value)
            widget.signal.connect(self.calculateWeights)
            
            layout.addWidget(widget)
            self.widgets.append(widget)
            
        # set visibility
        self.displayInfluences(False)
            
    # ------------------------------------------------------------------------
    
    def displayInfluences(self, state):
        """
        Based on the state the influences will be displayed always or only 
        when the value is more than 0. This is done to make the influences 
        overview less crowded and easier to manage.
        
        :param bool state: Influence visibility state
        """
        for widget in self.widgets:
            if widget.value > sys.float_info.epsilon:
                widget.setVisible(True)
                continue
                
            widget.setVisible(state)
            
    def displayMaxInfluences(self):
        """
        Determines if the maximum influences is exceeded and will emit a 
        warning signal so the user can be alerted this is happening.
        """
        if self.maintainMaxInfluences:
            num = len(
                [
                    0 
                    for widget in self.widgets 
                    if widget.value > sys.float_info.epsilon
                ]
            )
            if num > self.maxInfluences:
                self.warningSignal.emit(True)
                return
                
        self.warningSignal.emit(False)
        
    # ------------------------------------------------------------------------
        
    def resetWeights(self):
        """
        Reset the influence weights to the values before the input was 
        changed. This sometimes needs to happen if the user does invalid 
        actions. Like trying to change the weights, while all other influences
        are locked.
        """
        for widget in self.widgets:
            widget.setValue(widget.value)
            
    def calculateWeights(self, changedInfluence, changedValue):
        """
        Calculate the new weights based on the values of the skin cluster and
        updated ui fields. Of normalization mode is activated the new weights
        will be normalized, this will also be reflected in the ui. Locked 
        weights are respected and won't be changed. The new weights will be 
        formatted in a list that can be used by Maya's skinPercent command.
        This list will then be emmited to be picked up by another function.
        
        :param str changedInfluence: Influence name
        :param float changedValue: Influence value
        """
        
        # get new weights
        weightsList = []
        weightsDict = {
            widget.influence:widget.value
            for widget in self.widgets
        }
        weightsDict[changedInfluence] = changedValue
        
        # normalize weights
        if self.normalizeWeights == 1:
            factor = 1
            
            # get normalizable weights
            normalizeable = [ 
                widget.influence 
                for widget in self.widgets 
                if widget.value > 0 
                and widget.influence != changedInfluence 
                and not widget.isLocked() 
            ]
                 
            # get normalization factor
            if normalizeable:
                # get 
                total = sum(weightsDict.values())
                normal = sum(
                    [weight
                    for influence, weight in weightsDict.iteritems()
                    if influence in normalizeable ]
                )
                
                factor = (1-total+normal) / normal

            # reset and return if no normalizable weights are found
            else:
                self.resetWeights()
                return
                
            # set updated weights
            for influence, weight in weightsDict.iteritems():
                if influence in normalizeable:
                    weightsDict[influence] = weight * factor

        # update ui
        for widget in self.widgets:
            widget.setValue(weightsDict[widget.influence])
            
        # update list
        weightsList = [
            [influence, weight]
            for influence, weight in weightsDict.iteritems()
        ]
            
        self.signal.emit(weightsList)
        self.displayMaxInfluences()

class VertexWidget(ui.QWidget):
    """
    Widget used to manage the influences of an entire vertex. Will create a 
    header :class:`VertexLabelWidget`. and a manager for all of the influences
    :class:`VertexInfluencesWidget`.

    :param QWidget parent:   
    :param str vertex:
    """
    def __init__(self, parent, vertex):
        ui.QWidget.__init__(self, parent)
        
        # variables
        self.vertex = vertex
        self.mesh, _ = vertex.split(".", 1)
        self.skinCluster = utils.getSkinCluster(self.mesh)
        
        # get skinned data
        influences = cmds.skinPercent(
            self.skinCluster, vertex, query=True, transform=None
        )
        
        values = cmds.skinPercent(
            self.skinCluster, vertex, query=True, value=True
        )
        
        # order data
        data = zip(values, influences)
        data.sort()
        data.reverse()

        # create layout
        layout = ui.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        
        # create divider
        ui.addDivider(self, layout)
        
        # create label
        self.label = VertexLabelWidget(self, vertex)
        layout.addWidget(self.label)
        
        # create divider
        ui.addDivider(self, layout)
        
        # create frame
        self.frame = VertexInfluencesWidget(self, self.skinCluster, data)
        self.frame.signal.connect(self.setWeights)
        layout.addWidget(self.frame)
        
        # connect influences toggle
        self.label.signal.connect(self.frame.displayInfluences)
        self.frame.warningSignal.connect(self.label.displayWarning)
        
        # force display
        self.frame.displayMaxInfluences()
        
    # ------------------------------------------------------------------------
    
    def setWeights(self, data):
        """
        Set the weights on the Maya vertex.
        
        :param list data: List of list with influences and weights data
        """
        cmds.skinPercent(self.skinCluster, self.vertex, transformValue=data)
        
# ----------------------------------------------------------------------------

class TweakVertexWeightsWidget(ui.QWidget):
    """
    Widget used to manage all of the vertices that are currently selected. A
    callback is registered to update the ui every time the selection is 
    changed. For each vertex the following class is used :class:`VertexWidget`

    :param QWidget parent:   
    """
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)
        
        # ui
        self.setParent(parent)        
        self.setWindowFlags(ui.Qt.Window)   

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(550, 350)
        
        # set icon
        path = ui.findIcon(WINDOW_ICON)
        if path:
            self.setWindowIcon(ui.QIcon(path))      
    
        # create layout
        layout = ui.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)

        # create scroll
        scrollArea = ui.QScrollArea(self)
        scrollArea.setWidgetResizable(True)

        self.widget = ui.QWidget(self)
        self.layout = ui.QVBoxLayout(self.widget)
        
        scrollArea.setWidget(self.widget)
        layout.addWidget(scrollArea)
        
        # create spacer
        spacer = ui.QSpacerItem(
            1, 
            1, 
            ui.QSizePolicy.Minimum, 
            ui.QSizePolicy.Expanding
        )
        self.layout.addItem(spacer)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(3)
        
        # update
        self.id_ = None
        self.registerCallback()
        self.selectionChanged()
        
    # ------------------------------------------------------------------------
        
    def registerCallback(self):
        """
        Register callback that will update the ui everytime the selection has
        changed.
        """
        self.id_ = OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified, 
            self.selectionChanged
        )
        
    def removeCallback(self):
        if not self.id_:
            return
            
        OpenMaya.MMessage.removeCallback(self.id_)
        
    # ------------------------------------------------------------------------
        
    def closeEvent(self, event):
        self.removeCallback()
        ui.QWidget.closeEvent(self, event)
        
    # ------------------------------------------------------------------------
    
    def clear(self):
        """
        Remove all of the widgets from the layout apart from the last item 
        which is a spacer item.
        """
        for i in reversed(range(self.layout.count()-1)):
            item = self.layout.itemAt(i)
            item.widget().deleteLater()
        
    def selectionChanged(self, *args):
        """
        Query the current selection and populate the ui with the skinned 
        vertices that are currently selection.
        """
        # clear ui
        self.clear()
        
        # get selection
        vertices = tweakVertexWeights.getSkinnedVertices()
        for vertex in vertices[:DISPLAY_MAXIMUM]:
            widget = VertexWidget(self, vertex)
            
            num = self.layout.count() - 1
            self.layout.insertWidget(num, widget)

# ----------------------------------------------------------------------------
        
def show():
    tweakVertexWeights = TweakVertexWeightsWidget(ui.mayaWindow())
    tweakVertexWeights.show()
