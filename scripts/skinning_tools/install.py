import logging
from maya import mel
from maya import cmds


log = logging.getLogger(__name__)
ROOT_PACKAGE = __name__.rsplit(".", 1)[0]

PAINT_SMOOTH_WEIGHTS_COMMAND = """
import {0}.paintSmoothWeightsCtx
{0}.paintSmoothWeightsCtx.paint()
""".format(ROOT_PACKAGE)

PAINT_REMOVE_INFLUENCE_COMMAND = """
import {0}.paintRemoveInfluenceCtx.ui
{0}.paintRemoveInfluenceCtx.ui.show()
""".format(ROOT_PACKAGE)

TWEAK_VERTEX_WEIGHT_COMMAND = """
import {0}.tweakVertexWeights.ui
{0}.tweakVertexWeights.ui.show()
""".format(ROOT_PACKAGE)

INITIALIZE_WEIGHTS_COMMAND = """
import {0}.initializeWeights.ui
{0}.initializeWeights.ui.show()
""".format(ROOT_PACKAGE)

CONVERT_SOFT_SELECTION_COMMAND = """
import {0}.softSelectionToWeights.ui
{0}.softSelectionToWeights.ui.show()
""".format(ROOT_PACKAGE)

DELINEAR_WEIGHTS_COMMAND = """
import {0}.delinear_weights.ui
{0}.delinear_weights.ui.show()
""".format(ROOT_PACKAGE)

SHELF_NAME = "SkinningTools"
SHELF_TOOLS = [
    {
        "label": "paintSkinWeights",
        "command": "ArtPaintSkinWeightsTool;",
        "annotation": "Paint Skin Weights Tool: Paint weights on smooth bound skins",
        "image1": "ST_paintSkinWeightsCtx.png",
        "sourceType": "mel"
    },
    {
        "label": "paintSmoothWeights",
        "command": PAINT_SMOOTH_WEIGHTS_COMMAND,
        "annotation": "Paint Smooth Weights Tool: Smooth weights on smooth bound skins",
        "image1": "ST_paintSmoothWeightsCtx.png",
        "sourceType": "python"
    },
    {
        "label": "paintRemoveInfluence",
        "command": PAINT_REMOVE_INFLUENCE_COMMAND,
        "annotation": "Remove influence on smooth bound skins",
        "image1": "ST_paintRemoveInfluenceCtx.png",
        "sourceType": "python"
    },
    {
        "label": "tweakVertexWeights",
        "command": TWEAK_VERTEX_WEIGHT_COMMAND,
        "annotation": "Tweak Influences on a vertex level",
        "image1": "ST_tweakVertexWeights.png",
        "sourceType": "python"
    },
    {
        "label": "initializeWeights",
        "command": INITIALIZE_WEIGHTS_COMMAND,
        "annotation": "Initialize skin weights",
        "image1": "ST_initializeWeights.png",
        "sourceType": "python"
    },
    {
        "label": "softSelectionToWeights",
        "command": CONVERT_SOFT_SELECTION_COMMAND,
        "annotation": "Convert soft selection to skin weights",
        "image1": "ST_softSelectionToWeights.png",
        "sourceType": "python"
    },
    {
        "label": "delinearWeights",
        "command": DELINEAR_WEIGHTS_COMMAND,
        "annotation": "De-linearize skin weights",
        "image1": "ST_delinearWeights.png",
        "sourceType": "python"
    }
]


def execute():
    """
    Add a new shelf in Maya with all the tools that are provided in the
    SHELF_TOOLS variable. If the tab exists it will be deleted and re-created
    from scratch.
    """
    shelf_main = mel.eval("$tmpVar=$gShelfTopLevel")
    shelves = cmds.tabLayout(shelf_main, query=True, childArray=True)

    if SHELF_NAME in shelves:
        cmds.deleteUI(SHELF_NAME)

    cmds.shelfLayout(SHELF_NAME, parent=shelf_main)

    for tool in SHELF_TOOLS:
        if tool.get("image1"):
            cmds.shelfButton(style="iconOnly", parent=SHELF_NAME, **tool)
        else:
            cmds.shelfButton(style="textOnly", parent=SHELF_NAME, **tool)

    log.info("skinning-tools installed successfully.")