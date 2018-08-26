from maya import cmds
from .. import utils


def getSkinnedVertices():
    """
    Get all of the skinned vertices that are currently selected. Loop over the
    current selection and see if the vtx suffix is found indicating a 
    component selection. Then the mesh if extracted from this component and 
    checked if a skinCluster is attached. If the selection meets these 
    criteria it will be added to the list.
    
    :return: List of selected skinned vertices
    :rtype: list of strings
    """
    skinnedVertices = []
    selection = cmds.ls(sl=True, fl=True, l=True) or []
    
    for sel in selection:
        if not sel.count(".vtx"):
            continue
            
        mesh, _ = sel.split(".", 1)
        if utils.getSkinCluster(mesh):
            skinnedVertices.append(sel)
            
    return skinnedVertices
