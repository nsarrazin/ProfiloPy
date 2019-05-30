import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import date2num


class PlotManager:
    def __init__(self, DataManager):
        self.mngr = DataManager

    def plot_slice(self, time):
        array = self.mngr.get_array_time(time)
        plt.plot(array)
        pass

    def plot_run(self):
        pass

    def animate_run(self):
        pass