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
I would like to note that the idea for this script came from [Tom Ferstl](https://vimeo.com/tomferstl), he developed a script where the end results is very simular. I did use the original script as an inspiration, but what happens under the hood is completely different.

artUserPaintCtx only takes in mel commands, but instead of writting a wrapper in mel that calls python code, I registered a new command which is written in python, improving the speed. This also gives you the option to add Undo and Redo functionality.

The paint tool calls a script that find the surrounding vertices and its skin weights. These skin weights are then blended with the skin weights of the original vertex based value of the paint tool.

It also takes into account the settings on your skinCluster. For real-time purposes its very common to have your maintain max influences set to a certain number. The same goes for normalization of the weights and the locked state of influences.
