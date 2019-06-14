from profilopy.tools.jsonify import file_to_json, downsampler_mean, downsampler_random, downsampler_select
import numpy as np

print("Afternoon file")
file_to_json("data/Wheel8 Aternoon.txt", -3619682275.496, file_out="afternoon.json")
print("Morning file")
file_to_json("data/Wheel8 Morning.txt", -3619671997.651, file_out="morning.json")

print("Generate downsampled files")
downsampler_random("data/afternoon.json", n=500)
downsampler_mean("data/afternoon.json", n=50)
downsampler_select("data/morning.json", [0.4])

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

downsampler_select("data/afternoon.json", np.arange(run6["startStep"], run6["endStep"], 0.2), file_out="data/run6.json")
downsampler_select("data/afternoon.json", np.arange(run_angle["startStep"],run_angle["endStep"], 0.2), file_out="data/angles.json")
downsampler_select("data/afternoon.json", np.arange(run13["startStep"],run13["endStep"], 0.2), file_out="data/run13.json")