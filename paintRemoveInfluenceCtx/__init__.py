"""	
Remove a specific influence on vertices with the paint tool.

.. figure:: https://github.com/robertjoosten/rjSkinningTools/raw/master/paintRemoveInfluenceCtx/README.png
   :align: center
   
`Link to Video <https://vimeo.com/122189210>`_

Installation
============
Copy the **rjSkinningTools** folder to your Maya scripts directory
::
    C:/Users/<USER>/Documents/maya/scripts

Usage
=====
Select a skinned object and run the following code
::
    from rjSkinningTools import paintRemoveInfluenceCtx;
    paintRemoveInfluenceCtx.paint(mesh, influence)

Display UI
::
    import rjSkinningTools.paintRemoveInfluenceCtx.ui;
    rjSkinningTools.paintRemoveInfluenceCtx.ui.show()
    
Note
====
The paint tool calls a script that will select all the vertices that are 
influenced by the parsed influence. You can then paint away the influence 
on those vertices with the paint tool.
    * Undo-able / Redo-able
        
Based on the settings on the skinCluster the following attribute will be 
respected while removing the influence weights:
    * Normalize Weights
    * Locked Influences    

Code
====
"""

__author__    = "Robert Joosten"
__version__   = "0.8.1"
__email__     = "rwm.joosten@gmail.com"

from maya import cmds
import os

# ----------------------------------------------------------------------------

CONTEXT = "paintRemoveInfluenceCtx"
CONTEXT_INITIALIZE = "paintRemoveInfluenceCtxInitialize"
CONTEXT_BEFORE = "paintSmoothWeightsCtxBefore"
CONTEXT_AFTER = "paintSmoothWeightsCtxAfter"

# ----------------------------------------------------------------------------

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
        "paintRemoveInfluenceCtxCommands.py"
    )

    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    registered = cmds.pluginInfo(plugin, q=True, registered=True)
    
    if not registered or not loaded:
        cmds.loadPlugin(plugin)
    
if __name__ != "__builtin__":
    loadPlugin()