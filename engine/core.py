"""Family Destiny Engine - Core Module"""
from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, date
from functools import lru_cache

# Lazy loading: 只在第一次使用時載入 16MB 星曆檔，避免反覆 I/O
_load = None
_eph = None
_ts = None

def _ensure_loaded():
    global _load, _eph, _ts
    if _eph is None:
        _load = Loader('.')
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

# 月柱地支對應的節氣起點黃經（節，不是氣）
# 寅月起立春315°，卯月起驚蟄345°，辰月起清明15°...
MONTH_TERM_DEG = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
MONTH_ZHI = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑']

# 節氣名稱對照
TERM_NAMES = {
    315: '立春', 330: '雨水', 345: '驚蟄', 0: '春分', 15: '清明', 30: '穀雨',
    45: '立夏', 60: '小滿', 75: '芒種', 90: '夏至', 105: '小暑', 120: '大暑',
    135: '立秋', 150: '處暑', 165: '白露', 180: '秋分', 195: '寒露', 210: '霜降',
    225: '立冬', 240: '小雪', 255: '大雪', 270: '冬至', 285: '小寒', 300: '大寒'
}


@lru_cache(maxsize=32)
def _solar_terms(year):
    """計算某年24節氣的精確時刻（UTC），返回 [(datetime, 黃經), ...]"""
    ts = get_ts()
    eph = get_eph()
    earth = eph['earth']
    sun = eph['sun']

    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year + 1, 1, 1)
    n = 1000
    times = ts.linspace(t0, t1, n)

    lats, lons, dists = earth.at(times).observe(sun).apparent().ecliptic_latlon(epoch=None)
    lons_deg = lons.degrees % 360

    terms = []
    for target in range(0, 360, 15):
        for i in range(n - 1):
            l0 = float(lons_deg[i])
            l1 = float(lons_deg[i + 1])
            # 處理 360/0 跨越
            if l0 > l1 and l0 > 300 and l1 < 60:
                l1 += 360
            t_adj = target if target >= l0 else target + 360
            if l0 <= t_adj <= l1:
                frac = (t_adj - l0) / (l1 - l0)
                t_term = times[i].tt + frac * (times[i + 1].tt - times[i].tt)
                dt_term = ts.tt_jd(t_term).utc_datetime().replace(tzinfo=None)
                terms.append((dt_term, target))
                break
    terms.sort()
    return terms


def bazi_pillars(dt):
    """計算八字四柱（精確節氣版）"""
    year = dt.year

    # --- 年柱：以當年立春為界 ---
    terms_this_year = _solar_terms(year)
    lichen = next((t for t, d in terms_this_year if d == 315), None)  # 當年立春

    if lichen and dt < lichen:
        y = year - 1
    else:
        y = year

    year_g = gan[(y - 4) % 10]
    year_z = zhi[(y - 4) % 12]

    # --- 月柱：精確節氣 ---
    # 需要前後兩年的節氣來確保邊界正確
    all_terms = _solar_terms(year - 1) + terms_this_year + _solar_terms(year + 1)
    month_terms = [(t, d) for t, d in all_terms if d in MONTH_TERM_DEG]
    month_terms.sort()

    month_idx = 11  # 默認丑月
    for i in range(len(month_terms) - 1):
        if month_terms[i][0] <= dt < month_terms[i + 1][0]:
            deg = month_terms[i][1]
            month_idx = MONTH_TERM_DEG.index(deg)
            break

    month_z = MONTH_ZHI[month_idx]

    # 五虎遁
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_idx = gan.index(tg_start[year_g])
    month_g = gan[(start_idx + month_idx) % 10]

    # --- 日柱 ---
    ref = date(1999, 6, 7)
    ref_idx = 26
    delta = (dt.date() - ref).days
    idx = (ref_idx + delta) % 60
    day_g = gan[idx % 10]
    day_z = zhi[idx % 12]

    # --- 時柱 ---
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
    for name, body in bodies.items():
        lat, lon, dist = e.observe(body).apparent().ecliptic_latlon(epoch=None)
        deg = lon.degrees % 360
        sign = signs[int(deg // 30) % 12]
        deg_in_sign = deg % 30
        result[name] = {'sign': sign, 'degree': round(deg_in_sign, 1), 'longitude': deg}
    return result
