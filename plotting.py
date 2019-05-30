import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import date2num


class PlotManager:
    def __init__(self, DataManager):
        self.mngr = DataManager

    def plot_slice_raw(self, time):
        array = self.mngr.get_array_time(time)
        return plt.plot(array)
        

    def plot_slice_preprocessed(self, time):
        array = self.mngr.get_array_time(time)
        array = self.mngr.preprocessor(array)
        return plt.plot(array)
        

    def plot_run(self, times, aliasing):
        pass

    def animate_run(self):
        pass