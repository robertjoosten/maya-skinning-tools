# smoothWeightsCtx
Paint smooth weights tool in Maya using the weights of neighbouring vertices.
<a href="https://vimeo.com/126825847" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjSkinningTools** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Select a skinned object and run the following code:
```python
from rjSkinningTools import smoothWeightsCtx;
smoothWeightsCtx.paint()
```

## Note
The paint tool calls a script that find the surrounding vertices and its skin weights. These skin weights are then blended with the skin weights of the original vertex based value of the paint tool.
* Undo-able / Redo-able

Based on the settings on the skinCluster the following attribute will be respected while smoothing the weights:
* Max Influences
* Normalize Weights
* Locked Influences

I would like to note that the idea for this script came from [Tom Ferstl](https://vimeo.com/tomferstl), he developed a script where the end results is very simular. I did use the original script as an inspiration, but what happens under the hood is completely different.
