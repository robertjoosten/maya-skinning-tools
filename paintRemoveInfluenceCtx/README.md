# paintRemoveInfluenceCtx
<img align="right" src="https://github.com/robertjoosten/rjSkinningTools/blob/master/icons/paintRemoveInfluenceCtx.png">
Remove influences on vertices with the paint tool.
<a href="https://vimeo.com/122189210" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjSkinningTools** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Select a skinned object and run the following code:
```python
from rjSkinningTools import paintRemoveInfluenceCtx;
paintRemoveInfluenceCtx.paint(mesh, influence)
```

Display UI:
```python
import rjSkinningTools.paintRemoveInfluenceCtx.ui;
rjSkinningTools.paintRemoveInfluenceCtx.ui.show()
```
 
## Note
The paint tool calls a script that will select all the vertices that are influenced by the parsed influence. You can then paint away the influence on those vertices with the paint tool.
* Undo-able / Redo-able
        
Based on the settings on the skinCluster the following attribute will be respected while removing the influence weights:
* Normalize Weights
* Locked Influences