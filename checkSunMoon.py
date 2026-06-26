# -*- coding: utf-8 -*-
"""
@author: Mikko Syrjäsuo/University Centre in Svalbard

Given a Sony quicklook filename, compute the location of the Sun and the Moon
as well as the Moon illumination etc.

"""

import argparse
import numpy as np
import datetime as dt
import astropy.units as u
from astropy.constants import R_earth
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import get_sun, get_body
import astroplan

from pathlib import Path
import re

def findSunMoon(mytime):
    kho = EarthLocation(lat=78.14779*u.deg, lon=16.04042*u.deg, height=517*u.m)
    frame_observation = AltAz(obstime=mytime, location=kho)
    sunaltaz = get_sun(mytime).transform_to(frame_observation)

    moonaltaz = get_body("moon",mytime).transform_to(frame_observation)
    moon_illumination = astroplan.moon_illumination(mytime)

    # Quick estimate assuming a perfectly spherical Earth
    # by Dan Whiter, Southampton University
    shadow_height=R_earth/np.cos(sunaltaz.alt.radian)-R_earth

    return sunaltaz.alt.deg, shadow_height.to(u.km).value, moonaltaz.alt.deg, 100*moon_illumination


def checkTwilightOrMoon(sonyqlfile, sun_angle_max=-12, moon_angle_max=0, moon_illum_min=50):
    """ Check the solar and lunar angles of a given Sony quicklook image filename. 
    If the Sun altitude is more than -12 deg and the Moon altitude is more than 0 degrees,
    print out the filename and the angles and Moon illumination
    """
    filepattern=r"LYR-Sony-(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d).jpg"
    checkname=re.match(filepattern, sonyqlfile)
    if checkname == None:
        return

    # There is probably a more stylish way to do this in python
    # but at least this is easy to understand...
    validname=re.split(filepattern, sonyqlfile)

    fileday=int(validname[3])
    filemonth=int(validname[2])
    fileyear=int(validname[1])

    filehh=int(validname[4])
    filemm=int(validname[5])
    filess=int(validname[6])

    # Check the date is actually a valid date
    datefromfile=f'{fileyear}-{filemonth:02}-{fileday:02}T{filehh:02}:{filemm:02}:{filess:02}Z'

    try:
        filedt=dt.datetime.fromisoformat(datefromfile)
        filedt.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        print('Funny date and time in',sonyqlfile)
        return
    fileTime=Time(filedt)

    sunAlt, _, moonAlt, moonIllum = findSunMoon(fileTime)
    
    if sunAlt>sun_angle_max or (moonAlt>moon_angle_max and moonIllum>=moon_illum_min):
        print(f'{sonyqlfile} {sunAlt:.1f} {moonAlt:.1f} {moonIllum:.1f}')

def checkTwilight(sonyqlfile, sun_angle_max=-12):
    """ Check the solar angle of a given Sony quicklook image filename. 
    If the Sun altitude is more than -12 deg,
    print out the filename and the angles and Moon illumination
    """
    filepattern=r"LYR-Sony-(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d).jpg"
    checkname=re.match(filepattern, sonyqlfile)
    if checkname == None:
        return

    # There is probably a more stylish way to do this in python
    # but at least this is easy to understand...
    validname=re.split(filepattern, sonyqlfile)

    fileday=int(validname[3])
    filemonth=int(validname[2])
    fileyear=int(validname[1])

    filehh=int(validname[4])# The Sony quicklook images have a strict filenaming conventioni
    filemm=int(validname[5])
    filess=int(validname[6])

    # Check the date is actually a valid date
    datefromfile=f'{fileyear}-{filemonth:02}-{fileday:02}T{filehh:02}:{filemm:02}:{filess:02}Z'

    try:
        filedt=dt.datetime.fromisoformat(datefromfile)
        filedt.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        print('Funny date and time in',sonyqlfile)
        return
    fileTime=Time(filedt)

    sunAlt, _, _ , _ = findSunMoon(fileTime)
    
    if sunAlt>sun_angle_max:
        print(f'{sonyqlfile} {sunAlt:.1f}')

def alternative_main_for_cli_use():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", 
                        help="Filename Date and time YYYY-MM-DDTHH:MM:SS (in UT)", 
                        default=None)
    args = parser.parse_args()
    
    sonyqlfile=Path(args.filename).name
    checkTwilight(sonyqlfile)

"""
Go through all files in a specified directory
"""
def main():
    sourceDir=Path('.')
    datafiles=list(sourceDir.glob('*.jpg'))
    for filepath in datafiles:
        checkTwilightOrMoon(filepath.name)

if __name__ == "__main__":
    main()