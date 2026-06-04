#!/usr/bin/env python3
"""Pre-download skyfield ephemeris and build lunar.db during Render build phase"""
import os
import json
import sqlite3

# 1. Download JPL ephemeris
print("Downloading JPL ephemeris (de421.bsp) to ./skyfield_data ...")
from skyfield.api import Loader
os.makedirs('./skyfield_data', exist_ok=True)
load = Loader('./skyfield_data')
eph = load('de421.bsp')
ts = load.timescale()
print("Ephemeris ready.")

# 2. Build lunar.db from lunar_table.json
print("Building lunar.db from lunar_table.json ...")
json_path = os.path.join(os.path.dirname(__file__), 'lunar_table.json')
db_path = os.path.join(os.path.dirname(__file__), 'lunar.db')

with open(json_path, 'r', encoding='utf-8') as f:
    lunar_data = json.load(f)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lunar_days (
        solar_date TEXT PRIMARY KEY,
        lunar_year INTEGER,
        lunar_month INTEGER,
        lunar_day INTEGER,
        lunar_year_gz TEXT,
        is_leap_month BOOLEAN
    )
''')
cursor.execute('DELETE FROM lunar_days')

rows = []
for year_str, months in lunar_data.items():
    for month_str, days in months.items():
        for day_str, info in days.items():
            solar_date = f"{year_str}-{int(month_str):02d}-{int(day_str):02d}"
            rows.append((
                solar_date,
                info['lunar_year'],
                info['lunar_month'],
                info['lunar_day'],
                info['lunar_year_gz'],
                int(info['is_leap_month'])
            ))

cursor.executemany('''
    INSERT INTO lunar_days (solar_date, lunar_year, lunar_month, lunar_day, lunar_year_gz, is_leap_month)
    VALUES (?, ?, ?, ?, ?, ?)
''', rows)

conn.commit()
conn.close()
print(f"lunar.db built with {len(rows)} records.")
