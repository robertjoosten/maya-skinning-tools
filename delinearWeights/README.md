# delinearWeights
<img align="right" src="https://github.com/robertjoosten/rjSkinningTools/blob/master/icons/delinearWeights.png">
De-linearize skin weights.
<p align="center"><img src="https://github.com/robertjoosten/rjSkinningTools/blob/master/delinearWeights/README.gif"></p>

## Installation
Copy the **rjSkinningTools** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Display UI:
```python
import rjSkinningTools.delinearWeights.ui
rjSkinningTools.delinearWeights.ui.show()
```
 
## Note
Delinear weights applies an easing algorithm to the skin weights. This tool is best used if skin weights have been copied from a low polygon source, when this is done sometimes it is very obvious that the weights are linearly divided between the vertices of the low polygon source. This tool will tween those weights.