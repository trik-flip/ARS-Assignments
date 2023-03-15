# Running 
```python ./week4/__main__.py```
with the ```week4``` folder and the ```ea.obj``` file in the same root folder.

It will open a frame, show a red screen, and a empty plot.
Once the empty plot is closed the red screen will run the best robot.
To train a new robot from the beginning, 
edit the following code  
```py 
from main4 import main
main(load_from_file=True)
``` 
to 
```py
from main4 import main
main(load_from_file=False)
```
