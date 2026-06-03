"""Family Destiny Engine - Core Module"""
from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, date
from pathlib import Path

# 指向專案根目錄（de421.bsp 所在位置）
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Lazy loading: 只在第一次使用時載入 16MB 星曆檔，避免反覆 I/O
_load = None
_eph = None
_ts = None

def _ensure_loaded():
    global _load, _eph, _ts
    if _eph is None:
        _load = Loader(str(_PROJECT_ROOT))
        _eph = _load('de421.bsp')
        _ts = _load.timescale()

def get_eph():
    _ensure_loaded()
    return _eph

def get_ts():
    _ensure_loaded()
    return _ts

def get_observer(lat=25.0330, lon=121.5654):
    eph = get_eph()
    return eph['earth'] + wgs84.latlon(lat, lon)

gan = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
zhi = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

def bazi_pillars(dt):
    """計算八字四柱"""
    # 年柱（立春為界）
    lichen = datetime(dt.year, 2, 4)
    if dt < lichen:
        y = dt.year - 1
    else:
        y = dt.year
    year_g = gan[(y - 4) % 10]
    year_z = zhi[(y - 4) % 12]
    
    # 月柱（精確節氣版）
    jieqi = [
        (2, 4, 0), (3, 6, 1), (4, 5, 2), (5, 6, 3),
        (6, 6, 4), (7, 7, 5), (8, 8, 6), (9, 8, 7),
        (10, 8, 8), (11, 7, 9), (12, 7, 10), (1, 6, 11)
    ]
    lunar_year = y  # 與年柱相同的農曆年
    next_lichen = datetime(lunar_year + 1, 2, 4)
    month_idx = 11
    for m, d, mb in jieqi:
        if m >= 2:
            boundary = datetime(lunar_year, m, d)
        else:
            boundary = datetime(lunar_year + 1, m, d)
        if datetime(lunar_year, 2, 4) <= boundary < next_lichen:
            if dt >= boundary:
                month_idx = mb
    month_z = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'][month_idx]
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_idx = gan.index(tg_start[year_g])
    month_g = gan[(start_idx + month_idx) % 10]
    
    # 日柱
    ref = date(1999, 6, 7)
    ref_idx = 26
    delta = (dt.date() - ref).days
    idx = (ref_idx + delta) % 60
    day_g = gan[idx % 10]
    day_z = zhi[idx % 12]
    
    # 時柱
    hi = ((dt.hour + 1) // 2) % 12
    hour_z = zhi[hi]
    tg_hstart = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    hstart_idx = gan.index(tg_hstart[day_g])
    hour_g = gan[(hstart_idx + hi) % 10]
    
    return {
        'year': f"{year_g}{year_z}", 'month': f"{month_g}{month_z}",
        'day': f"{day_g}{day_z}", 'hour': f"{hour_g}{hour_z}",
        'day_master': day_g, 'day_master_zhi': day_z
    }

def western_astrology(dt, lat=25.0330, lon=121.5654):
    eph = get_eph()
    ts = get_ts()
    observer = get_observer(lat, lon)
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    e = observer.at(t)
    bodies = {
        '太陽': eph['sun'], '月亮': eph['moon'], '水星': eph['mercury'],
        '金星': eph['venus'], '火星': eph['mars'], '木星': eph['jupiter barycenter'],
        '土星': eph['saturn barycenter']
    }
    signs = ['牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','摩羯','水瓶','雙魚']
    result = {}
    for planet_name, body in bodies.items():
        ra, dec, dist = e.observe(body).apparent().radec()
        ecl_lon = ra.hours * 15
        sign = signs[int(ecl_lon // 30) % 12]
        deg = ecl_lon % 30
        result[planet_name] = {'sign': sign, 'degree': round(deg, 1), 'longitude': ecl_lon}
    return result
