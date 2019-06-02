from DataManager import DataManager
from functions.processing import get_depth, get_std
from functions.preprocessing import preprocessor_1
from plotting import PlotManager

import numpy as np
import matplotlib.pyplot as plt

class Analyzer(DataManager):
    def __init__(self, *, json_path, preprocessor=lambda array:array, processor=lambda array:1, plotter=PlotManager, count=0):
        """A children class of the DataManager, containing the necessary functions for groove depth analysis.

        
        Arguments:
            json_path {[str]} -- [Path to the json file to be loaded in the analyzer]
            preprocessor {[func]} -- [A function that takes a numpy array as an input and returns a numpy array. It should preprocess the raw data (removing noise, smoke, etc.)]
            processor {[func]} -- [A function that takes a numpy array as an input and returns a single float. This numerical output will be use for analyzing runs.]
            plotter{[Class : PlotManager]} -- [A link to the PlotManager class to be used for  plotting runs]

        Keyword Arguments:
            count {int} -- [An ID to identify that dataset idk why I added that tbh] (default: {0})
        """
        DataManager.__init__(self, json_path)
        self.preprocessor = preprocessor
        self.processor = processor
        self.plotter = plotter(self) #we pass the analyzer as an attribute to the plotmanager so it can extract values from it
        self.id = count

    def preprocess_slice(self, time):
        array = self.get_array_time(time)

        array_processed = self.preprocessor(array)

        return array_processed

    def get_depth(self, time, plotting=False):
        """This function returns the groove depth at a specific timestep.
        
        Arguments:
            time {[type]} -- [The timestamp at which we want the groove depth]
        
        Keyword Arguments:
            plotting {bool} -- [Determines if this slice should be passed to the plot manager] (default: {False})
        
        Returns:
            [float] -- [The result of the processor function, usually the groove depth]
        """
        array_processed = self.preprocess_slice(time)

        depth = self.processor(array_processed)

        if plotting:
            self.plotter.plot_slice(time)

        return depth

    def get_depth_list(self, times, plotting=False):
        """This function returns a list of groove depth.
        
        Arguments:
            times {[array of size n]} -- [An array containing the timestamps to be interpolated]
        
        Keyword Arguments:
            plotting {bool} -- [Determines if this slice should be passed to the plot manager] (default: {False})
        
        Returns:
            [list] -- [The list containing all the groove depth measured]
        """
        depth_list = []

        for time in times:
            depth = self.get_depth(time)
            depth_list.append(depth)
        
        if plotting:
            self.plotter.plot_run(times)
        
        return depth_list


if __name__ == "__main__":
    analyzer = Analyzer(json_path='afternoon.json', preprocessor=preprocessor_1, processor=get_depth, plotter=PlotManager)
    
    t0, tf = 0, 10000   
    # plt.figure(dpi=300)
    depths = analyzer.get_depth_list(np.arange(t0, tf, 10))
    # for threshold in [0.1, 0.25, 0.5, 1, 2.5, 8]:
    #     print("Threshold {}".format(threshold))
    #     analyzer.preprocessor = lambda array : preprocessor_1(array, threshold=threshold) 
    #     depths = analyzer.get_depth_list((t0,tf), aliasing=100)
    plt.scatter(range(len(depths), depths))
    
    plt.xlabel("Time")
    plt.ylabel("Groove depth [mm]")
    plt.ylim([-10, 0])
    # plt.legend()
    plt.show()