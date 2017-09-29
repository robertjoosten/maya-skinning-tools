"""					
I N S T A L L A T I O N:
    Copy the "rjSkinningTools" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts
        
U S A G E:
    Select a skinned object and run the following code:
        from rjSkinningTools import paintSmoothWeightsCtx;
        paintSmoothWeightsCtx.paint()
    
N O T E:
    The paint tool calls a script that find the surrounding vertices and its 
    skin weights. These skin weights are then blended with the skin weights 
    of the original vertex based value of the paint tool.
        * Undo-able / Redo-able

    Based on the settings on the skinCluster the following attribute will be 
    respected while smoothing the weights:
        * Max Influences
        * Normalize Weights
        * Locked Influences

    I would like to note that the idea for this script came from 
    `Tom Ferstl <https://vimeo.com/tomferstl>` he developed a script where 
    the end results is very simular. I did use the original script as an 
    inspiration, but what happens under the hood is completely different.
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