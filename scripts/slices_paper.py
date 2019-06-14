import profilopy as pp
import matplotlib.pyplot as plt
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

analyzer = pp.Analyzer(json_path='data/angles.json') #XXX
analyzer.preprocessor = lambda array: pp.functions.preprocessing.preprocessor_1(array, threshold=1, zeroing=439.5)
t0, tf = run13["startStep"], run13["endStep"] #XXX

plt.figure(figsize=(12,6))
# analyzer.plotter.plot_slice_processed(4500) # run6_slice
analyzer.plotter.plot_slice_processed(9980)
# analyzer.plotter.plot_slice_processed(10560+15) #run13_slice
# analyzer.plotter.plot_slice_processed(4642)
# for i in np.linspace(0, 100, 25):
    # analyzer.plotter.plot_slice_preprocessed(t0)
analyzer_morning.plotter.plot_slice_raw(0.4)
plt.legend()
plt.gca().tick_params(axis="both",labelsize=16)
plt.grid()
plt.savefig("results/angle1_slice.png")