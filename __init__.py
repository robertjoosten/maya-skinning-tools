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
    