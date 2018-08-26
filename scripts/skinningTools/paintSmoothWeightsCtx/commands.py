from maya import cmds
from .. import decorators


# ----------------------------------------------------------------------------


CONTEXT = "paintSmoothWeightsCtx"
CONTEXT_INITIALIZE = "paintSmoothWeightsCtxInitialize"
CONTEXT_UPDATE = "paintSmoothWeightsCtxUpdate"


# ----------------------------------------------------------------------------

@decorators.loadPlugin("paintSmoothWeightsCtxCommands.py")
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
