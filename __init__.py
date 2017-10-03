"""					
I N S T A L L A T I O N:
    Copy the "rjSkinningTools" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts

U S A G E:
    Add skinning shelf:
        import rjSkinningTools
        rjSkinningTools.install()

T O O L S
    paintSmoothWeightsCtx:
        Paint smooth weights tool in Maya using the weights of neighbouring 
        vertices.
    paintRemoveInfluenceCtx:
        Remove a specific influence on vertices with the paint tool.
"""

from maya import cmds, mel
from . import ui

__author__    = "Robert Joosten"
__email__     = "rwm.joosten@gmail.com"

from maya import cmds, mel
from . import ui

TOOLS = [
    {
        "label":"paintSkinWeights",
        "command":"ArtPaintSkinWeightsTool;",
        "annotation":"Paint Skin Weights Tool: Paint weights on smooth bound skins",
        "image1":ui.findIcon("paintSkinWeightsCtx.png"),
        "sourceType":"mel"
    },
    {
        "label":"paintSmoothWeights",
        "command":"from rjSkinningTools import paintSmoothWeightsCtx; paintSmoothWeightsCtx.paint()",
        "annotation":"Paint Smooth Weights Tool: Smooth weights on smooth bound skins",
        "image1":ui.findIcon("paintSmoothWeightsCtx.png"),
        "sourceType":"python"
    },
    {
        "label":"paintRemoveInfluence",
        "command":"import rjSkinningTools.paintRemoveInfluenceCtx.ui; rjSkinningTools.paintRemoveInfluenceCtx.ui.show()",
        "annotation":"Paint Remove Influence Tool: Remove influence on smooth bound skins",
        "image1":ui.findIcon("paintRemoveInfluenceCtx.png"),
        "sourceType":"python"
    },
    {
        "label":"tweakVertexWeights",
        "command":"import rjSkinningTools.tweakVertexWeights.ui; rjSkinningTools.tweakVertexWeights.ui.show()",
        "annotation":"Tweak Influences on a vertex level",
        "image1":ui.findIcon("tweakVertexWeights.png"),
        "sourceType":"python"
    }
]

def install():
    """
    Add a new shelf in Maya with all the tools that are provided in the TOOLS 
    variable. If a tab already exist new buttons that weren't registered yet
    will be added to the shelf.
    """
    # get top shelf
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    
    # get top shelf names
    shelves = cmds.tabLayout(gShelfTopLevel, query=1, ca=1)
    
    # create shelf if it doesn't exist yet
    if not __name__ in shelves:
        cmds.shelfLayout(__name__, parent=gShelfTopLevel)
  
    # get existing members
    existing = cmds.shelfLayout(__name__, query=True, childArray=True ) or []
    existing = [cmds.shelfButton(e, query=True, label=True) for e in existing]
    
    # add modules
    for tool in TOOLS:
        if tool.get("label") in existing:
            continue
        
        if tool.get("image1"):
            cmds.shelfButton(style = "iconOnly", parent = __name__, **tool)
        else:
            cmds.shelfButton(style = "textOnly", parent = __name__, **tool)
    
