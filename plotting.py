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
        """Called from inside the `Analyzer` class. You probably shouldn't call it yourself.
        
        Arguments:
            DataManager {[object child of DataManager]} -- a reference to a DataManager that can be used to extract the data needed for plotting
        """
        self.mngr = DataManager

    def plot_slice_raw(self, time):
        """Just plots the basic raw data, without preprocessing. Does not show the plot, gotta call plt.show() outside of the function
        
        Arguments:
            time {[float]} -- timestamp to plot            
        """
        array = self.mngr.get_array_time(time)
        return plt.plot(array)
        
    def plot_slice_preprocessed(self, time):
        """Plots the preprocessed data. Does not show the plot, gotta call plt.show() outside of the function
        
        Arguments:
            time {[float]} -- timestamp to plot            
        """

        array = self.mngr.get_array_time(time)
        array = self.mngr.preprocessor(array)
        return plt.plot(array)

    def plot_slice_processed(self, time):
        """Plots the processed data. Does not show the plot, gotta call plt.show() outside of the function, but it does everything else.
        #NOTE: ITS HARDCODED TO DISPLAY GET_DEPTH, if the processor function is changed to something else, this won't update
        Careful with this, it should probably be reworked.

        Arguments:
            time {[float]} -- timestamp to plot            
        """
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

    def plot_3d(self, times, type="cylindrical", radius=20, resample=50):
        """Plots a 3D representation of the tire over time.
        
        Arguments:
            times {[list]} -- [List of timestamps to use in the plotting, preferably sorted]
        
        Keyword Arguments:
            type {str} -- [Whether the plot should be linear or wrapped in a cylindrical shape] (default: {"cylindrical"})
            radius {int} -- [Radius of the virtual wheel (mm)] (default: {20})
            resample {int} -- [Number of points to use for resampling each timestamp. The raw timestamp has 1k points, too much for plotting] (default: {50})
        """
        array = []
        for y, time in enumerate(times):
            raw = self.mngr.get_array_time(time)
            processed = signal.resample(self.mngr.preprocessor(raw), resample)
            for x,z in enumerate(processed[1:-2]):
                array.append((x,y,z))
        
        x = np.array([i[0] for i in array])
        y = np.array([i[1] for i in array])
        z = np.array([i[2] for i in array])
        
        #TODO: Update linear to use plotly ,it's kinda garbage rn
        if type=="linear":    
            fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
            surf = ax.plot_trisurf(x,y,z,cmap=cm.terrain,
                        linewidth=0, antialiased=True, shade=False)
        
        if type=="cylindrical":
            x_array = 2.5*radius*(x - np.min(x))/np.ptp(x).astype(int)
            theta = y*(2*np.pi)/(np.max(y)-np.min(y))
            
            r = z+radius
            y_array = r*np.cos(theta)
            z_array= r*np.sin(theta)

            dic_x = {}
            dic_theta = {}


            # we start by going in circles over the virtual tire
            for x,y,z in zip(x_array,y_array,z_array): #we regroup the points by x-values
                if x in dic_x.keys():
                    dic_x[x].append((x,y,z))
                    continue
                dic_x[x] = ["x={}".format(round(x,2)), (x,y,z)] 
            
            value_superlist_x = dic_x.values()

            #now we go by timestamp (or theta)
            n=0
            for theta, x,y,z in zip(theta, x_array,y_array,z_array): #we regroup the points by theta-values
                if theta in dic_theta.keys():
                    dic_theta[theta].append((x,y,z))
                    continue
                dic_theta[theta] = ["t={}".format(round(times[n],2)), (x,y,z)]
                n+=1
            
            value_superlist_theta = dic_theta.values()



            list_traces = []
            for vals in list(value_superlist_theta)+list(value_superlist_x):
                x = np.array([val[0] for val in vals[1:]])
                y = np.array([val[1] for val in vals[1:]])
                z = np.array([val[2] for val in vals[1:]])
                trace = go.Scatter3d(x=x, 
                                    y=y, 
                                    z=z, 
                                    mode="lines",
                                    name=vals[0],
                                    line=dict(
                                        color=np.sqrt(y**2+z**2), #TODO: Improve the scale here
                                        colorscale="Jet",
                                        cmin = np.min(r),
                                        cmax = np.max(r),
                                        width=10,
                                    ))
                list_traces.append(trace)

            min_ax = min([np.min(x_array), np.min(y_array), np.min(z_array)])
            max_ax = max([np.max(x_array), np.max(y_array), np.max(z_array)])

            layout = go.Layout(
                title="3D Plot",
                # scene=dict(
                # xaxis=dict(
                #     range=[min_ax, max_ax]
                # ),
                # yaxis=dict(
                #     range=[min_ax, max_ax]
                # ),
                # zaxis=dict(
                #     range=[min_ax, max_ax]
                # ))
            )

            list_traces.append(trace)
            plotly.offline.plot({
                                "data": list_traces,
                                "layout": layout,
                                }, auto_open=True)
                                    


            