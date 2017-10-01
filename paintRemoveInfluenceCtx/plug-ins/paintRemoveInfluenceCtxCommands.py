from maya import cmds, OpenMaya, OpenMayaMPx, OpenMayaAnim
from rjSkinningTools import utils

__author__    = "Robert Joosten"
__version__   = "0.8.1"
__email__     = "rwm.joosten@gmail.com"

# ----------------------------------------------------------------------------

CONTEXT_INITIALIZE = "paintRemoveInfluenceCtxInitialize"
CONTEXT_BEFORE = "paintSmoothWeightsCtxBefore"
CONTEXT_AFTER = "paintSmoothWeightsCtxAfter"

# ----------------------------------------------------------------------------

class RemoveInfluenceCtxManager(object):
    def __init__(self):
        self.reset()
        
    # ------------------------------------------------------------------------
    
    def reset(self):
        self._obj = None
        self._dag = None
        self._index = None
        self._influence = None
        self._influences = OpenMaya.MDagPathArray()
        self._influencesLocked = []
        
        self._skinCluster = None
        self._normalizeMode = None
        
        self.beforeSelection = OpenMaya.MIntArray()
        self.afterSelection = OpenMaya.MIntArray()
        
    def initialize(self, obj, influence):
        # if no mesh reset variables
        if not obj or not influence:
            self.reset()
            return 

        # get mesh data
        self._obj = utils.asMObject(obj)
        self._dag = utils.asMDagPath(self.obj)
        
        # get skin cluster
        self._skinCluster = utils.asMFnSkinCluster(self.obj)
        
        # get normalized mode
        normalPlug = self.skinCluster.findPlug("normalizeWeights")
        self._normalizeMode = normalPlug.asInt()
        
        # set influence
        influenceObj = utils.asMObject(influence)
        self._influence = utils.asMDagPath(influenceObj)
        
        # set influences
        self.skinCluster.influenceObjects(self._influences)
        
        # set locked influences
        self._influencesLocked = []
        for i in range(self.influences.length()):
            path = self.influences[i].fullPathName()
            locked = cmds.getAttr("{0}.liw".format(path))
            
            self._influencesLocked.append(locked)
        
        # set index
        for i in range(self.influences.length()):
            if self.influence == self.influences[i]:
                self._index = i

    # ------------------------------------------------------------------------
        
    @property
    def obj(self): 
        return self._obj
        
    @property
    def dag(self):
        return self._dag

    @property
    def skinCluster(self): 
        return self._skinCluster
        
    # ------------------------------------------------------------------------
    
    @property
    def normalizeMode(self): 
        return self._normalizeMode
        
    # ------------------------------------------------------------------------
    
    @property
    def index(self):
        return self._index
    
    @property
    def influence(self):
        return self._influence
        
    @property
    def influences(self):
        return self._influences
        
    @property
    def influencesLocked(self):
        return self._influencesLocked
               
    # ------------------------------------------------------------------------
    
    def select(self):
        # variables
        selection = OpenMaya.MSelectionList()
        weights = OpenMaya.MFloatArray()

        # get infliences vertices
        self.skinCluster.getPointsAffectedByInfluence(
            self.influence, 
            selection, 
            weights
        )

        # if no vertices select joint
        if not selection.isEmpty():
            selection.add(self.influence)
        
        # set selection
        componentMode = OpenMaya.MGlobal.kSelectComponentMode
        componentMaskMode = OpenMaya.MSelectionMask.kSelectMeshVerts
        componentMask = OpenMaya.MSelectionMask(componentMaskMode)
        OpenMaya.MGlobal.setSelectionMode(componentMode)
        OpenMaya.MGlobal.setComponentSelectionMask(componentMask)
        OpenMaya.MGlobal.setHiliteList(selection)  
        OpenMaya.MGlobal.setActiveSelectionList(selection)  
        
    # ------------------------------------------------------------------------
    
    def getSelection(self):
        # variable
        indices = OpenMaya.MIntArray()
        allIndices = OpenMaya.MIntArray()
        
        # get active selection
        selection = OpenMaya.MSelectionList()  
        OpenMaya.MGlobal.getActiveSelectionList(selection)

        # loop selection
        iter = OpenMaya.MItSelectionList(selection)
        while not iter.isDone():
            # variables
            component = OpenMaya.MObject()
            dag = OpenMaya.MDagPath()

            iter.getDagPath(dag, component)
            
            if not component.isNull(): 
                objIndices = OpenMaya.MIntArray()

                components = OpenMaya.MFnSingleIndexedComponent(component) 
                components.getElements(indices)
                
                for i in range(indices.length()):
                    allIndices.append(indices[i])
                
            iter.next()
            
        return allIndices
    
    def storeBeforeSelection(self):
        self.beforeSelection = self.getSelection()
        return self.beforeSelection
        
    def storeAfterSelection(self):
        self.afterSelection = self.getSelection()
        return self.afterSelection
        
    # ------------------------------------------------------------------------
    
    def calculateWeights(self, weights, num):
        """
        Calculate the new weights of the removed indices. The new weights are 
        calculated by trying to remove the influence that is active in the 
        tool. Locked influences, normalization are taken into account as they 
        are set on the skin cluster.
        
        :param OpenMaya.MDoubleArray weights: original weights
        :param int num: Amount of influences per vertex
        :return: New weights, new influences
        :rtype: tuple(OpenMaya.MDoubleArray, OpenMaya.MIntArray)
        """
        # variables
        influenceNew = OpenMaya.MIntArray()
        weightsNew = OpenMaya.MDoubleArray()
        
        # add influences
        for i in range(num):
            influenceNew.append(i)
           
        # calculate weights
        for i in range(0, weights.length(), num):
            weightsVtx = [weights[i+j] for j in range(num)]
            indexWeight = weights[i+self.index]
            total = sum(weightsVtx)
            
            # if weight that is trying to be removed is only influence
            # reselect vertex as weights cannot be removed
            if indexWeight == total:
                for w in weightsVtx:
                    weightsNew.append(w)

                continue
                
            # remove index weight
            factor = 1
            factorLocked = 1
            
            weightsVtx = [
                weights[i+j] if j != self.index else 0.0
                for j in range(num)
            ]
    
            # normalize weights
            if self.normalizeMode == 1:
                # get total locked weights
                weightsVtxLocked = sum(
                    [
                        weights[i+j]
                        for j in range(num)
                        if self.influencesLocked[j] 
                    ]
                )
                
                # get total to blend
                total = sum(weightsVtx) - weightsVtxLocked
                
                # get multiply factor
                if weightsVtxLocked >= 1.0 or total == 0.0:
                    factor = 0
                    factorLocked = 1/weightsVtxLocked
                else:
                    factor = (1.0-weightsVtxLocked)/total            
                
            # apply multiply factor
            for j, w in enumerate(weightsVtx):
                if not self.influencesLocked[j]:
                    weightsNew.append(w * factor)
                else:
                    weightsNew.append(w * factorLocked)

        return weightsNew, influenceNew  

    # ------------------------------------------------------------------------
        
    def setWeights(self):
        """
        Calculate and set new weights of the vertices that have been painted
        away. This function will return the previous weights data for undo 
        purposes.
        
        :return: Skin cluster, dag, component, influences, old weights
        :rtype: list(
            OpenMayaAnim.MFnSkinCluster, 
            OpenMaya.MDagPath, 
            OpenMaya.MFn.kMeshVertComponent, 
            OpenMaya.MIntArray
            OpenMaya.MDoubleArray, 
        )
        """
        # convert selection to normal lists
        before = [
            self.beforeSelection[i] 
            for i in range(self.beforeSelection.length())
        ]
        after = [
            self.afterSelection[i] 
            for i in range(self.afterSelection.length())
        ]
        
        # get difference between two lists
        difference = list(set(before) - set(after))
        if not difference:
            return
        
        # get component
        component = utils.asComponent(difference)
        
        # get original weights
        weightsO, influences = utils.getSkinWeights(
            self.dag, 
            self.skinCluster, 
            component
        )
        
        # calculate new weights
        weightsN, influences = self.calculateWeights( 
            weightsO,
            influences
        )
        
        # set weights
        self.skinCluster.setWeights(
            self.dag, 
            component, 
            influences, 
            weightsN, 
            1
        )
        
        return [
            self.skinCluster, 
            self.dag, 
            component, 
            influences, 
            weightsO
        ]

# ----------------------------------------------------------------------------

manager = RemoveInfluenceCtxManager()      

# ----------------------------------------------------------------------------
    
class RemoveInfluenceCtxInitialize(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
 
    def doIt(self, args):
        mesh = args.asString(0)
        influence = args.asString(1)
        
        manager.initialize(mesh, influence)
        manager.select()

def creatorInitialize():     
    return OpenMayaMPx.asMPxPtr(RemoveInfluenceCtxInitialize())
    
def syntaxInitialize():  
    syntax = OpenMaya.MSyntax()  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    return syntax
    
# ----------------------------------------------------------------------------
            
class RemoveInfluenceCtxBefore(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
 
    def doIt(self, args):  
        self.beforeSelection = manager.storeBeforeSelection()
        
    def undoIt(self):
        manager.beforeSelection = OpenMaya.MIntArray()
        
    def redoIt(self):
        manager.beforeSelection = self.beforeSelection

    def isUndoable(self):
        return True
        
def creatorBefore():     
    return OpenMayaMPx.asMPxPtr(RemoveInfluenceCtxBefore())
    
def syntaxBefore():  
    return OpenMaya.MSyntax()  
    
# ----------------------------------------------------------------------------
    
class RemoveInfluenceCtxAfter(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
 
    def doIt(self, args):      
        self.afterSelection = manager.storeAfterSelection()
        self.data = manager.setWeights()
        
    def undoIt(self):
        if not self.data or not all(self.data):
            return
            
        skinCluster, dag, component, influences, weights = self.data
        skinCluster.setWeights(dag, component, influences, weights, 1)
        
    def redoIt(self):
        manager.afterSelection = self.afterSelection
        self.data = manager.setWeights()

    def isUndoable(self):
        return True
            
def creatorAfter():     
    return OpenMayaMPx.asMPxPtr(RemoveInfluenceCtxAfter())
    
def syntaxAfter():  
    return OpenMaya.MSyntax()  
    
# ----------------------------------------------------------------------------

def initializePlugin( obj ):
    plugin = OpenMayaMPx.MFnPlugin(obj, __author__, __version__, "Any")
        
    # get all commands
    commands = [
        (CONTEXT_INITIALIZE, creatorInitialize, syntaxInitialize),
        (CONTEXT_BEFORE, creatorBefore, syntaxBefore),
        (CONTEXT_AFTER, creatorAfter, syntaxAfter),
    ]
    
    # register all commands
    for command, creator, syntax in commands:
        try:            
            plugin.registerCommand(command, creator, syntax)
        except:         
            raise RuntimeError("Failed to register : {0}".format(command))
    
 
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    
    # get all commands
    commands = [
        CONTEXT_INITIALIZE,
        CONTEXT_BEFORE,
        CONTEXT_AFTER
    ]
    
    # unregister all commands
    for command in commands:
        try:            
            plugin.deregisterCommand(command)
        except:         
            raise RuntimeError("Failed to unregister : {0}".format(command))
    