import re
from maya import cmds, OpenMaya
from collections import OrderedDict

from . import commands
from ..utils import ui, api, path, selection
from ..utils.ui import Qt, widgets


# ------------------------------------------------------------------------


WINDOW_TITLE = "Paint : Remove Influences"
WINDOW_ICON = "ST_paintRemoveInfluenceCtx.png"


ITEM_STYLESHEET = """
QPushButton {text-align: left}
QPushButton::pressed, QPushButton::hover {color: orange}
"""


INFLUENCE_ICONS = {
    "joint": ":/out_joint.png",
    "transform": ":/out_transform.png"
}


# ------------------------------------------------------------------------


class InfluenceWidget(Qt.QTreeWidgetItem):
    def __init__(self, parent, mesh, influence):
        Qt.QTreeWidgetItem.__init__(self, parent)

        # set variables
        self._mesh = mesh
        self._influence = influence
        self._name = path.getRootPath(influence)
        self._parent = parent

        # set text
        self.setText(0, self.name)

        # set expanded
        self.setExpanded(True)

        # set icon
        icon = self.getInfluenceIcon()
        self.setIcon(0, icon)

    # ------------------------------------------------------------------------

    @property
    def name(self):
        """
        :return: Name
        :rtype: str
        """
        return self._name

    # ------------------------------------------------------------------------

    @property
    def mesh(self):
        """
        :return: Mesh
        :rtype: str
        """
        return self._mesh

    @property
    def influence(self):
        """
        :return: Influence
        :rtype: str
        """
        return self._influence

    # ------------------------------------------------------------------------

    def getPreferredParent(self):
        """
        :return: Preferred parent
        :rtype: InfluenceWidget/QTreeWidget
        """
        return self._parent

    # ------------------------------------------------------------------------

    def getInfluenceIcon(self):
        """
        Get the influence icon based on the node type of the influence. If
        the node type is not present in the INFLUENCE_ICONS variable the
        icon will be defaulted to a transform.

        :return: Icon
        :rtype: QIcon
        """
        # get influence node type
        nodeType = cmds.nodeType(self.influence)

        # get icon path
        path = INFLUENCE_ICONS.get(nodeType, ":/out_transform.png")
        return Qt.QIcon(path)

    # ------------------------------------------------------------------------

    def paint(self):
        commands.paint(self.mesh, self.influence)


class PaintRemoveInfluencesWidget(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # ui
        self.setParent(parent)        
        self.setWindowFlags(Qt.Qt.Window)

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(250, 400)
        
        # set icon
        path = ui.getIconPath(WINDOW_ICON)
        if path:
            self.setWindowIcon(Qt.QIcon(path))

        # create layout   
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create search
        self.search = widgets.Search(self)
        self.search.searchChanged.connect(self.filter)
        layout.addWidget(self.search)
        
        # create tree
        self.tree = Qt.QTreeWidget(self)
        self.tree.setRootIsDecorated(True)
        self.tree.setFocusPolicy(Qt.Qt.NoFocus)
        self.tree.header().setVisible(False)
        self.tree.setFont(ui.FONT)
        self.tree.itemSelectionChanged.connect(self.paint)

        layout.addWidget(self.tree)
        
        # create button
        self.button = Qt.QPushButton( self )
        self.button.setText("Load")
        self.button.setFixedHeight(35) 
        self.button.setFont(ui.BOLT_FONT)
        self.button.pressed.connect(self.load)
        layout.addWidget(self.button)

    # ------------------------------------------------------------------------

    def paint(self):
        """
        Get the selected item and trigger the paint function on that item.
        """
        # get items
        items = self.tree.selectedItems()

        # validate items
        if not items:
            return

        # trigger paint command
        items[0].paint()

    # ------------------------------------------------------------------------

    def filter(self, text):
        """
        Loop all items and hide widgets not matching the text value. If no
        text is provided all widgets will be displayed.

        :param str text:
        """
        # clear selection
        for item in self.tree.selectedItems():
            item.setSelected(False)

        # variables
        text = text.lower()
        matches = OrderedDict()
        misses = []

        # get matching widgets
        iter = Qt.QTreeWidgetItemIterator(self.tree)
        while iter.value():
            # get widget
            widget = iter.value()

            # set widget
            if not text or re.search(text, widget.name.lower()):
                matches[widget.name] = widget
            else:
                misses.append(widget)

            iter.next()

        # re-parent matching widgets so they are visible in case its parent
        # widget is not a match.
        for name, widget in matches.iteritems():
            # get preferred parent
            parent = widget.getPreferredParent()

            # get actual parent
            if isinstance(parent, InfluenceWidget):
                parent = matches.get(
                    parent.name,
                    self.tree.invisibleRootItem()
                )

            # remove child
            temp = widget.parent() or self.tree.invisibleRootItem()
            temp.removeChild(widget)

            # add child
            parent.addChild(widget)

            # set expanded
            widget.setHidden(False)
            widget.setExpanded(True)

        # hide rest
        for widget in misses:
            widget.setHidden(True)

    # ------------------------------------------------------------------------
    
    def load(self):
        """
        Load the selected mesh into the paint remove influence widget. All
        selected skinned meshes will be queried but only the first one will be
        displayed by the widget.

        :raise RuntimeError: When no skinned mesh is selected
        """
        # clear ui
        self.tree.clear()

        # get selected meshes
        meshes = selection.getSkinnedMeshesFromSelection()
        
        if not meshes:
            self.setWindowTitle(WINDOW_TITLE)
            raise RuntimeError("Select a smooth bound mesh!")
             
        # update window title
        mesh = meshes[0]
        self.setWindowTitle(mesh.split("|")[-1])
        
        # get skinCluster
        obj = api.asMObject(mesh)
        skinCluster = api.asMFnSkinCluster(obj)
        
        # get influences
        influencesPrev = []
        influencesSort = []
        infDag, _, _ = api.getInfluences(skinCluster)
        
        # sort influences
        for i in range(infDag.length()):
            influencesSort.append((i, infDag[i]))
        influencesSort.sort(key=lambda x: len(x[1].fullPathName().split("|")))
        
        def getParent(path):
            for p, button in influencesPrev:
                if path.startswith(p):
                    return button
                    
            return self.tree.invisibleRootItem()
        
        # create buttons
        for i, dag in influencesSort:
            # get influence path
            path = dag.fullPathName()

            # get parent
            parent = getParent(path)

            # create widget
            item = InfluenceWidget(parent, mesh, path)

            # store previous
            influencesPrev.insert(0, (path, item))

        # filter
        self.filter(self.search.text)


# ----------------------------------------------------------------------------


def show():
    paintRemoveInfluences = PaintRemoveInfluencesWidget(ui.getMayaMainWindow())
    paintRemoveInfluences.show()
