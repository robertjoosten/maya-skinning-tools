from maya import cmds, OpenMayaAnim
from ..utils import (
    api,
    path,
    skin,
    undo,
    weight,
    tweening,
    selection,
    conversion
)


def deLinearSkinWeightsOnSelection(method):
    """
    All of the selected vertices will be queried, these vertices will then be
    parsed to the :func:`deLinearSkinWeights` function that will process the
    weights.
    
    :param str method: De-linearization method
    """
    # get skinned meshes
    meshes = selection.getSkinnedMeshesFromSelection()

    # split objects from components
    objects, components = selection.splitComponents(meshes, ".vtx")

    # extend components with vertex components of objects
    for obj in objects:
        components.extend(conversion.meshToVertices(obj))

    # delinearize weights
    deLinearSkinWeights(components, method)


def deLinearSkinWeights(vertices, method):
    """
    Loop over all of the provided vertices. Loop over all of the vertices and 
    see if these vertices are deformed by a skin cluster. If this is the case, 
    the weights will be de-linearized by the function provided. This function
    is found in the tweening module.
    
    :param list vertices: List of vertices
    :param str method: De-linearization method
    """
    func = tweening.getTweeningMethod(method)
    if not func:
        raise ValueError("Tweening method is not supported.")

    objects = list(set([vtx.split(".")[0] for vtx in vertices]))
    
    with undo.UndoChunkContext():
        for obj in objects:
            # get skin cluster
            sk = skin.getSkinCluster(obj)
            if not sk:
                continue
            
            # get indices
            indices = [
                conversion.componentIndexFromString(vtx)
                for vtx in vertices 
                if vtx.startswith(obj)
            ]
            
            # get api objects
            meshObj = api.asMObject(obj)
            meshDag = api.asMDagPath(meshObj)
            meshDag.extendToShape()
            
            skObj = api.asMObject(sk)
            skMfn = OpenMayaAnim.MFnSkinCluster(skObj)
            
            # get weights
            components = api.asComponent(indices)
            weightsAll, num = api.getSkinWeights(
                meshDag, 
                skMfn, 
                components
            )
            
            # split weights
            weightChunks = path.asChunks(weightsAll, num)

            for i, weights in enumerate(weightChunks):
                # calculate per vertex weights
                weights = weight.normalizeWeights(weights)
                weights = [func(w) for w in weights]
                weights = weight.normalizeWeights(weights)
                
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
