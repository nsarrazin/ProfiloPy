from .DataManager import DataManager
from .functions.processing import get_depth, get_std
from .functions.preprocessing import preprocessor_1, zeroing
from .plotting import PlotManager

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
        """[summary]
        
        Arguments:
            time {[type]} -- [description]
        """
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
    analyzer_morning = Analyzer(json_path="morning_select.json")

    analyzer = Analyzer(json_path='afternoon_random_downsampled.json', preprocessor=lambda array:preprocessor_1(array, threshold=np.inf), processor=get_depth, plotter=PlotManager)
    
    keys = list(analyzer.data[0].keys())
    # keys = np.clip([float(key) for key in keys], 0, 12000)

    keys = np.clip([float(key) for key in keys], 0, 12000)[125:150]
    analyzer.preprocessor = zeroing
    analyzer.plotter.plot_3d(keys, type='cylindrical', radius=25, resample=100)
    plt.show()

    # analyzer.processor = get_depth
    # values_depth = analyzer.get_depth_list(keys)
    # analyzer.processor = get_std
    # values_sd = analyzer.get_depth_list(keys)


    # values_depth = median_filter(values_depth, size=5)
    # values_sd = median_filter(values_sd, size=5)

    # fig, ax1 = plt.subplots(dpi=300, figsize=(12,6))

    # color = 'tab:orange'
    # ax1.set_xlabel('Time (s)', size=18)
    # ax1.set_ylabel('Groove depth (mm)', color=color, size=18)
    # ax1.plot(keys, values_depth, color=color,linewidth=1.5, label="Groove depth measurement")
    # ax1.tick_params(axis='y', labelcolor=color, labelsize=16)
    # ax1.tick_params(axis='x', labelsize=16)
    # ax1.set_ylim(0, 9)
    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    # color = 'tab:blue'
    # ax2.set_ylabel('Standard Deviation (mm)', color=color, size=18)  # we already handled the x-label with ax1
    # ax2.plot(keys, values_sd, color=color,linewidth=1.5, label="Standard Deviation measurement")
    # ax2.tick_params(axis='y', labelcolor=color, labelsize=16)
    # ax2.grid(False) #otherwise we get one grid for each axis
    # ax2.set_ylim(0, 4)

    # plt.savefig("full_run.png")