#!/usr/bin/env python3
"""Pre-download skyfield ephemeris during Render build phase"""
from skyfield.api import Loader

print("Downloading JPL ephemeris (de421.bsp)...")
load = Loader('.')
eph = load('de421.bsp')
ts = load.timescale()
print("Ephemeris ready.")
