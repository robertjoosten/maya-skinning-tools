# softSelectionToWeights
<img align="right" src="https://github.com/robertjoosten/rjSkinningTools/blob/master/icons/softSelectionToWeights.png">
Convert soft selection to skin weights.

<p align="center"><img src="https://github.com/robertjoosten/rjSkinningTools/blob/master/softSelectionToWeights/README.png"></p>
<a href="https://vimeo.com/121190357" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjSkinningTools** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Display UI:
```python
import rjSkinningTools.softSelectionToWeights.ui
rjSkinningTools.softSelectionToWeights.ui.show()
```
 
## Note
Convert soft selection into skin weights. More influences can be added by clicking the plus button. When more influences are added these weights are automatically blended. The influence and soft selection can be reselected by right clicking the influence widget and using the context menu. 
    
Skin cluster settings like max influences and normalization will be taken into account when applying the skin weights.