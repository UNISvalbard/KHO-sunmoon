# -*- coding: utf-8 -*-
"""
@author: Mikko Syrjäsuo/University Centre in Svalbard

The first analysis run with KHOnet2026 resulted in daily data files, where
each row comprised date and time and class probabilities (ClearAurora, 
ClearNoAurora, CloudyAurora, CloudyNoAurora) for individual images from that day.

For details of the classification method, 
see the preprint https://doi.org/10.5194/egusphere-2026-2388

Later we decided to add details of the solar altitude as well as lunar altitude
and illumination to the original classification results. This allows for
simple thresholding of data to e.g. ignore images during twilight conditions or
periods of full Moon high in the sky.

For each data line (i.e. date & time of captured image), we compute the location
of the Sun and Moon in relation to the local horizon. Also, the degree of Moon
illumination (0-100%) is provided.
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

    
def process_data_file(filepath):
    """
        Read the data file line by line and adds the solar and lunar altitudes plus 
        lunar illumination (0-100%) to each line. Each line should have the following
        items:

        year month day hours minutes seconds p1 p2 p3 p4

        where p1-p4 are the class probabilities
    """
    outputfile=Path(filepath).with_stem(Path(filepath).stem+"_smi")
    
    print(outputfile)
      
    
    try:
        with open(filepath,'r') as infile, open(outputfile,'w') as outfile:
            for line_num, line in enumerate(infile, start=1):
                parts=line.strip().split()

                # Skip empty lines
                if not parts:
                    continue

                # There should be one comment line specifiying the column
                # names: add the names of the new columns

                if line.strip().startswith('%'):
                    modified_comment=f"{line.rstrip()} sun_alt moon_alt moon_illumination"
                    outfile.write(modified_comment+"\n")
                    continue
                
                # Ignore lines with incorrect number of items
                if len(parts) != 10:
                    continue

                try:
                    year, month, day, hour, minute, second = parts[:6]
                    class_probs = parts[6:]

                    linetime=dt.datetime(
                        year=int(year), month=int(month), day=int(day),
                        hour=int(hour), minute=int(minute), second=int(second)
                    )
                    linetime.replace(tzinfo=dt.timezone.utc)

                    sun_alt, _ , moon_alt, moon_illumination = findSunMoon(Time(linetime))
                    outfile.write(f"{line.strip()} {sun_alt:.1f} {moon_alt:.1f} {moon_illumination:.1f} \n")
                    #return
                except ValueError as ve:
                    print(f"Parsing error at line {line_num}: {ve}")
    
    except FileNotFoundError:
        print(f"File not found: {filepath}")


if __name__ == "__main__":
    sourceDir=Path("/home/mikkos/CNN/CNN-20260317")

    datafiles=list(sourceDir.glob('*.txt'))
    for filepath in datafiles:
        process_data_file(filepath)