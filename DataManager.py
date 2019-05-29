import numpy as np
import numba as nb
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
            data = np.interp(np.linspace(0,1,1280), np.linspace(0,1,len(data)), data).tolist()
            experiment[key] = data
    
    if file_out == "":
        file_out = filepath.replace('.txt', '.json')
    
    with open(file_out, 'w') as outfile:
        json.dump(listExperiments, outfile)
                

if __name__ == '__main__':
    print("Afternoon file")
    file_to_json("Wheel8 Aternoon.txt", -3619682275.496)
    print("Morning file")
    file_to_json("Wheel8 Morning.txt", -3619671997.651)