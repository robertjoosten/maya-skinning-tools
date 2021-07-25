# delinear-weights
<img align="right" src="../../../../icons/ST_delinearWeights.png?raw=true">
De-linearize skin weights.
<p align="center"><img src="../../../../docs/_images/delinear-weights-example.gif?raw=true"></p>

## Installation
* Extract the content of the .rar file anywhere on disk.
* Drag the skinning-tools.mel file in Maya to permanently install the script.
 
## Note
Delinear weights applies an easing algorithm to the skin weights. This tool is best used if skin weights have been copied from a low polygon source, when this is done sometimes it is very obvious that the weights are linearly divided between the vertices of the low polygon source. This tool will tween those weights.