import logging
from maya import mel
from maya import cmds


log = logging.getLogger(__name__)
ROOT_PACKAGE = __name__.rsplit(".", 1)[0]

PAINT_SMOOTH_WEIGHTS_COMMAND = """
import {0}.tools.smooth_weights_context
{0}.tools.smooth_weights_context.paint()
""".format(ROOT_PACKAGE)

PAINT_REMOVE_INFLUENCE_COMMAND = """
import {0}.tools.remove_weights_context.ui
{0}.tools.remove_weights_context.ui.show()
""".format(ROOT_PACKAGE)

INITIALIZE_WEIGHTS_COMMAND = """
import {0}.tools.initialize_weights.ui
{0}.tools.initialize_weights.ui.show()
""".format(ROOT_PACKAGE)

MIRROR_WEIGHTS_COMMAND = """
import {0}.tools.mirror_weights.ui
{0}.tools.mirror_weights.ui.show()
""".format(ROOT_PACKAGE)

CONVERT_SOFT_SELECTION_COMMAND = """
import {0}.tools.soft_selection_weights.ui
{0}.tools.soft_selection_weights.ui.show()
""".format(ROOT_PACKAGE)

TWEAK_WEIGHT_COMMAND = """
import {0}.tools.tweak_weights.ui
{0}.tools.tweak_weights.ui.show()
""".format(ROOT_PACKAGE)

DELINEAR_WEIGHTS_COMMAND = """
import {0}.tools.delinear_weights.ui
{0}.tools.delinear_weights.ui.show()
""".format(ROOT_PACKAGE)

PROJECTION_PLANE_COMMAND = """
import {0}.tools.projection_plane.ui
{0}.tools.projection_plane.ui.show()
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
        "image1": "ST_paintRemoveWeightsCtx.png",
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
        "label": "mirrorWeights",
        "command": MIRROR_WEIGHTS_COMMAND,
        "annotation": "Mirror skin weights using topology",
        "image1": "ST_mirrorWeights.png",
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
        "label": "tweakWeights",
        "command": TWEAK_WEIGHT_COMMAND,
        "annotation": "Tweak Influences on a component level",
        "image1": "ST_tweakWeights.png",
        "sourceType": "python"
    },
    {
        "label": "delinearWeights",
        "command": DELINEAR_WEIGHTS_COMMAND,
        "annotation": "De-linearize skin weights",
        "image1": "ST_delinearWeights.png",
        "sourceType": "python"
    },
    {
        "label": "projectionPlane",
        "command": PROJECTION_PLANE_COMMAND,
        "annotation": "Create projection planes from selection joints",
        "image1": "ST_projectionPlane.png",
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
