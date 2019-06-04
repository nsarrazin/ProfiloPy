import numpy as np
import numba as nb
import json

@nb.jit(nopython=True, cache=True)
def find_nearest(array, value):
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

class DataManager:
    def __init__(self, json_path):
        """This class reads a json file generated from `file_to_json` and loads into memory so that it can be called later.
        
        Arguments:
            json_path {[str]} -- [Path to the json file to be loaded in the data manager]
        """
        self.dt = 0.2
        with open(json_path, "rb") as json_file:
            self.data = json.load(json_file)

    def get_array_time(self, time, experiment=0):
        """This functions parses through the raw data and returns the data whose timestamp is the closest to the specified time
        
        Arguments:
            time {[float]} -- [The time whose nearest slice you want to extract]
        
        Keyword Arguments:
            experiment {int} -- [The experiment index, in case the json file contains multiple experiments] (default: {0})
        
        Returns:
            [list] -- [The full slice of the nearest recorded timestamp]
        """
        time = float(time)
        timestamps = [float(i) for i  in self.data[experiment].keys()]

        key = str(find_nearest(timestamps, time))

        return np.array(self.data[experiment][key])

    def get_array_index(self, index, experiment=0):
        """This functions returns the raw data for a specific index.
        
        Arguments:
            index {[int]} -- [The index for which you want the data]
        
        Keyword Arguments:
            experiment {int} -- [The experiment index, in case the json file contains multiple experiments] (default: {0})
        
        Returns:
            [list] -- [The full slice at the specified index]
        """
        key = [self.data[experiment].keys()][index] #FIXME: Fix that line
        return np.array(self.data[experiment][key])

