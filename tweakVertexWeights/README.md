# tweakVertexWeights
<img align="right" src="https://github.com/robertjoosten/rjSkinningTools/blob/master/icons/tweakVertexWeights.png">
Remove a specific influence on vertices with the paint tool.

<p align="center"><img src="https://github.com/robertjoosten/rjSkinningTools/blob/master/tweakVertexWeights/README.png"></p>
<a href="https://vimeo.com/120942200" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjSkinningTools** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Display UI:
```python
import rjSkinningTools.tweakVertexWeights.ui
rjSkinningTools.tweakVertexWeights.ui.show()
```
 
## Note
Tweak vertex weights with sliders or spinbox input fields. This tool will give the user a good overview of what influences are translating the vertex. At the same time being able to tweak those influence to a 0.001 of precision, while setting the locked state of certain influences. It also shows if the maximum amount of influences is exceeded. The ui gets updated every time the selection is changed in Maya.
