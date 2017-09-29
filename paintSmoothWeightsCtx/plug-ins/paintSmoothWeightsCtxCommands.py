from maya import cmds, OpenMaya, OpenMayaMPx, OpenMayaAnim
from rjSkinningTools import utils

__author__    = "Robert Joosten"
__version__   = "0.9.0"
__email__     = "rwm.joosten@gmail.com"

# ----------------------------------------------------------------------------

CONTEXT_INITIALIZE = "paintSmoothWeightsCtxInitialize"
CONTEXT_UPDATE = "paintSmoothWeightsCtxUpdate"

# ----------------------------------------------------------------------------

class SmoothWeightsCtxManager(object):
    def __init__(self):
        self.reset()
        
    # ------------------------------------------------------------------------
    
    def reset(self):
        self._obj = None
        self._dag = None
        self._skinCluster = None
        
        self._maxInfluences = 0
        self._normalizeMode = 0
        self._maintainMaxInfluences = False
        
        self._influences = OpenMaya.MDagPathArray()
        self._influencesLocked = []
    
    def initialize(self, obj):
        # if no obj reset variables
        if not obj:
            self.reset()
            return 

        # get object data
        self._obj = utils.asMObject(obj)
        self._dag = utils.asMDagPath(self.obj)
        
        # get skin cluster
        self._skinCluster = utils.asMFnSkinCluster(self.obj)
        
        # get skin cluster data
        maxPlug = self.skinCluster.findPlug("maxInfluences")
        normalPlug = self.skinCluster.findPlug("normalizeWeights")
        maintainPlug = self.skinCluster.findPlug("maintainMaxInfluences")
        
        self._maxInfluences = maxPlug.asInt()
        self._normalizeMode = normalPlug.asInt()
        self._maintainMaxInfluences = maintainPlug.asBool()
        
        # get influences
        self._influences = OpenMaya.MDagPathArray()
        self.skinCluster.influenceObjects(self._influences)
            
        # get locked influences
        self._influencesLocked = []
        for i in range(self.influences.length()):
            path = self.influences[i].fullPathName()
            locked = cmds.getAttr("{0}.liw".format(path))
            
            self._influencesLocked.append(locked)

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
    def maxInfluences(self):
        return self._maxInfluences

    @property
    def normalizeMode(self): 
        return self._normalizeMode
        
    @property
    def maintainMaxInfluences(self): 
        return self._maintainMaxInfluences
    
    # ------------------------------------------------------------------------
    
    @property
    def influences(self): 
        return self._influences
        
    @property
    def influencesLocked(self): 
        return self._influencesLocked
               
    # ------------------------------------------------------------------------
        
    def calculateWeights(self, value, weightsO, weightsC, numI, numC):
        """
        Calculate the new weights of the parsed index. The new weights are 
        calculated by blending the weights of the connected vertices, this is 
        done with the factor of the value. The value is parsed by the context
        and can range from 0-1 depending on where the point is in the paint 
        brush. Locked influences, normalization and maintaining maximum
        influences are taken into account as they are set on the skin cluster.
        
        :param float value: Blend factor
        :param OpenMaya.MDoubleArray weightsO: Weights of original
        :param OpenMaya.MDoubleArray weightsC: Weights of connected
        :param int numI: Influences of original
        :param int numC: Influences of connected
        :return: New weights, new influences
        :rtype: tuple(OpenMaya.MDoubleArray, OpenMaya.MIntArray)
        """
        # weight variables
        weightsNew = OpenMaya.MDoubleArray()
        influenceNew = OpenMaya.MIntArray()
        
        # blend weights
        for i in range(numI):
            influenceNew.append(i)
            weightsNew.append(0.0)
            
            # if influence is locked dont change value
            if self.influencesLocked[i]:
                weightsNew[i] = weightsO[i]
                continue
            
            # blend weights with connected vertices
            for j in range(i, len(weightsC), numI):
                w = ((weightsO[i]/numC)*(1-value))+((weightsC[j]/numC)*value)
                weightsNew[i] += w
         
        # force max influences by removing excess weights
        if self.maintainMaxInfluences:
            weights = zip(weightsNew, influenceNew)
            excess = sorted(weights, reverse=True)[self.maxInfluences:]
            for e in excess:    
                weightsNew[e[1]] = 0.0
                
        # normalize weights to one
        if self.normalizeMode == 1:
            # get total locked weights
            lockedTotal = sum(
                [
                    weightsNew[i] 
                    for i in range(weightsNew.length()) 
                    if self.influencesLocked[i] 
                ]
            )
            
            # get total to blend
            total = sum(weightsNew) - lockedTotal
            
            # get multiply factor
            if lockedTotal >= 1.0 or total == 0.0:
                factor = 0
            else:
                factor = (1.0-lockedTotal)/total            
            
            # apply multiply factor
            for i in range(weightsNew.length()):
                if self.influencesLocked[i]:
                    continue
                    
                weightsNew[i] = weightsNew[i] * factor

        return weightsNew, influenceNew

    # ------------------------------------------------------------------------
        
    def setWeights(self, index, value):
        """
        Calculate and set new weights of the vertex with the blend factor. 
        This function will return the previous weights data for undo purposes.
        
        :param int index: Vertex number
        :param float value: Blend factor
        :return: Skin cluster, dag, component, influences, old weights
        :rtype: list(
            OpenMayaAnim.MFnSkinCluster, 
            OpenMaya.MDagPath, 
            OpenMaya.MFn.kMeshVertComponent, 
            OpenMaya.MDoubleArray, 
            OpenMaya.MIntArray
        )
        """
        # check if manager is initialized
        if not self.obj:
            return [None]*5

        # get components
        component = utils.asComponent(index)
        componentConnected, componentCount = utils.getConnectedVertices(
            self.dag, 
            component
        )
        
        # get current weights
        weightsO, _ = utils.getSkinWeights(
            self.dag, 
            self.skinCluster, 
            component, 
        )
        
        # get connected weights
        weightsC, influences = utils.getSkinWeights(
            self.dag, 
            self.skinCluster, 
            componentConnected
        )
        
        # calculate new weights
        weightsN, influencesN = self.calculateWeights(
            value, 
            weightsO, 
            weightsC, 
            influences, 
            componentCount
        )      

        # set new weights
        self.skinCluster.setWeights(
            self.dag, 
            component, 
            influencesN, 
            weightsN, 
            1 
        )
        
        # return data for undo
        return [self.skinCluster, self.dag, component, influencesN, weightsO]

# ----------------------------------------------------------------------------

manager = SmoothWeightsCtxManager()      

# ----------------------------------------------------------------------------
    
class SmoothWeightsCtxInitialize(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
 
    def doIt( self, args ):
        obj = args.asString(0)
        manager.initialize(obj)

def creatorInitialize():     
    return OpenMayaMPx.asMPxPtr(SmoothWeightsCtxInitialize())
    
def syntaxInitialize():  
    syntax = OpenMaya.MSyntax()  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    return syntax
    
# ----------------------------------------------------------------------------
            
class SmoothWeightsCtxUpdate(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
 
    def doIt( self, args ):            
        self.index = args.asInt(1)
        self.value = args.asDouble(2)
        
        self.data = manager.setWeights(self.index, self.value)

    def undoIt(self):
        if not all(self.data):
            return
            
        skinCluster, dag, component, influences, weights = self.data
        skinCluster.setWeights(dag, component, influences, weights, 1)
            
    def redoIt(self):
        if not self.index or not self.value:
            return
            
        self.data = manager.setWeights(self.index, self.value)
        
    # ------------------------------------------------------------------------
 
    def isUndoable(self):
        return True

def creatorUpdate():       
    return OpenMayaMPx.asMPxPtr(SmoothWeightsCtxUpdate())
    
def syntaxUpdate():  
    syntax = OpenMaya.MSyntax()  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    syntax.addArg(OpenMaya.MSyntax.kDouble)  
    return syntax  

# ----------------------------------------------------------------------------

def initializePlugin( obj ):
    plugin = OpenMayaMPx.MFnPlugin(obj, __author__, __version__, "Any")
        
    # get all commands
    commands = [
        (CONTEXT_INITIALIZE, creatorInitialize, syntaxInitialize),
        (CONTEXT_UPDATE, creatorUpdate, syntaxUpdate),
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
        CONTEXT_UPDATE
    ]
    
    # unregister all commands
    for command in commands:
        try:            
            plugin.deregisterCommand(command)
        except:         
            raise RuntimeError("Failed to unregister : {0}".format(command))
    