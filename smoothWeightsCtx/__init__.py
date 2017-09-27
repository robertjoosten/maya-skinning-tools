from maya import cmds
import os

# ----------------------------------------------------------------------------

CONTEXT = "smoothWeightsCtx"
CONTEXT_INITIALIZE = "smoothWeightsCtxInitialize"
CONTEXT_UPDATE = "smoothWeightsCtxUpdate"

# ----------------------------------------------------------------------------

def paint():
    """
    Initialize the smooth weight context, make sure to have a mesh selected 
    with a skin cluster attached to it. Once this command is run the context
    will be set as the active tool.
    """
    if not cmds.artUserPaintCtx(CONTEXT, query=True, exists=True):
        cmds.artUserPaintCtx(CONTEXT)
            
    cmds.artUserPaintCtx(
        CONTEXT, 
        edit=True, 
        ic=CONTEXT_INITIALIZE, 
        svc=CONTEXT_UPDATE, 
        whichTool="userPaint", 
        fullpaths=True,
        outwhilepaint=True,
        brushfeedback=False,
        selectedattroper="additive"
    )

    cmds.setToolTo(CONTEXT)
    
# ----------------------------------------------------------------------------

def loadPlugin():
    """
    When this script is imported the following code will make sure the 
    accompanying plugin is loaded that registers the commands used by the 
    context.
    """
    plugin = os.path.join(
        os.path.dirname(__file__), 
        "plug-in", 
        "smoothWeightsCtxCommands.py"
    )

    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    registered = cmds.pluginInfo(plugin, q=True, registered=True)
    
    if not registered or not loaded:
        cmds.loadPlugin(plugin)
    
if __name__ != "__builtin__":
    loadPlugin()