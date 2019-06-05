import profilopy as pp
import matplotlib.pyplot as plt 
import numpy as np
from scipy.ndimage.filters import median_filter

analyzer = pp.Analyzer(json_path='data/afternoon.json')

keys = list(analyzer.data[0].keys())
keys = np.clip([float(key) for key in keys], 0, 12000)

analyzer.processor = pp.functions.processing.get_depth
values_depth = analyzer.get_depth_list(keys)

analyzer.processor = pp.functions.processing.get_std
values_sd = analyzer.get_depth_list(keys)


values_depth = median_filter(values_depth, size=5)
values_sd = median_filter(values_sd, size=5)

fig, ax1 = plt.subplots(dpi=300, figsize=(12,6))

color = 'tab:orange'
ax1.set_xlabel('Time (s)', size=18)
ax1.set_ylabel('Groove depth (mm)', color=color, size=18)
ax1.plot(keys, values_depth, color=color,linewidth=1.5, label="Groove depth measurement")
ax1.tick_params(axis='y', labelcolor=color, labelsize=16)
ax1.tick_params(axis='x', labelsize=16)
ax1.set_ylim(0, 9)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Standard Deviation (mm)', color=color, size=18)  # we already handled the x-label with ax1
ax2.plot(keys, values_sd, color=color,linewidth=1.5, label="Standard Deviation measurement")
ax2.tick_params(axis='y', labelcolor=color, labelsize=16)
ax2.grid(False) #otherwise we get one grid for each axis
ax2.set_ylim(0, 4)

plt.savefig("results/full_run.png")