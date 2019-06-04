import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import date2num

from matplotlib import cm
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d import Axes3D  

import numpy as np

from scipy.ndimage.filters import median_filter
from scipy.interpolate import UnivariateSpline, CubicSpline
from scipy import signal

import plotly
import plotly.graph_objs as go
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
        plt.legend()
        
    def plot_run(self, times):
        pass

    def animate_run(self):
        pass

    def plot_3d(self, times, type="linear", radius=10, resample=50, alpha=-1):
        array = []

        for y, time in enumerate(times):
            raw = self.mngr.get_array_time(time)
            processed = signal.resample(self.mngr.preprocessor(raw), resample)
            for x,z in enumerate(processed[1:-2]):
                array.append((x,y,z))
        
        x = np.array([i[0] for i in array])
        y = np.array([i[1] for i in array])
        z = np.array([i[2] for i in array])
        
        if type=="linear":    
            fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
            surf = ax.plot_trisurf(x,y,z,cmap=cm.terrain,
                        linewidth=0, antialiased=True, shade=False)
        
        if type=="cylindrical":
            x_array = 2*radius*(x - np.min(x))/np.ptp(x).astype(int)
            theta = y*(2*np.pi)/(np.max(y)-np.min(y))
            
            r = z+radius
            y_array = r*np.cos(theta)
            z_array= r*np.sin(theta)

            dic_x = {}
            dic_theta = {}

            for x,y,z in zip(x_array,y_array,z_array): #we regroup the points by x-values
                if x in dic_x.keys():
                    dic_x[x].append((x,y,z))
                    continue
                dic_x[x] = [(x,y,z)] 
            
            value_superlist_x = dic_x.values()

            for theta, x,y,z in zip(theta, x_array,y_array,z_array): #we regroup the points by theta-values
                if theta in dic_theta.keys():
                    dic_theta[theta].append((x,y,z))
                    continue
                dic_theta[theta] = [(x,y,z)]
            
            value_superlist_theta = dic_theta.values()



            list_traces = []
            line_marker = dict(color='#0066FF', width=2)

            for vals in value_superlist_x:
                trace = go.Scatter3d(x=[val[0] for val in vals], 
                                    y=[val[1] for val in vals], 
                                    z=[val[2] for val in vals], 
                                    mode="lines",
                                    line=line_marker)
                list_traces.append(trace)

            for vals in value_superlist_theta:
                trace = go.Scatter3d(x=[val[0] for val in vals], 
                                    y=[val[1] for val in vals], 
                                    z=[val[2] for val in vals], 
                                    mode="lines",
                                    line=line_marker)
                list_traces.append(trace)
            
            list_traces.append(trace)
            plotly.offline.plot({
                                "data": list_traces,
                                "layout": go.Layout(title="3D Plot")
                                }, auto_open=True)
                                    


            