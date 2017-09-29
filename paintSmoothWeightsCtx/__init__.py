"""					
I N S T A L L A T I O N:
    Copy the "rjSkinningTools" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts
        
U S A G E:
    Select a skinned object and run the following code:
        from rjSkinningTools import paintSmoothWeightsCtx;
        paintSmoothWeightsCtx.paint()
    
N O T E:
    I would like to note that the idea for this script came from Tom Ferstl, 
    he developed a script where the end results is very simular.

    Profile: vimeo.com/tomferstl
    Demo: vimeo.com/19802823

    I did use the original script as an inspiration, but what happens under 
    the hood is completely different.

    artUserPaintCtx only takes in mel commands, but instead of writting a 
    wrapper in mel that calls python code, I registered a new command which 
    is written in python, improving the speed. This also gives you the option 
    to add Undo and Redo functionality.

    The paint tool calls a script that find the surrounding vertices and its 
    skin weights. These skin weights are then blended with the skin weights 
    of the original vertex based value of the paint tool.

    It also takes into account the settings on your skinCluster. For real-time 
    purposes its very common to have your maintain max influences set to a 
    certain number. The same goes for normalization of the weights and the 
    locked state of influences.
"""

__author__    = "Robert Joosten"
__version__   = "0.9.0"
__email__     = "rwm.joosten@gmail.com"

from maya import cmds
import os

# ----------------------------------------------------------------------------

CONTEXT = "paintSmoothWeightsCtx"
CONTEXT_INITIALIZE = "paintSmoothWeightsCtxInitialize"
CONTEXT_UPDATE = "paintSmoothWeightsCtxUpdate"

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
        "plug-ins", 
        "paintSmoothWeightsCtxCommands.py"
    )

    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    registered = cmds.pluginInfo(plugin, q=True, registered=True)
    
    if not registered or not loaded:
        cmds.loadPlugin(plugin)
    
if __name__ != "__builtin__":
    loadPlugin()