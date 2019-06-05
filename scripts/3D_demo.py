import profilopy as pp
import numpy as np

print(pp.__spec__)
analyzer_morning = pp.Analyzer(json_path="data/morning_select.json")

analyzer = pp.Analyzer(json_path='data/afternoon_random_downsampled.json')

keys = list(analyzer.data[0].keys())
# keys = np.clip([float(key) for key in keys], 0, 12000)

keys = np.clip([float(key) for key in keys], 0, 12000)[125:150]
analyzer.preprocessor = pp.functions.preprocessing.zeroing

analyzer.plotter.plot_3d(keys, type='cylindrical', radius=25, resample=100)