import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import date2num

from matplotlib import cm
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d import Axes3D  

import numpy as np
from scipy.ndimage.filters import median_filter
from scipy.interpolate import UnivariateSpline, CubicSpline

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

    def plot_slice_processed(self, time):
        z = self.mngr.get_array_time(time)
        z = self.mngr.preprocessor(z)

        x = np.linspace(0,1,z.shape[0])
        
        spl = UnivariateSpline(x,z)
        spl.set_smoothing_factor(10)

        z_spl = spl(x)
        z_smooth = UnivariateSpline(x, z_spl)
        z_smooth.set_smoothing_factor(1e5)
        
        
        #getting the first order derivative
        dz = np.gradient(z_spl) 
        dz_spl = UnivariateSpline(x, dz)
        dz_spl.set_smoothing_factor(1e-3)
        
        
        #getting the second order derivative
        h       = 0.0001
        d2z     = (dz[1:]-dz[:-1])/h
        d2z_spl = UnivariateSpline(x[1:], d2z)
        d2z_spl.set_smoothing_factor(1e-3)
        
        #getting the difference between the aaverage line and the "real" profile
        delta_z = z_spl - z_smooth(x)
        delta_z_spl = UnivariateSpline(x, delta_z)
        delta_z_spl.set_smoothing_factor(1e-3)
        
        #first derivative of the difference of the two lines
        dz = np.gradient(delta_z)     
        dz_spl = UnivariateSpline(x, dz)
        dz_spl.set_smoothing_factor(1e-3)
        
        roots = dz_spl.roots()   #roots of the difference 
        
        mins = [i for _,i in sorted(zip(delta_z_spl(roots),roots))][:2]   
        
        eps_down=10 #lower bound for second dderivative
        n=len(mins)
        #print("Second derivative value at its roots",d2z_spl(roots))
        grooves=[]
        for i in range(n):
            if  d2z_spl(mins[i]) > eps_down and  (z_smooth(mins[i]) -spl(mins[i]))  >= 1:
                grooves.append(mins[i])    #or roots, I dont know
        grooves=np.array(grooves)

        #print("All roots",roots)
        
        range_values = spl(1)-spl(0)
        
        dz_mins = delta_z_spl(grooves)
        if dz_mins.size ==0:
            dz_mins=np.array([0])
        
        plt.clf()
        plt.plot(x, z_smooth(x), linewidth=1.5, label="Smoothed spline")
        plt.scatter(x, z,s=0.75,c="C4", label="Raw data")
        plt.plot(x, z_spl, linewidth=1.5, label="Fitting spline")
        for i in mins:
            plt.axvline(i, c="C2", linestyle="dashed", linewidth=1.5,label="Detected groove")
        plt.xlim(0,1)
        plt.xlabel("Width [-]")
        plt.ylabel("Depth [mm]")
        # plt.ylim((0, 35))
        plt.legend()
        
    def plot_run(self, times):
        pass

    def animate_run(self):
        pass

    def plot_3d(self, times, type="linear"):
        array = []

        for y, time in enumerate(times):
            for x,z in enumerate(self.mngr.preprocessor(self.mngr.get_array_time(time))):
                array.append((x,y,z))
        x,y = np.array([i[0] for i in array]), np.array([i[1] for i in array])
        z = np.array([i[2] for i in array])

        if type=="linear":    
            fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
            surf = ax.plot_trisurf(x,y,z,cmap=cm.terrain,
                        linewidth=0, antialiased=True, shade=False)
        if type=="cylindrical":
            pass
