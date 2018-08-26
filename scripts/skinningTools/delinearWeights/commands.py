from maya import cmds, OpenMayaAnim

from . import utils as toolUtils
from .. import utils as projectUtils


def deLinearSkinWeightsOnSelection(method):
    """
    All of the selected vertices will be queried, these vertices will then be
    parsed to the :func:`deLinearSkinWeights` function that will process the
    weights.
    
    :param str method: De-linearization method
    """
    vertices = toolUtils.getSelectedVertices()
    deLinearSkinWeights(vertices, method)


def deLinearSkinWeights(vertices, method):
    """
    Loop over all of the provided vertices. Loop over all of the vertices and 
    see if these vertices are deformed by a skin cluster. If this is the case, 
    the weights will be de-linearized by the function provided. This function
    is found in the tweening module.
    
    :param list vertices: List of vertices
    :param str method: De-linearization method
    """
    func = toolUtils.getTweeningMethod(method)
    if not func:
        raise ValueError("Tweening method is not supported.")

    objects = list(set([vtx.split(".")[0] for vtx in vertices]))
    
    with projectUtils.UndoChunkContext():
        for obj in objects:
            # get skin cluster
            sk = projectUtils.getSkinCluster(obj)
            if not sk:
                continue
            
            # get indices
            indices = [
                toolUtils.getIndexFromString(vtx)
                for vtx in vertices 
                if vtx.startswith(obj)
            ]
            
            # get api objects
            meshObj = projectUtils.asMObject(obj)
            meshDag = projectUtils.asMDagPath(meshObj)
            meshDag.extendToShape()
            
            skObj = projectUtils.asMObject(sk)
            skMfn = OpenMayaAnim.MFnSkinCluster(skObj)
            
            # get weights
            components = projectUtils.asComponent(indices)
            weightsAll, num = projectUtils.getSkinWeights(
                meshDag, 
                skMfn, 
                components
            )
            
            # split weights
            weightChunks = toolUtils.splitByInfluences(weightsAll, num)

            for i, weights in enumerate(weightChunks):
                # calculate per vertex weights
                weights = projectUtils.normalizeWeights(weights)
                weights = [func(w) for w in weights]
                weights = projectUtils.normalizeWeights(weights)
                
                # set weights
                for j, w in enumerate(weights):
                    cmds.setAttr(
                        "{0}.weightList[{1}].weights[{2}]".format(
                            sk, 
                            indices[i],
                            j
                        ), 
                        w
                    )
