#!/usr/bin/env python

import numpy as np
from matplotlib.pyplot import *


def plot_polar_contour(values, azimuths, zeniths):
    """Plot a polar contour plot, with 0 degrees at the North.

    Arguments:

     * `values` -- A list (or other iterable - eg. a NumPy array) of the values to plot on the
     contour plot (the `z` values)
     * `azimuths` -- A list of azimuths (in degrees)
     * `zeniths` -- A list of zeniths (that is, radii)

    The shapes of these lists are important, and are designed for a particular
    use case (but should be more generally useful). The values list should be `len(azimuths) * len(zeniths)`
    long with data for the first azimuth for all the zeniths, then the second azimuth for all the zeniths etc.

    This is designed to work nicely with data that is produced using a loop as follows:

    values = []
    for azimuth in azimuths:
      for zenith in zeniths:
        # Do something and get a result
        values.append(result)

    After that code the azimuths, zeniths and values lists will be ready to be passed into this function.

    Cfr: http://blog.rtwilson.com/producing-polar-contour-plots-with-matplotlib/
    """
    theta = np.radians(azimuths)
    zeniths = np.array(zeniths)

    values = np.array(values)
    values = values.reshape(len(azimuths), len(zeniths))

    r, theta = np.meshgrid(zeniths, np.radians(azimuths))
    fig, ax = subplots(subplot_kw=dict(projection='polar'))

    # orientation of 0 and direction of azimuth
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    autumn()
    cax = ax.contourf(theta, r, values, 30)
    autumn()

    cb = fig.colorbar(cax)
    cb.set_label("Pixel reflectance")

    return fig, ax, cax


# main starts here
if __name__ == '__main__':
    azimuths = np.linspace(0, 360, 13)
    elevations = np.linspace(0, 90, 15)

    print('azimuths = %s' % azimuths)
    print('elevations = %s' % elevations)

    values = []
    for azimuth in azimuths:
        for elev in elevations:
            # Do something and get a result
            values.append(elev)

    figure, axis, caxis = plot_polar_contour(values, azimuths, elevations)

    figure.savefig('plotPolarContour.png')
