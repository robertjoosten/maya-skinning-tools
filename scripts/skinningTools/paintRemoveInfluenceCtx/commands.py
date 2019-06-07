from maya import cmds
from ..utils import decorator


# ----------------------------------------------------------------------------


CONTEXT = "paintRemoveInfluenceCtx"
CONTEXT_INITIALIZE = "paintRemoveInfluenceCtxInitialize"
CONTEXT_BEFORE = "paintSmoothWeightsCtxBefore"
CONTEXT_AFTER = "paintSmoothWeightsCtxAfter"


# ----------------------------------------------------------------------------


@decorator.loadPlugin("paintRemoveInfluenceCtxCommands.py")
def paint(mesh, influence):
    """
    Initialize the remove influence context. Once this command is run the 
    context will be set as the active tool.
    
    :param str mesh:
    :param str influence:
    """
    # initialize paint tool
    cmds.paintRemoveInfluenceCtxInitialize(
        mesh,
        influence
    )
    
    # initialize context
    if not cmds.artSelectCtx(CONTEXT, query=True, exists=True):
        cmds.artSelectCtx(CONTEXT)
            
    cmds.artSelectCtx( 
        CONTEXT, 
        edit=True, 
        beforeStrokeCmd=CONTEXT_BEFORE,
        afterStrokeCmd=CONTEXT_AFTER,
        selectop="unselect", 
        outwhilepaint=True,
        brushfeedback=False 
    )
     
    # set tool
    cmds.setToolTo(CONTEXT)
