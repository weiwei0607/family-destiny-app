#!/usr/bin/env python3
"""Pre-download skyfield ephemeris during Render build phase"""
from skyfield.api import Loader

print("Downloading JPL ephemeris (de421.bsp) to ./skyfield_data ...")
import os
os.makedirs('./skyfield_data', exist_ok=True)
load = Loader('./skyfield_data')
eph = load('de421.bsp')
ts = load.timescale()
print("Ephemeris ready.")
