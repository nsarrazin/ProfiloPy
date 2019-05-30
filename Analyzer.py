from DataManager import DataManager
import numpy as np
from processing import get_delta_z
from preprocessing import pre_processing
from plotting import PlotManager
import matplotlib.pyplot as plt

class Analyzer(DataManager):
    def __init__(self, json_path, preprocessor, processor, plotter, count=0):
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


    def get_depth(self, time, preprocessed=True, plotting=False):
        """This function returns the groove depth at a specific timestep.
        
        Arguments:
            time {[type]} -- [The timestamp at which we want the groove depth]
        
        Keyword Arguments:
            preprocessed {bool} -- [Determines if the raw data be passed through the preprocessor ] (default: {True})
            plotting {bool} -- [Determines if this slice should be passed to the plot manager] (default: {False})
        
        Returns:
            [float] -- [The result of the processor function, usually the groove depth]
        """
        array = self.get_array_time(time)

        if preprocessed:
            array = self.preprocessor(array)

        depth = self.processor(array)

        if plotting:
            self.plotter.plot_slice(time)

        return depth

    def get_depth_list(self, times, preprocessed=True, plotting=False, aliasing=1):
        """This function returns a list of groove depth.
        
        Arguments:
            times {[tuple of size 2]} -- [A tuple containing the beginning timestamp and the end timestamp]
        
        Keyword Arguments:
            preprocessed {bool} -- [Determines if the raw data be passed through the preprocessor ] (default: {True})
            plotting {bool} -- [Determines if this slice should be passed to the plot manager] (default: {False})
            aliasing {int} -- [The aliasing factor. If it's 2, every other timestamp is sampled, if it's set to 4 it's 1 in 4 etc.] (default: {1})
        
        Returns:
            [list] -- [The list containing all the groove depth measured]
        """
        depth_list = []

        for time in np.arange(times[0], times[1], self.dt*aliasing):
            depth = self.get_depth(time, preprocessed=preprocessed)
            depth_list.append(depth)
        
        if plotting:
            self.plotter.plot_run(times, aliasing)
        
        return depth_list


if __name__ == "__main__":
    analyzer = Analyzer('afternoon.json', pre_processing, get_delta_z, PlotManager)
    t0 = 0
    tf = 12000
    times = (t0, tf)
    # depth1 = analyzer.get_depth_list(times, preprocessed=True, aliasing=50)
    # print(depth1, depth2)
    # plt.scatter(np.arange(t0, tf, 50*0.2), depth1)
    # plt.plot(np.arange(t0, tf, 20), depth2)
    
    z = analyzer.plotter.plot_slice_raw(6000)
    plt.show()
    z = analyzer.plotter.plot_slice_preprocessed(6000)
    plt.show()

    # plt.plot(z)
    # plt.show()
    # for i in np.arange(times[0], times[1], 0.2*100):
        # print(analyzer.get_depth(i))