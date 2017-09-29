from maya import cmds, OpenMaya, OpenMayaMPx, OpenMayaAnim

# ----------------------------------------------------------------------------

def asMObject(path):
    """
    str -> OpenMaya.MObject

    :param str path: Path to Maya object
    :rtype: OpenMaya.MObject
    """
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(path)
    
    obj = OpenMaya.MObject()
    selectionList.getDependNode(0, obj)
    return obj
    
def asMDagPath(obj):
    """
    OpenMaya.MObject -> OpenMaya.MDagPath

    :param OpenMaya.MObject obj:
    :rtype: OpenMaya.MDagPath
    """
    return OpenMaya.MDagPath.getAPathTo(obj)
    
def asMFnSkinCluster(obj):
    """
    OpenMaya.MObject -> OpenMaya.MFnSkinCluster

    :param OpenMaya.MObject obj:
    :rtype: OpenMaya.MFnSkinCluster
    """
    iter = OpenMaya.MItDependencyGraph(
        obj, 
        OpenMaya.MFn.kSkinClusterFilter, 
        OpenMaya.MItDependencyGraph.kUpstream
    )
    
    while not iter.isDone():
        return OpenMayaAnim.MFnSkinCluster(iter.currentItem())
        
# ----------------------------------------------------------------------------
        
def asMIntArray(index):
    """
    index -> OpenMaya.MIntArray
    
    :param int/OpenMaya.MIntArray index: indices
    :return: Array of indices
    :rtype: OpenMaya.MIntArray
    """
    if type(index) != OpenMaya.MIntArray:
        array = OpenMaya.MIntArray()
        array.append(index)
        return array

    return index

# ----------------------------------------------------------------------------
        
def asComponent(index):
    """
    index -> OpenMaya.MFn.kMeshVertComponent
    
    :param int/OpenMaya.MIntArray index: indices to create component for
    :return: Initialized component(s)
    :rtype: OpenMaya.MFn.kMeshVertComponent
    """
    # convert input to an MIntArray if it not already is one
    indices = asMIntArray(index)
    
    # initialize component(s)
    t = OpenMaya.MFn.kMeshVertComponent
    component = OpenMaya.MFnSingleIndexedComponent().create(t)
    OpenMaya.MFnSingleIndexedComponent(component).addElements(indices)
    return component
    
def getConnectedVertices(dag, component):
    """
    index -> OpenMaya.MFn.kMeshVertComponent
    
    :param OpenMaya.MDagPath dag:
    :param OpenMaya.MFn.kMeshVertComponent component:
    :return: Initialized component(s), number of connected vertices
    :rtype: tuple(OpenMaya.MFn.kMeshVertComponent, int)
    """
    connected = OpenMaya.MIntArray()
        
    # get connected vertices
    iter = OpenMaya.MItMeshVertex(dag, component)
    iter.getConnectedVertices(connected)
    
    # get component of connected vertices
    component = asComponent(connected)
    return component, len(connected)
    
def getSkinWeights(dag, skinCluster, component):
    """
    Get the skin weights of the original vertex and of its connected vertices.
    
    :param OpenMaya.MDagPath dag:
    :param OpenMayaAnim.MFnSkinCluster skinCluster:
    :param OpenMaya.MFn.kMeshVertComponent component:
    :return: skin weights and number of influences
    :rtype: tuple(OpenMaya.MDoubleArray, int)
    """
    # weights variables
    weights = OpenMaya.MDoubleArray()
    
    # influences variables
    influenceMSU = OpenMaya.MScriptUtil()
    influencePTR = influenceMSU.asUintPtr()
    
    # get weights
    skinCluster.getWeights(dag, component, weights, influencePTR)
    
    # get num influences
    num = OpenMaya.MScriptUtil.getUint(influencePTR)
    
    return weights, num