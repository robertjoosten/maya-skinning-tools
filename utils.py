from maya import cmds, OpenMaya, OpenMayaMPx, OpenMayaAnim

# ----------------------------------------------------------------------------

class UndoChunkContext(object):
    """
    The undo context is used to combine a chain of commands into one undo.
    Can be used in combination with the "with" statement.
    
    with UndoChunkContext():
        # code
    """
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        
    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

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
    
    :param int/list of ints/OpenMaya.MIntArray index: indices
    :return: Array of indices
    :rtype: OpenMaya.MIntArray
    """
    if type(index) != OpenMaya.MIntArray:
        array = OpenMaya.MIntArray()
        if type(index) == list:
            for i in index:
                array.append(i)
        else:
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
    
def getInfluences(skinCluster):
    """
    Get all of the influence data connected to the skinCluster. This is a 
    OpenMaya.MDagPathArray, OpenMaya.MIntArray() and a regular list of partial
    names.
    
    :param OpenMaya.MFnSkinCluster skinCluster:
    :return: Dag paths, integer and partial names
    :rtype: tuple(
        OpenMaya.MDagPathArray
        OpenMaya.MIntArray
        list of strings
    )
    """
    # variables
    influencesDag = OpenMaya.MDagPathArray()
    influencesI = OpenMaya.MIntArray()
    influencesN = []
    
    # get influences
    skinCluster.influenceObjects(influencesDag)
    
    # get influences data
    for i in range(influencesDag.length()):
        influencesI.append(i)
        influencesN.append(influencesDag[i].partialPathName())

    return influencesDag, influencesI, influencesN
    
# ----------------------------------------------------------------------------

def getSkinCluster(mesh):
    """
    Loop over an objects history and see if a skinCluster node is part of the
    history.

    :param str mesh:
    :return: skinCluster that is attached to the parsed mesh
    :rtype: str or None
    """
    skinClusters = [ 
        h 
        for h in cmds.listHistory(mesh) or [] 
        if cmds.nodeType(h) == "skinCluster" 
    ]
    
    if skinClusters: 
        return skinClusters[0]
        
# ----------------------------------------------------------------------------
        
def addInfluences(skinCluster, influences):
    """
    Add influences to the skin cluster. Expects full path influences. Will
    try to reach the bind pose before attached the new influences to the skin
    cluster.

    :param str skinCluster:
    :param list influences:
    """
    # get existing influences
    existing = cmds.skinCluster(skinCluster, query=True, influence=True)
    existing = cmds.ls(existing, l=True)
    
    # try restoring dagpose
    try:    cmds.dagPose(existing, restore=True, g=True, bindPose=True)
    except: cmds.warning("Unable to reach dagPose!")
    
    # add influences
    for influence in influences:
        if not influence in existing:
            cmds.skinCluster(
                skinCluster, 
                edit=True, 
                addInfluence=influence, 
                weight=0.0
            )
      
# ----------------------------------------------------------------------------

def isMesh(mesh):
    """
    :param str mesh:
    :return: if the parsed object is a mesh.
    :rtype: bool
    """
    return cmds.nodeType(mesh) == "mesh"
    
def isSkinned(mesh):
    """
    :param str mesh:
    :return: if the parsed object is a skinned mesh.
    :rtype: bool
    """
    if not isMesh(mesh):
        return False
        
    return getSkinCluster(mesh) != None
    
# ----------------------------------------------------------------------------

def getMeshesFromSelection():
    """
    Loop over the current selection, excluding intermediate shapes. If the 
    current selected object is not a mesh. The selection will be extended with
    the shapes of that object.
    
    :return: List of meshes
    :rtype: list of strings
    """
    meshes = []
    selection = cmds.ls(sl=True, l=True, noIntermediate=True)
    
    for sel in selection:
        # check if mesh
        if isMesh(sel):
            meshes.append(sel)
            continue
            
        # extend to shapes
        shapes = [
            shape
            for shape in cmds.listRelatives(sel, shapes=True, ni=True) or []
            if isMesh(shape) 
        ]
        meshes.extend(shapes)
        
    return meshes
    
def getSkinnedMeshesFromSelection():
    """
    Loop over the current selection, excluding intermediate shapes. If the 
    current selected is a mesh and has a skin cluster attached to it. The 
    selection will be extended with the shapes of that object.
    
    :return: List of skinned meshes
    :rtype: list of strings
    """
    return [
        mesh
        for mesh in getMeshesFromSelection()
        if isSkinned(mesh)  
    ]
