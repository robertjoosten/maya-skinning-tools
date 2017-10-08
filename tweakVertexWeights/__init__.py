"""					
I N S T A L L A T I O N:
    Copy the "rjSkinningTools" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts

U S A G E:
    Display UI:  
        import rjSkinningTools.tweakVertexWeights.ui
        rjSkinningTools.tweakVertexWeights.ui.show()

N O T E:
    Tweak vertex weights with sliders or spinbox input fields. This tool will
    give the user a good overview of what influences are translating the 
    vertex. At the same time being able to tweak those influence to a 0.001 
    of precision, while setting the locked state of certain influences. It 
    also shows if the maximum amount of influences is exceeded. The ui gets 
    updated every time the selection is changed in Maya.
"""

from maya import cmds, mel
from rjSkinningTools import utils

__author__    = "Robert Joosten"
__version__   = "0.8.1"
__email__     = "rwm.joosten@gmail.com"

# ----------------------------------------------------------------------------

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