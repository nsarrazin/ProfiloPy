import numpy as np
from scipy.ndimage.filters import median_filter
from scipy.interpolate import UnivariateSpline, CubicSpline

def preprocessor_1(array, threshold=2, zeroing=0, plotting=False):
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