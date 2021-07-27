# remove-weights-context
<img align="right" src="../../../../icons/ST_paintRemoveWeightsCtx.png?raw=true">
Remove a specific influence on vertices with the paint tool.
<p align="center"><img src="../../../../docs/_images/remove-weights-context-example.png?raw=true"></p>
<a href="https://vimeo.com/122189210" target="_blank"><p align="center">Click for video</p></a>

##Installation
* Extract the content of the .rar file anywhere on disk.
* Drag the skinning-tools.mel file in Maya to permanently install the script.

## Note
The paint tool calls a script that will select all the vertices that are influenced by the parsed influence. You can then paint away the influence on those vertices with the paint tool.
* Undo-able / Redo-able
        
Based on the settings on the skinCluster the following attribute will be respected while removing the influence weights:
* Normalize Weights
* Locked Influences

If you are working with a mesh that contains many influences it is possible to filter then using the search box.