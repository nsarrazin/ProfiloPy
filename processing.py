import numpy as np
from scipy.ndimage.filters import median_filter
from scipy.interpolate import UnivariateSpline, CubicSpline

def pre_processing(array, threshold=0.5, zeroing=0, plotting=False):
    """
    input :
     - key, takes a int/float as a timestamp
     - threshold : threshold of the gradient filter
     - plotting : bool that decides wether or not to plot the process
    output: 
     - returns the array of points

     #FIXME: It seems like the errors get worse with preprocessing enabled
    """
    z = array

    corrector = [0]
    for grad in np.gradient(z):
        if np.abs(grad) > threshold:
            corrector.append(grad+corrector[-1])
            continue
        corrector.append(corrector[-1])

    corrector.pop(0)
    corrected = median_filter(z-corrector,5)
    
    zero = zeroing - corrected[0]
    corrected += zero
    
    return corrected

def get_delta_z(array):
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
    
    mins = [i for _,i in sorted(zip(delta_z_spl(roots),roots))]   
    
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
    
    return np.average(dz_mins)
