import numpy as np
import numba as nb
import json

@nb.jit(nopython=True, cache=True)
def find_nearest(array, value):
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

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
                
class DataManager:
    def __init__(self, json_path):
        """This class reads a json file generated from `file_to_json` and loads into memory so that it can be called later.
        
        Arguments:
            json_path {[str]} -- [Path to the json file to be loaded in the data manager]
        """
        with open(json_path, "rb") as json_file:
            self.data = json.load(json_file)

    def get_step(self, time, experiment=0):
        """This functions parses through the raw data and returns the data whose timestamp is the closest to the specified time
        
        Arguments:
            time {[float]} -- [The time whose nearest slice you want to extract]
        
        Keyword Arguments:
            experiment {int} -- [The experiment index, in case the json file contains multiple experiments] (default: {0})
        
        Returns:
            [list] -- [The full slice of the nearest recorded timestamp]
        """
        timestamps = [float(i) for i  in self.data[experiment].keys()]

        key = str(find_nearest(timestamps, time))

        return self.data[experiment][key]

    def get_index(self, index, experiment=0):
        """[summary]
        
        Arguments:
            index {[int]} -- [The index for which you want the data]
        
        Keyword Arguments:
            experiment {int} -- [The experiment index, in case the json file contains multiple experiments] (default: {0})
        
        Returns:
            [list] -- [The full slice at the specified index]
        """
        key = [self.data[experiment].keys()][n]
        return self.data[experiment][key]

if __name__ == '__main__':
    print("Afternoon file")
    file_to_json("Wheel8 Aternoon.txt", -3619682275.496)
    print("Morning file")
    file_to_json("Wheel8 Morning.txt", -3619671997.651)