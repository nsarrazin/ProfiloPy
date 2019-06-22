# ProfiloPy
Code repo for AE2223-I group CD13, contains all the processing code to analyze raw profilometer data and reproduce the graphs found in the paper.

## INSTALLATION
Start by cloning the repository in a folder.
```
$ git clone https://github.com/nsarrazin/profilometer-analysis.git
```
Open a terminal and navigate in the profilometer-analysis folder and install the package in developer mode.
```
$ pip install -e .
```

## PREPARATION
The profilometer outputs raw text files. However ProfiloPy reads json files in. In order to convert the raw files, a helper function was created. Take a look in `scripts/create_json.py` for an example. This helper function as well as other json downsampling functions are available in `tools.jsonify.py`

All downsamplers read json files as an input, so calling `file_to_json` before is mandatory. They also output a output file. Read the docstrings for more information about parameters.

The following downsamplers are available :
- `downsampler_mean`   : Takes the average of `n` samples at a time, reducing the size of the file by a factor `n`.
- `downsampler_random` : Takes `n` random samples across the input file.
- `downsampler_select` : This downsampler requires a list `times` of timestamps as an input, it then extracts said timestamps from the input file.

A simple example would be the following  (make sure the raw files are located in `scripts/data/` before calling this script.):
```python
from profilopy.tools.jsonify import file_to_json, downsampler_random
import profilopy as pp

file_to_json("data/Wheel8 Aternoon.txt", -3619682275.496, file_out="afternoon.json")

downsampler_random("data/afternoon.json", n=500)
```
## ANALYSIS
The main way to use ProfiloPy is through the use of the `Analyzer` class. This class allows you to use and update processing and preprocessing functions to analyze the data. This allows for modularity and easy method comparison. The class has the following attributes.

- `preprocessing` : A preprocessing function, it takes an array as an input and returns an array as an output.
- `processing` : The processing function, it takes an array as an input and returns a single numerical value as an output.
- `plotter` : A plotter class, with access to the `Analyzer`, so it can pull the data it needs for analysis. You probably shouldn't touch this, or just add methods to the default `PlotManager` one, available in `plotting.py`

A simple example would be :
```python
analyzer = pp.Analyzer(json_path='data/afternoon_random_downsampled.json') # read the json file we created previously

analyzer.preprocessor = pp.functions.preprocessing.preprocessor_1
analyzer.processor = pp.functions.processing.get_depth

init_depth = analyzer.get_depth(0)
end_depth = analyzer.get_depth(10000)
print('Initial groove depth : {}mm\nFinal groove depth : {}mm'.format(round(init_depth,2), \
                                                                    round(end_depth,2)))
```
Which would output the following :
```
Initial groove depth : 7.97mm
Final groove depth : 2.25mm
```

### Using lambdas
Because the (pre)processing functions can be updated on the fly, the code is very modular. Using lambdas to define these functions let you tweak their parameters on the fly. A simple example could be changing the threshold of the default preprocessing function.

```python
import numpy as np
import matplotlib.pyplot as plt 

t0,tf = 0, 10000
timestamps = list(analyzer.data[0].keys()) # get the timestamps of the first experiment

for val in [0.1, 0.25, 0.5, 1, 2.5, 8]:
    # Using a lambda to change some kwargs of the preprocessor function
    analyzer.preprocessor = lambda array : preprocessor_1(array, threshold=val) 

    depths = analyzer.get_depth_list(timestamps)
    plt.plot(depths)

plt.show()
```

## PLOTTING

The `Analyzer` class comes with a plotting manager, which can be accessed through the `plotter` argument. It can perform multiple operations such as :
- `plot_slice_raw` : to plot a slice raw from the json
- `plot_slice_preprocessed` : to plot a slice that went through the preprocessor
- `plot_slice_processed` : to plot a processed slice with all the elements used to compute groove depth. Currently hardcoded, this will need be changed in the future.
- `plot_3d` : Plot a list of slices in a "virtual tire", to get a feel for the state of the tire.
  
Need to be ported from the notebook :
- `plot_run` : TODO plot the computed groove depth over time
- `animate_run` : TODO plots slice back to back to create a video.

A couple of examples :
```python 
import profilopy as pp
import matplotlib.pyplot as plt
import numpy as np
analyzer_morning = pp.Analyzer(json_path="data/morning_select.json")

analyzer = pp.Analyzer(json_path='data/afternoon.json')

analyzer.preprocessor = lambda array: pp.functions.preprocessing.preprocessor_1(array, threshold=1, zeroing=439.5)

plt.figure(figsize=(12,6))
analyzer.plotter.plot_slice_processed(4500) # run6_slice
analyzer_morning.plotter.plot_slice_raw(0.4)

plt.legend()
plt.gca().tick_params(axis="both",labelsize=16)
plt.grid()
plt.savefig("results/plot6_slice.png")
```

This would produce the following figure :
![figure1](https://i.imgur.com/iwF636L.png)


Here is another example with 3D plotting:
```python
analyzer = pp.Analyzer(json_path='data/afternoon_random_downsampled.json')

keys = list(analyzer.data[0].keys())

#get a subset of the keys for plotting
keys = np.clip([float(key) for key in keys], 0, 12000)[125:150] 

#make sure the slices are calibrated to start at zero
analyzer.preprocessor = pp.functions.preprocessing.zeroing

analyzer.plotter.plot_3d(keys, type='cylindrical', radius=25, resample=100)
```

Which would produce an html file that contains [the following figure](http://nsarrazin.com/tire_demo):

![figure2](https://i.imgur.com/TVEbVHJ.png)

## TODO
- Port the 3D linear plotting to plotly
- Add more preprocessing options
- Add more processing options
- Add full run plotting
- Add animations back