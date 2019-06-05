import numpy as np
from scipy.ndimage.filters import median_filter
from scipy.interpolate import UnivariateSpline, CubicSpline

def get_depth(array):
    x = np.linspace(0,1,array.shape[0])
    z = array  #data points

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
    
    #roots = dz_spl.roots()
    
    eps_down=10 #lower bound for second dderivative
    n=len(mins)
    #print("Second derivative value at its roots",d2z_spl(roots))
    grooves=[]

    for i in range(n):
        if  d2z_spl(mins[i]) > eps_down and  (z_smooth(mins[i]) -spl(mins[i]))  >= 1:
            grooves.append(mins[i])    #or roots, I dont know
    grooves=np.array(grooves)
    #print("All roots",roots)
    
    
    dz_mins = delta_z_spl(grooves)
    if dz_mins.size ==0:
        dz_mins=np.array([np.nan])
    
    return -1*np.average(dz_mins)

def get_std(array):
    x = np.linspace(0,1,array.shape[0])
    z = array  #data points

    
    spl = UnivariateSpline(x,z,s=5)
    
    z2 = spl(x)
    z_smooth = UnivariateSpline(x, z2, s=1e5)
    
    delta_z = z2 - z_smooth(x)
    
    return np.std(delta_z)