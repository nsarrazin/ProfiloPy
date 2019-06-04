import numpy as np
from random import shuffle
import json

def file_to_json(filepath, t0, cutoff_experiment=10, cutoff_datapoint=25, resample=1000, maxdt=10, file_out = "", debug=False):
    """This function converts a raw .txt obtained from the profilometer into an organized JSON that can be parsed easily. 
        It splits the data into "experiments" if the difference between two timestamps is too large.

    Arguments:
        filepath {[str]} -- Filepath to the raw data
        t0 {[float]} -- Timestamp value to zero out the timestamps
                        ( Use -3619682275.496 for the afternoon)
                        ( Use -3619671997.651 for the morning)
    
    Keyword Arguments:
        cutoff_experiment {int} -- If an experiment has less than `cutoff_experiment` timestamps, it is removed. (default: {10})
        cutoff_datapoint {int} -- If a timestamp containes less than `cutoff_datapoint` datapoints, it is removed. (default: {25})
        resample {int} -- Since the data contains a varying number of datapoints per timestamp, it is resampled to `resample` datapoints. (default: {1000})
        maxdt {int} -- if the difference between two timestamps is bigger than `maxdt`, a new experiment is created (default: {10})
        file_out {str} -- path of the output json, if it is not specified, the name of the txt is used.
        debug {bool} -- If debug is true, print statements are issued throughout the process for easier tracking
    """
    rawData = {}
    if debug:
        print("Reading the file...")
    
    with open(filepath) as f:
        lines = f.readlines()
    
    for line in lines:
        lst = line.strip().split("\t")
        rawData[str(lst[0])] = [float(i) for i in lst[1:]]
            
    listExperiments = []

    currentDict = {}
    rawKeys = list(rawData.keys())

    if debug:
        print("Splitting the data")
    
    for n, key in enumerate(rawKeys):
        key2 = str(float(key)+t0)
        if n == 0:
            currentDict[key2] = rawData[key]
            continue
        
        if float(key) - float(rawKeys[n-1]) > maxdt:
            listExperiments.append(currentDict)
            currentDict = {}
            currentDict[key2] = rawData[key]    
            continue
        
        currentDict[key2] = rawData[key]
        
    listExperiments.append(currentDict)

    if debug:
        print("Removing experiments that are too short")

    listExperiments = [ i for i in listExperiments if len(list(i.keys())) > cutoff_experiment]
    
    for experiment in listExperiments:
        if debug:
            print("Removing empty lines from experiments...")
        for key in list(experiment.keys()).copy():
            if len(experiment[key]) <= cutoff_datapoint:
                experiment.pop(key)
        
        if debug:
            print('Resampling the data...')
        for key in experiment.keys():
            data = experiment[key]
            data = np.interp(np.linspace(0.5,1,resample), np.linspace(0,1,len(data)), data).tolist()
            data.pop(0)
            experiment[key] = data
    
    if file_out == "":
        file_out = filepath.replace('.txt', '.json')
    
    with open(file_out, 'w') as outfile:
        json.dump(listExperiments, outfile)

def downsampler_mean(json_path, n=5, experiment=0, file_out = ""):
    """Takes the average of n timestamps and downsamples the data for faster processing.
    
    Arguments:
        json_path {[str]} -- [Path to the input json, should have been processed through `file_to_json` before to ensure data consistency]
    
    Keyword Arguments:
        n {int} -- [Downsampler window, defaults to 5 which means one sample per second (raw resolution of 5Hz)] (default: {5})
    """
    with open(json_path, "rb") as json_file:
        data = json.load(json_file)[experiment]
    
    keys = list(data.keys())
    n_points = len(data[keys[0]]) # we assume a constant amount of points per timestamp
    downsampled_array = []

    for point in range(n_points):
        arr = np.array([data[timestamp][point] for timestamp in keys]) # we extract one of these points along the time dimension
        end =  n * int(len(arr)/n)
        downsampled_column = np.mean(arr[:end].reshape(-1, n), 1)
        downsampled_array.append(downsampled_column)
    
    downsampled_array = np.array(downsampled_array).T.tolist()

    keys = np.array([float(key) for key in keys])
    end =  n * int(len(keys)/n)
    downsampled_keys = np.mean(keys[:end].reshape(-1, n), 1)

    json_dict = {}
    for n, key in enumerate(downsampled_keys):
        json_dict[key] = downsampled_array[n]
    
    if file_out == "":
        file_out = json_path.replace('.json', "_mean_downsampled.json")
    
    with open(file_out, 'w') as outfile:
        json.dump([json_dict], outfile)

def downsampler_random(json_path, n=500, experiment=0, file_out=""):
    with open(json_path, "rb") as json_file:
        data = json.load(json_file)[experiment]
    
    keys = list(data.keys())
    keys = [float(key) for key in keys]
    shuffle(keys)

    timestamps = keys[:n]
    timestamps.sort()
    # print(timestamps)
    json_dict = {}
    for n, key in enumerate(timestamps):
        json_dict[key] = data[str(key)]
    
    if file_out == "":
        file_out = json_path.replace('.json', "_random_downsampled.json")
    
    with open(file_out, 'w') as outfile:
        json.dump([json_dict], outfile)
if __name__ == '__main__':
    # print("Afternoon file")
    # file_to_json("Wheel8 Aternoon.txt", -3619682275.496)
    # print("Morning file")
    # file_to_json("Wheel8 Morning.txt", -3619671997.651)
    downsampler_random("afternoon.json", n=500)
    # downsampler_mean("afternoon.json", n=50)