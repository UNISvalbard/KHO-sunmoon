# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:21:32 2024

@author: Mikko Syrjäsuo/University Centre in Svalbard

This script uses a quick approximation to compute the "shadow height"
above KHO. The part of the atmosphere above the shadow height is sunlit.


"""


import numpy as np
import astropy.units as u
from astropy.constants import R_earth
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import get_sun, get_body
from astroplan.moon import moon_illumination



def main():
#    mytime = Time('2024-12-26T12:00:00', format='isot', scale='utc')
    mytime = Time.now()

    kho = EarthLocation(lat=78.148*u.deg, lon=16.043*u.deg, height=520*u.m)
    obs_frame = AltAz(obstime=mytime, location=kho)
    sunaltaz = get_sun(mytime).transform_to(obs_frame)
    moonaltaz = get_body("moon",mytime,location=kho).transform_to(obs_frame)
    moonillum = np.max(moon_illumination(mytime))*100

    # Quick estimate assuming a perfectly spherical Earth
    # by Dan Whiter, Southampton University
    shadow_height=R_earth/np.cos(sunaltaz.alt.radian)-R_earth

    print("KHO observations at",mytime)
    print("- solar altitude %.1f degrees" % sunaltaz.alt.deg)
    print("- Zenith angle   %.1f degrees" % (90-sunaltaz.alt.deg))
    if sunaltaz.alt.deg<0:
        print("- shadow height  %.1f km" % shadow_height.to(u.km).value)
    print("- Moon altitude %.1f degrees" % moonaltaz.alt.deg)
    print("- Moon illumination %.1f %%" % moonillum)


if __name__ == "__main__":
    main()
