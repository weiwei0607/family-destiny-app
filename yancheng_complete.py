from skyfield.api import Loader, wgs84
from skyfield import almanac
from skyfield.searchlib import find_discrete
from datetime import datetime, timedelta
import math

load = Loader('.')
eph = load('de421.bsp')
ts = load.timescale()
taipei = eph['earth'] + wgs84.latlon(25.0330, 121.5654)

stems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

def sun_longitude(t):
    """計算太陽黃經（簡化：用赤道轉黃道）"""
    e = taipei.at(t)
    ra, dec, dist = e.observe(eph['sun']).apparent().radec()
    return ra.hours * 15

def find_term(target_lon, year, month_start, month_end):
    """找太陽到達某黃經的時刻"""
    t0 = ts.utc(year, month_start, 1)
    t1 = ts.utc(year, month_end, 1)
    
    # 簡化線性搜尋
    t = t0
    best_t = None
    best_diff = 999
    
    while t.tt < t1.tt:
        lon = sun_longitude(t)
        diff = abs((lon - target_lon + 360) % 360)
        if diff < best_diff:
            best_diff = diff
            best_t = t
        if diff < 0.1:
            break
        t = ts.tt(t.tt + 0.01)
    
    # 精化
    if best_t:
        for _ in range(20):
            lon = sun_longitude(best_t)
            err = (lon - target_lon + 360) % 360
            if err > 180:
                err -= 360
            best_t = ts.tt(best_t.tt - err * 0.00027)  # 粗略修正
    
    return best_t

# ========== 農曆轉換器 ==========
def get_lunar_date(dt):
    """完整農曆轉換"""
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    year = dt.year
    
    # 找立春
    spring = find_term(0, year, 1, 3)  # 春分=0度，立春=315度
    if not spring or spring.utc.month > 3:
        spring = find_term(315, year-1, 12, 2)
    
    # 農曆年
    lichen = datetime(spring.utc.year, spring.utc.month, spring.utc.day, 
                       spring.utc.hour, spring.utc.minute)
    if dt < lichen:
        lunar_year = year - 1
    else:
        lunar_year = year
    
    # 找前後的朔日
    t0 = ts.utc(lunar_year-1, 11, 1)
    t1 = ts.utc(lunar_year+1, 3, 1)
    
    phases = almanac.moon_phases(eph)
    t_moons, y_moons = almanac.find_discrete(t0, t1, phases)
    new_moons = [ti for ti, yi in zip(t_moons, y_moons) if yi == 0]
    
    # 找到出生日期所在的朔日區間
    nm_idx = -1
    for i in range(len(new_moons)-1):
        if new_moons[i].tt <= t.tt < new_moons[i+1].tt:
            nm_idx = i
            lunar_day = int((t.tt - new_moons[i].tt) / ((new_moons[i+1].tt - new_moons[i].tt) / 30)) + 1
            if lunar_day > 30:
                lunar_day = 30
            break
    
    if nm_idx < 0:
        return lunar_year, 1, 1, False
    
    # 找中氣（雨水=330, 春分=0, 谷雨=30, 小滿=60, 夏至=90, 大暑=120,
    #         處暑=150, 秋分=180, 霜降=210, 小雪=240, 冬至=270, 大寒=300）
    zhongqi = [330, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    
    # 找到這個朔月區間內的中氣
    month_has_zhongqi = False
    for zq_lon in zhongqi:
        zq_t = None
        # 在兩個新月之間找中氣
        for t_test in [ts.tt((new_moons[i].tt + new_moons[i+1].tt)/2) for i in range(len(new_moons)-1)]:
            lon = sun_longitude(t_test)
            diff = abs((lon - zq_lon + 360) % 360)
            if diff < 15:
                # 在附近精搜
                zq_t = find_term(zq_lon, t_test.utc.year, t_test.utc.month-1, t_test.utc.month+1)
                break
        
        if zq_t and new_moons[nm_idx].tt <= zq_t.tt < new_moons[nm_idx+1].tt:
            month_has_zhongqi = True
            break
    
    # 確定農曆月
    # 從立春後的第一個新月開始數
    first_nm_after_lichen = None
    for i, nm in enumerate(new_moons):
        nm_dt = datetime(nm.utc.year, nm.utc.month, nm.utc.day)
        if nm_dt >= lichen:
            first_nm_after_lichen = i
            break
    
    if first_nm_after_lichen is None:
        first_nm_after_lichen = 0
    
    lunar_month = nm_idx - first_nm_after_lichen + 1
    is_leap = False
    
    # 閏月判斷：如果這個月沒有中氣，而且前一個月有中氣
    if not month_has_zhongqi and nm_idx > 0:
        is_leap = True
        lunar_month -= 1  # 重複前一個月的月名
    
    if lunar_month <= 0:
        lunar_month += 12
    if lunar_month > 12:
        lunar_month = (lunar_month - 1) % 12 + 1
        is_leap = True
    
    return lunar_year, lunar_month, lunar_day, is_leap

# ========== 測試農曆轉換 ==========
test_dates = [
    (1999, 1, 4), (2001, 11, 6), (1965, 10, 31), (1969, 4, 28), (1999, 1, 12)
]

for y, m, d in test_dates:
    dt = datetime(y, m, d)
    ly, lm, ld, leap = get_lunar_date(dt)
    leap_str = "閏" if leap else ""
    print(f"{y}-{m:02d}-{d:02d} -> 農曆 {ly}年 {leap_str}{lm}月 {ld}日")

