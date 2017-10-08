import sys

from maya import OpenMaya, cmds
from functools import partial
from rjSkinningTools import ui, utils
from .. import softSelectionToWeights

# ----------------------------------------------------------------------------

WINDOW_TITLE = "Soft Selection to Skin Weights"
WINDOW_ICON = "softSelectionToWeights.png"

ADD_ICON = ui.QIcon(":/setEdAddCmd.png")
REMOVE_ICON = ui.QIcon(":/setEdRemoveCmd.png")
JOINT_ICON = ui.QIcon(":/kinJoint.png")
SOFTSELECT_ICON = ui.QIcon(":/customSoftSelectFalloffCurve.png")
SELECT_ICON = ui.QIcon(":/redSelect.png")

# ----------------------------------------------------------------------------

class IconButton(ui.QPushButton):
    """
    Widget used to quickly create icon buttons.

    :param QWidget parent:   
    :param QIcon icon:   
    """
    def __init__(self, parent, icon):
        ui.QPushButton.__init__(self, parent)

        self.setIcon(icon)
        self.setIconSize(ui.QSize(24,24))
        self.setFixedSize(ui.QSize(24,24))

class AddInfluenceWidget(ui.QWidget):
    """
    Widget used to add influences. Will emit the 'addInfluence' signal when
    the add button is released.

    :param QWidget parent:   
    """
    addInfluence = ui.Signal()
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)
        
        # create layout
        layout = ui.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)
        
        # create add button
        add = IconButton(self, ADD_ICON)
        add.setFlat(True)
        add.released.connect(self.addInfluence.emit)
        layout.addWidget(add)
        
        # create title
        label = ui.QLabel(self)
        label.setText("Add Influence")
        label.setFont(ui.BOLT_FONT)
        layout.addWidget(label)

# ----------------------------------------------------------------------------

class FillerInfluenceWidget(ui.QWidget):
    """
    Widget used to set the filler influence. 

    :param QWidget parent:   
    """
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)
        
        # variable
        self._influence = None

        # create layout
        layout = ui.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)
        
        # create joint
        joint = IconButton(self, JOINT_ICON)
        joint.released.connect(self.setInfluenceFromSelection)
        layout.addWidget(joint)
        
        # create label
        self.label = ui.QLabel(self)
        self.label.setText("< filler influence >")
        self.label.setFont(ui.FONT)
        layout.addWidget(self.label)
        
    # ------------------------------------------------------------------------
      
    @property
    def influence(self):
        return self._influence
        
    @influence.setter
    def influence(self, influence):
        self._influence = influence
        
    # ------------------------------------------------------------------------
          
    def setInfluenceFromSelection(self):
        """
        Get all of the joints in the current selection. If no joints are 
        selected a RuntimeError will be raised and the UI reset.
        
        :raises RuntimeError: if no joints are selected
        """
        # get selected joints
        joints = cmds.ls(sl=True, l=True, type="joint")
        
        # if no joints selected reset ui
        if not joints:
            self.influence = None
            self.label.setText("< filler influence >")
            raise RuntimeError("No joint selection detected!")
            
        self.influence = joints[0]
        self.label.setText(joints[0].split("|")[-1])
  
    # ------------------------------------------------------------------------
    
    def contextMenuEvent(self, event): 
        menu = ui.QMenu(self)
        influence = menu.addAction(
            "Select: Filler Influence", 
            partial(
                cmds.select, 
                self.influence
            )
        )
        influence.setIcon(SELECT_ICON)
        influence.setEnabled(True if self.influence else False)

        menu.exec_(self.mapToGlobal(event.pos()))
        
class InfluenceWidget(ui.QWidget):
    """
    Widget used to set the influence and soft selection. Once a new soft 
    selection is made the 'setSoftSelection' signal will be emitted.

    :param QWidget parent:   
    """
    setSoftSelection = ui.Signal()
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)
        
        # variable
        self._influence = None
        
        self._ssActive = None
        self._ssData = {}
        self._ssSettings = {}
        
        # create layout
        layout = ui.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)
        
        # create joint
        joint = IconButton(self, JOINT_ICON)
        joint.released.connect(self.setInfluenceFromSelection)
        layout.addWidget(joint)
        
        # create soft select
        soft = IconButton(self, SOFTSELECT_ICON)
        soft.released.connect(self.setSoftSelectionFromSelection)
        layout.addWidget(soft)
        
        # create label
        self.label = ui.QLabel(self)
        self.label.setText("< influence >")
        self.label.setFont(ui.FONT)
        layout.addWidget(self.label)
        
        # create remove button
        remove = IconButton(self, REMOVE_ICON)
        remove.setFlat(True)
        remove.released.connect(self.deleteLater)
        layout.addWidget(remove)
        
    # ------------------------------------------------------------------------
      
    @property
    def influence(self):
        return self._influence
        
    @influence.setter
    def influence(self, influence):
        self._influence = influence
        
    # ------------------------------------------------------------------------
          
    def setInfluenceFromSelection(self):
        """
        Get all of the joints in the current selection. If no joints are 
        selected a RuntimeError will be raised and the UI reset.
        
        :raises RuntimeError: if no joints are selected
        """
        # get selected joints
        joints = cmds.ls(sl=True, l=True, type="joint")
        
        # if no joints selected reset ui
        if not joints:
            self.influence = None
            self.label.setText("< influence >")
            raise RuntimeError("No joint selection detected!")
            
        self.influence = joints[0]
        self.label.setText(joints[0].split("|")[-1])
        
    # ------------------------------------------------------------------------
    
    @property
    def ssActive(self):
        return self._ssActive
        
    @ssActive.setter
    def ssActive(self, value):
        self._ssActive = value
        
    @property
    def ssSettings(self):
        return self._ssSettings
        
    @ssSettings.setter
    def ssSettings(self, value):
        self._ssSettings = value
 
    @property
    def ssData(self):
        return self._ssData
        
    @ssData.setter
    def ssData(self, value):
        self._ssData = value
        
    # ------------------------------------------------------------------------
    
    def setSoftSelectionFromSelection(self):
        """
        Get the current soft selection. If no soft selection is made a 
        RuntimeError will be raised.
        
        :raises RuntimeError: if no soft selection is made
        """
        self.ssActive, self.ssData = softSelectionToWeights.getSoftSelection()
        self.setSoftSelection.emit()
        
        # reset values if no soft selection
        if not self.ssData:            
            self.ssActive = None
            self.ssData = {}
            self.ssSettings = {}
            raise RuntimeError("No soft selection detected!")
        
        self.ssSettings = {
            "ssc":cmds.softSelect(query=True, ssc=True),
            "ssf":cmds.softSelect(query=True, ssf=True),
            "ssd":cmds.softSelect(query=True, ssd=True)
        }
        
    def selectSoftSelection(self):
        """
        Set the stored soft selection.
        """
        cmds.softSelect(sse=1, **self.ssSettings) 
        OpenMaya.MGlobal.setActiveSelectionList(self.ssActive)
        
    # ------------------------------------------------------------------------
    
    def contextMenuEvent(self, event):    
        menu = ui.QMenu(self)
        influence = menu.addAction(
            "Select: Influence", 
            partial(
                cmds.select, 
                self.influence
            )
        )
        influence.setIcon(SELECT_ICON)
        influence.setEnabled(True if self.influence else False)

        soft = menu.addAction(
            "Select: Soft Selection",
            self.selectSoftSelection
        )
        soft.setIcon(SELECT_ICON)
        soft.setEnabled(True if self.ssData else False)
        
        menu.exec_(self.mapToGlobal(event.pos()))
        
class SoftSelectionToWeightsWidget(ui.QWidget):
    """
    Widget used to manage all of the added influences and their soft 
    selection.
    
    :param QWidget parent:   
    """
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)
        
        # ui
        self.setParent(parent)        
        self.setWindowFlags(ui.Qt.Window)   

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(300, 250)
        
        # set icon
        path = ui.findIcon(WINDOW_ICON)
        if path:
            self.setWindowIcon(ui.QIcon(path))      
    
        # create layout
        layout = ui.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        
        # create add widget
        title = AddInfluenceWidget(self)
        title.addInfluence.connect(self.addInfluence)
        layout.addWidget(title)

        # create scroll
        scrollArea = ui.QScrollArea(self)
        scrollArea.setWidgetResizable(True)

        self.widget = ui.QWidget(self)
        self.layout = ui.QVBoxLayout(self.widget)
        
        scrollArea.setWidget(self.widget)
        layout.addWidget(scrollArea)
        
        # create filler influence
        self.filler = FillerInfluenceWidget(self)
        self.layout.addWidget(self.filler)
        
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

        # create button
        button = ui.QPushButton(self)
        button.setText("Skin")
        button.setFont(ui.FONT)
        button.released.connect(self.skin)
        layout.addWidget(button) 
        
        # create button
        self.progressBar = ui.QProgressBar(self)   
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)
        
    # ------------------------------------------------------------------------
       
    def addInfluence(self):
        """
        Add an new influence widget to the layout, :class:`InfluenceWidget`.
        """
        widget = InfluenceWidget(self)
        widget.setSoftSelection.connect(self.setEnableInfluence)
        
        num = self.layout.count() - 2
        self.layout.insertWidget(num, widget)
        
    def getInfluences(self):
        """
        Loop over all of the content of the scroll layout and yield if the
        item is an instance of :class:`InfluenceWidget`.
        
        :return: All influence widgets in the scroll layout
        :rtype: iterator
        """
        for i in range(self.layout.count()-1):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, InfluenceWidget):
                yield widget
                
    # ------------------------------------------------------------------------
    
    def setEnableInfluence(self):
        """
        This function is called when a soft selection is made. All influences 
        will be checked to see if there is a mesh with no skin cluster 
        attached. If this is the case the filler joint widget 
        :class:`FillerInfluenceWidget` will be enabled.
        """
        self.filler.setEnabled(False)
        influences = self.getInfluences()
        for influence in influences:
            for mesh in influence.ssData.keys():
                if not utils.isSkinned(mesh):
                    self.filler.setEnabled(True)
                    return
                    
    # ------------------------------------------------------------------------
                
    def skin(self):
        """
        This function is called when the skin button is released. All of the
        influences sorted and the mesh skin weights updated. As this can be 
        a time consuming process a progress bar will be updated with every 
        mesh that gets updated.
        """
        data = {}
        infs = []
        
        # blend influences
        influences = self.getInfluences()
        for influence in influences:
            inf = influence.influence
            soft = influence.ssData
            
            if not inf or not soft:
                continue
                
            # add influences
            infs.append(inf)
            
            # loop meshes
            for mesh, weights in soft.iteritems():
                if not mesh in data.keys():
                    data[mesh] = {}
                    
                # loop weights
                for index, weight in weights.iteritems():
                    if not index in data[mesh].keys():
                        data[mesh][index] = {}
                        
                    if not inf in data[mesh][index].keys():
                        data[mesh][index][inf] = 0
                        
                    data[mesh][index][inf] += weight
                    
        # set progress bar
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)  
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(data.keys()))
        
        # set weights
        for mesh, meshData in data.iteritems():
            filler = self.filler.influence
            if not utils.isSkinned(mesh) and not filler:
                print "No Filler Influence found for mesh: {0}".format(mesh)
                continue
                
            softSelectionToWeights.setSkinWeights(
                mesh,
                meshData,
                infs,
                filler
            )
            
            # update progress bar
            num = self.progressBar.value()
            self.progressBar.setValue(num+1)  
        
# ----------------------------------------------------------------------------
        
def show():
    softSelectionToWeights = SoftSelectionToWeightsWidget(ui.mayaWindow())
    softSelectionToWeights.show()
