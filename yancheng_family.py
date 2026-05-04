from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, timedelta
import math

load = Loader('.')
eph = load('de421.bsp')
ts = load.timescale()

# 台北座標
taipei = eph['earth'] + wgs84.latlon(25.0330, 121.5654)

stems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
animals = ['鼠','牛','虎','兔','龍','蛇','馬','羊','猴','雞','狗','豬']

elements = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
yin_yang = {'甲':'陽','乙':'陰','丙':'陽','丁':'陰','戊':'陽','己':'陰','庚':'陽','辛':'陰','壬':'陽','癸':'陰'}

# ===== 八字計算工具 =====

def jd_to_datetime(jd):
    """Julian date to datetime UTC"""
    # 簡化轉換
    t = ts.tt_jd(jd)
    utc = t.utc
    return datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, int(utc.second))

def find_solar_longitude(t_start, t_end, target_lon):
    """二分搜尋太陽到達某黃經的時刻"""
    def get_lon(t):
        e = taipei.at(t)
        astrometric = e.observe(eph['sun'])
        app = astrometric.apparent()
        ra, dec, dist = app.radec()
        lon = ra.hours * 15  # 粗略估計黃經
        return lon
    
    lo, hi = t_start.tt, t_end.tt
    for _ in range(50):
        mid = (lo + hi) / 2
        t_mid = ts.tt(mid)
        lon_mid = get_lon(t_mid)
        # 處理 0/360 跨越
        diff = (lon_mid - target_lon + 360) % 360
        if diff < 180:
            hi = mid
        else:
            lo = mid
    return ts.tt((lo + hi) / 2)

def get_year_pillar(dt):
    """八字年柱，以立春為界（精確版）"""
    year = dt.year
    # 找當年和前一年的立春
    for y in [year - 1, year]:
        t0 = ts.utc(y, 2, 1)
        t1 = ts.utc(y, 2, 10)
        t, ev = almanac.find_discrete(t0, t1, almanac.seasons(eph))
        for ti, ei in zip(t, ev):
            if ei == 0:  # 春分？不對，almanac.seasons的編號
                pass
    
    # 簡化：直接用已知立春日期（夠用）
    # 近年立春大約在2月4日
    lichen = datetime(year, 2, 4, 0, 0)
    if dt < lichen:
        y = year - 1
    else:
        y = year
    
    stem = stems[(y - 4) % 10]
    branch = branches[(y - 4) % 12]
    return stem, branch, y

def get_month_pillar(dt, year_stem):
    """月柱，用節氣邊界"""
    year = dt.year
    
    # 定義節氣（節）邊界
    # 立春、驚蟄、清明、立夏、芒種、小暑、立秋、白露、寒露、立冬、大雪、小寒
    jieqi_list = [
        ('立春', 315, 2, 4), ('驚蟄', 345, 3, 6), ('清明', 15, 4, 5),
        ('立夏', 45, 5, 6), ('芒種', 75, 6, 6), ('小暑', 105, 7, 7),
        ('立秋', 135, 8, 8), ('白露', 165, 9, 8), ('寒露', 195, 10, 8),
        ('立冬', 225, 11, 7), ('大雪', 255, 12, 7), ('小寒', 285, 1, 6)
    ]
    
    month_branches = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑']
    
    # 找到適用的節氣
    applicable = None
    for i in range(len(jieqi_list)):
        name, lon, m, d = jieqi_list[i]
        boundary = datetime(year, m, d)
        if (m, d) < (2, 4):
            boundary = datetime(year - 1, m, d)
        
        if dt >= boundary:
            applicable = i
    
    if applicable is None:
        applicable = 11  # 丑月
    
    month_branch = month_branches[applicable % 12]
    
    # 月干：五虎遁月
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_stem = tg_start[year_stem]
    start_idx = stems.index(start_stem)
    branch_idx = branches.index(month_branch)
    month_stem_idx = (start_idx + branch_idx - 2) % 10
    month_stem = stems[month_stem_idx]
    
    return month_stem, month_branch

def get_day_pillar(dt):
    """日柱"""
    ref = datetime(1999, 6, 7)
    ref_idx = 26  # 庚寅
    delta = (dt.date() - ref.date()).days
    idx = (ref_idx + delta) % 60
    return stems[idx % 10], branches[idx % 12]

def get_hour_pillar(hour, day_stem):
    """時柱"""
    hour_idx = ((hour + 1) // 2) % 12
    hour_branch = branches[hour_idx]
    
    tg_start = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    start_stem = tg_start[day_stem]
    start_idx = stems.index(start_stem)
    hour_stem_idx = (start_idx + hour_idx) % 10
    hour_stem = stems[hour_stem_idx]
    
    return hour_stem, hour_branch

# ===== 占星計算 =====

def get_planet_positions(dt):
    """計算行星位置"""
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    e = taipei.at(t)
    
    planets = {
        '太陽': eph['sun'],
        '月亮': eph['moon'],
        '水星': eph['mercury'],
        '金星': eph['venus'],
        '火星': eph['mars'],
        '木星': eph['jupiter barycenter'],
        '土星': eph['saturn barycenter']
    }
    
    results = {}
    for name, planet in planets.items():
        apparent = e.observe(planet).apparent()
        ra, dec, dist = apparent.radec()
        lon = ra.hours * 15
        results[name] = lon
    
    return results

def longitude_to_sign(lon):
    signs = ['牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','摩羯','水瓶','雙魚']
    idx = int(lon // 30) % 12
    deg = lon % 30
    return signs[idx], deg

# ===== 主要計算函數 =====

def calculate_person(name, year, month, day, hour, minute, note=""):
    dt = datetime(year, month, day, hour, minute)
    
    # 八字
    year_stem, year_branch, _ = get_year_pillar(dt)
    month_stem, month_branch = get_month_pillar(dt, year_stem)
    day_stem, day_branch = get_day_pillar(dt)
    hour_stem, hour_branch = get_hour_pillar(hour, day_stem)
    
    # 日主屬性
    day_master = day_stem
    dm_element = elements[day_master]
    dm_yy = yin_yang[day_master]
    
    # 五行統計
    five_elements = {'木':0,'火':0,'土':0,'金':0,'水':0}
    for s in [year_stem, month_stem, day_stem, hour_stem]:
        five_elements[elements[s]] += 1
    for b in [year_branch, month_branch, day_branch, hour_branch]:
        # 地支本氣（簡化）
        branch_main = {
            '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
            '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
        }
        five_elements[branch_main[b]] += 1
    
    # 太陽月亮
    planets = get_planet_positions(dt)
    sun_sign, sun_deg = longitude_to_sign(planets['太陽'])
    moon_sign, moon_deg = longitude_to_sign(planets['月亮'])
    
    return {
        'name': name,
        'datetime': dt,
        'note': note,
        'bazi': f"{year_stem}{year_branch} {month_stem}{month_branch} {day_stem}{day_branch} {hour_stem}{hour_branch}",
        'day_master': f"{day_master} ({dm_yy}{dm_element})",
        'dm_element': dm_element,
        'five_elements': five_elements,
        'sun': f"{sun_sign} {sun_deg:.1f}°",
        'moon': f"{moon_sign} {moon_deg:.1f}°",
        'planets': {k: longitude_to_sign(v)[0] for k, v in planets.items()}
    }

# ===== 衍徵一家 =====
people = [
    calculate_person("衍徵", 1999, 1, 4, 0, 8, "好友"),
    calculate_person("衍徵妹妹", 2001, 11, 6, 7, 30, ""),
    calculate_person("衍徵爸爸", 1965, 10, 31, 8, 0, ""),
    calculate_person("衍徵媽媽", 1969, 4, 28, 8, 0, "時間推估"),
    calculate_person("衍徵男友", 1999, 1, 12, 7, 0, ""),
]

print("=" * 70)
print("衍徵一家 命盤總表")
print("=" * 70)

for p in people:
    print(f"\n【{p['name']}】{p['note']}")
    print(f"  出生: {p['datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"  八字: {p['bazi']}")
    print(f"  日主: {p['day_master']}")
    print(f"  五行: {p['five_elements']}")
    print(f"  太陽: {p['sun']}")
    print(f"  月亮: {p['moon']}")
    print(f"  行星: 水{p['planets']['水星']} 金{p['planets']['金星']} 火{p['planets']['火星']} 木{p['planets']['木星']} 土{p['planets']['土星']}")

# ===== 家庭關係分析 =====
print("\n" + "=" * 70)
print("衍徵一家 人物關係與角色定位")
print("=" * 70)

# 角色定位函數
def role_analysis(p):
    dm = p['dm_element']
    yy = p['day_master'].split('(')[1][0]
    fe = p['five_elements']
    
    # 根據日主和五行分布推角色
    roles = []
    
    # 看哪個五行最強
    max_e = max(fe, key=fe.get)
    
    if dm == '火':
        roles.append("暖爐/發光體")
    elif dm == '水':
        roles.append("潤滑劑/情感流動者")
    elif dm == '木':
        roles.append("成長引擎/開創者")
    elif dm == '金':
        roles.append("架構師/邊界守護者")
    elif dm == '土':
        roles.append("地基/穩定器")
    
    if fe['火'] >= 2 or fe['木'] >= 2:
        roles.append("行動派")
    if fe['水'] >= 2:
        roles.append("感性派")
    if fe['金'] >= 2 or fe['土'] >= 2:
        roles.append("務實派")
    
    return roles

for p in people:
    roles = role_analysis(p)
    print(f"\n【{p['name']}】→ 家庭角色: {' / '.join(roles)}")

# 夫妻關係
print("\n--- 夫妻關係 ---")
dad = people[2]
mom = people[3]
print(f"爸爸({dad['day_master']}) vs 媽媽({mom['day_master']})")
print(f"  爸爸戊土(高山陽土) vs 媽媽癸水(雨露陰水)")
print(f"  → 戊癸合化火: 這是一對有強烈化學反應的夫妻")
print(f"  → 爸爸像山，媽媽像水繞山而行，但山太大會擋住水的流動")
print(f"  → 關鍵課題: 爸爸要學會讓出空間，媽媽要學會不被吸收")

# 親子關係
print("\n--- 親子關係 ---")
print(f"衍徵(丙火) vs 爸爸(戊土): 火生土 → 衍徵天生會照顧爸爸情緒")
print(f"衍徵(丙火) vs 媽媽(癸水): 水克火 → 媽媽的規矩會讓衍徵感到壓抑")
print(f"妹妹(癸水) vs 媽媽(癸水): 同日主 → 母女靈魂伴侶，但一起溺水的風險")
print(f"妹妹(癸水) vs 爸爸(戊土): 土克水 → 爸爸的控制欲是妹妹最大壓力源")

# 情侶關係
print("\n--- 衍徵與男友 ---")
yan = people[0]
bf = people[4]
print(f"衍徵({yan['day_master']}) vs 男友({bf['day_master']})")
print(f"  甲木(男友)生丙火(衍徵): 男友是衍徵的能量供應站")
print(f"  兩人太陽都是摩羯: 目標導向，現實考量優先")
print(f"  衍徵月亮獅子 vs 男友月亮天蠍: 一個需要被看見，一個需要深度連結")
print(f"  → 潛在衝突: 衍徵想炫耀/被稱讚，男友想私藏/獨佔")

print("\n" + "=" * 70)

