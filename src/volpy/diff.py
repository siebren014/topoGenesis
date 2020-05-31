
"""
Numerical Differentiation tools for volumetric data 
"""

import numpy as np

__author__ = "Shervin Azadi, and Pirouz Nourian"
__copyright__ = "???"
__credits__ = ["Shervin Azadi", "Pirouz Nourian"]
__license__ = "???"
__version__ = "0.0.2"
__maintainer__ = "Shervin Azadi"
__email__ = "shervinazadi93@gmail.com"
__status__ = "Dev"


def gradient(val):

    dx = (val[:-2, 1:-1, 1:-1] - val[2:, 1:-1, 1:-1])*0.5
    dy = (val[1:-1, :-2, 1:-1] - val[1:-1, 2:, 1:-1])*0.5
    dz = (val[1:-1, 1:-1, :-2] - val[1:-1, 1:-1, 2:])*0.5

    d = np.stack(dx, dy, dz)

    return(d)