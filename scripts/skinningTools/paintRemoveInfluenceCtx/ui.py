from maya import cmds, OpenMaya
from functools import partial

from . import commands
from .. import ui, utils


# ------------------------------------------------------------------------


WINDOW_TITLE = "Paint : Remove Influences"
WINDOW_ICON = "ST_paintRemoveInfluenceCtx.png"


ITEM_STYLESHEET = """
QPushButton {text-align: left}
QPushButton::pressed, QPushButton::hover {color: orange}
"""


# ------------------------------------------------------------------------


class PaintRemoveInfluencesWidget(ui.QWidget):
    def __init__(self, parent):
        ui.QWidget.__init__(self, parent)

        # ui
        self.setParent(parent)        
        self.setWindowFlags(ui.Qt.Window)   

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(250, 400)
        
        # set icon
        path = ui.getIconPath(WINDOW_ICON)
        if path:
            self.setWindowIcon(ui.QIcon(path))      

        # create layout   
        layout = ui.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        
        # create tree
        self.tree = ui.QTreeWidget(self)
        self.tree.setRootIsDecorated(True)
        self.tree.setSelectionMode(ui.QAbstractItemView.NoSelection)
        self.tree.setFocusPolicy(ui.Qt.NoFocus)
        self.tree.header().setVisible(False)
        self.tree.setFont(ui.FONT)
        layout.addWidget(self.tree)
        
        # create button
        self.button = ui.QPushButton( self )
        self.button.setText("Load")
        self.button.setFixedHeight(35) 
        self.button.setFont(ui.BOLT_FONT)
        self.button.pressed.connect(self.load)
        layout.addWidget(self.button)
   
    # ------------------------------------------------------------------------
    
    def paint(self, mesh, influence):
        commands.paint(mesh, influence)
            
    # ------------------------------------------------------------------------ 
    
    def load( self ):
        # clear ui
        self.tree.clear()
        
        # get selected meshes
        meshes = utils.getSkinnedMeshesFromSelection()
        
        if not meshes:
            self.setWindowTitle(WINDOW_TITLE)
            raise RuntimeError("Select a smooth bound mesh!")
             
        # update window title
        mesh = meshes[0]
        self.setWindowTitle(mesh.split("|")[-1])
        
        # get skinCluster
        obj = utils.asMObject(mesh)
        skinCluster = utils.asMFnSkinCluster(obj)
        
        # get influences
        influencesPrev = []
        influencesSort = []
        infDag, _, _ = utils.getInfluences(skinCluster)
        
        # sort influences
        for i in range(infDag.length()):
            influencesSort.append((i, infDag[i]))
        influencesSort.sort(key=lambda x: len(x[1].fullPathName().split("|")))
        
        def getParent(path):
            for p, button in influencesPrev:
                if path.startswith(p):
                    return button
                    
            return self.tree
        
        # create buttons
        for i, dag in influencesSort:
            # get influence names
            path = dag.fullPathName()
            partialPath = dag.partialPathName()
            
            # get parent
            parent = getParent(path)

            # create button
            button = ui.QPushButton(self.tree)
            button.setFlat(True)
            button.setText(partialPath)
            button.setFont(ui.FONT)
            button.setStyleSheet(ITEM_STYLESHEET)
            
            # connect command
            button.pressed.connect( 
                partial(
                    self.paint, 
                    mesh,
                    path
                ) 
            )
            
            # create item
            item = ui.QTreeWidgetItem(parent)
            
            # add to tree
            self.tree.setItemWidget(item, 0, button)
            
            # update item
            item.setIcon( 0, self.getInfluenceIcon(dag.apiType()))
            item.setExpanded(True)
            
            # store previous
            influencesPrev.insert(0, (path, item))
            
    def getInfluenceIcon(self, t):
        if t == OpenMaya.MFn.kJoint:        
            return ui.QIcon(":/out_joint.png")
        elif t == OpenMaya.MFn.kTransform:    
            return u.QIcon(":/out_transform.png")


# ----------------------------------------------------------------------------


def show():
    paintRemoveInfluences = PaintRemoveInfluencesWidget(ui.mayaWindow())
    paintRemoveInfluences.show()
