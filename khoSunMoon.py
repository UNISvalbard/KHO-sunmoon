"""
Create a Sun & Moon plot for KHO
"""

import matplotlib
matplotlib.use('Agg')  # Run matplotlib in headless mode

import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style, quantity_support
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.coordinates import get_sun, get_moon
import datetime as dt
from astroplan.moon import moon_illumination, moon_phase_angle


def main():
    plt.style.use(astropy_mpl_style)
    quantity_support()

    kho = EarthLocation(lat=78.148*u.deg, lon=16.043*u.deg, height=520*u.m)

    dttoday = dt.datetime.utcnow()
    daystart = Time(dttoday.strftime("%Y-%m-%d"))
    daystart = Time('2020-10-21 00:00:00')
    timesteps = np.linspace(0, 24, 200)*u.hour
    oneDay = daystart+timesteps
    frame_oneDay = AltAz(obstime=oneDay, location=kho)

    sunaltazs = get_sun(oneDay).transform_to(frame_oneDay)
    moonaltazs = get_moon(oneDay).transform_to(frame_oneDay)

    maxmoon = np.max(moon_illumination(oneDay))*100

    # Prepare to save a fixed sized PNG
    my_dpi = 96
    rows = 500
    cols = 800
    plt.figure(figsize=(cols/my_dpi, rows/my_dpi), dpi=my_dpi)

    plt.plot(timesteps, sunaltazs.alt, color='r', label='Sun')
    plt.plot(timesteps, moonaltazs.alt, color=[0.75]*3, ls='--', label='Moon')

    # Civil twilight
    plt.fill_between(timesteps, -40*u.deg, 40*u.deg,
                     sunaltazs.alt <= -6*u.deg, color='0.4', zorder=0)

    # Nautical twilight
    plt.fill_between(timesteps, -40*u.deg, 40*u.deg,
                     sunaltazs.alt <= -12*u.deg, color='0.3', zorder=0)

    # Astronomical twilight
    plt.fill_between(timesteps, -40*u.deg, 40*u.deg,
                     sunaltazs.alt <= -18*u.deg, color='k', zorder=0)

    plt.legend(loc='upper left')
    plt.xlim(0, 24)
    plt.xticks(np.arange(13)*2)
    plt.ylim(-40*u.deg, 40*u.deg)
    plt.xlabel('Time (UTC)')
    plt.ylabel('Altitude [deg]')
    plt.title(dttoday.strftime("%Y-%m-%d") +
              '    Moon phase ='+str(int(np.round(maxmoon)))+'%')

    plt.savefig('sunmoon.png', dpi=my_dpi)


if __name__ == "__main__":
    main()
