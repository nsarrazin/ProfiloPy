import profilopy as pp
import matplotlib.pyplot as plt 
from scipy.interpolate import UnivariateSpline
from scipy.ndimage.filters import median_filter

import numpy as np

run6 = {"startStep" : 4400,
        "endStep" : 4800,
       "windStatus" : "UPWIND",
       "force" : 15,
       "speed" : 50,
       'notes' : "Smoke, smoke, smoke !!!"}

run_angle = {"startStep" : 9960-30,
        "endStep" : 10080+30,
       "windStatus" : "DOWNWIND",
       "force" : 40,   #in T
       "speed" : 10,    #km/h
       'notes' : "angles"}

run13 = {"startStep" : 10500-120,
        "endStep" : 10560+30,
       "windStatus" : "UPWIND",
       "force" : 40,   #in T
       "speed" : 20,    #km/h
       'notes' : "smoke (medium)"}
       
analyzer_morning = pp.Analyzer(json_path="data/morning_select.json")

analyzer = pp.Analyzer(json_path='data/run6.json') #XXX
t0, tf = run6["startStep"], run6["endStep"] #XXX

keys = list(analyzer.data[0].keys())
keys = np.array([float(key) for key in keys])

keys = keys[(keys >= t0) & (keys <= tf)]

analyzer.preprocessor = pp.functions.preprocessing.preprocessor_1

analyzer.processor = pp.functions.processing.get_depth
values_depth = analyzer.get_depth_list(keys)

x,y =[], []
for key, value in zip(keys, values_depth):
       if not np.isnan(value):
              x.append(key)
              y.append(value)

y = median_filter(y, size=3)
spl = UnivariateSpline(x, y, s=6)
# print(spl(keys))

plt.figure(figsize=(12,6))
plt.scatter(keys, values_depth,label="Groove depth", s=2.5)
plt.plot(keys, spl(keys), label="Interpolating spline")
plt.xlabel("Time (s)", size=15)
plt.ylabel("Groove depth (mm)", size=15)
# plt.ylim(0, 2.5) #XXX
plt.xlim(t0, tf)
plt.grid(True)
plt.legend()

plt.savefig('results/run6_run.png') 