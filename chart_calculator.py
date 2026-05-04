#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Birth Chart Calculator (Astrology + Bazi 八字)
Uses NASA JPL ephemeris (de421.bsp) via skyfield for precise solar calculations.

Requirements:
    uv pip install skyfield --system

The first run will download ~17MB de421.bsp ephemeris to ./skyfield_data
"""

from skyfield.api import Loader, wgs84
from datetime import datetime, timedelta
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# User Config
# ---------------------------------------------------------------------------
LAT = 25.009
LON = 121.458
YEAR, MONTH, DAY = 1999, 6, 7
HOUR, MINUTE = 15, 30
TZ_OFFSET = 8
GENDER = "女"  # 男 / 女

# ---------------------------------------------------------------------------
# Bazi Constants
# ---------------------------------------------------------------------------
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
GAN_YINYANG = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 1=陽, 0=陰
GAN_WUXING = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]  # 木火土金水
ZHI_WUXING = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]

DIZHI_CANGGAN = {
    "子": [("癸", 100)],
    "丑": [("己", 60), ("癸", 30), ("辛", 10)],
    "寅": [("甲", 60), ("丙", 30), ("戊", 10)],
    "卯": [("乙", 100)],
    "辰": [("戊", 60), ("乙", 30), ("癸", 10)],
    "巳": [("丙", 60), ("庚", 30), ("戊", 10)],
    "午": [("丁", 70), ("己", 30)],
    "未": [("己", 60), ("丁", 30), ("乙", 10)],
    "申": [("庚", 60), ("壬", 30), ("戊", 10)],
    "酉": [("辛", 100)],
    "戌": [("戊", 60), ("辛", 30), ("丁", 10)],
    "亥": [("壬", 70), ("甲", 30)],
}

# 五虎遁: 年干 -> 寅月起始天干
WUHU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

# 五鼠遁: 日干 -> 子時起始天干
WUSHU_DUN = {
    "甲": "甲", "己": "甲",
    "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊",
    "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}

# 節 (月建) 對應黃經
JIE_BY_ZHI = {
    "寅": 315, "卯": 345, "辰": 15, "巳": 45,
    "午": 75, "未": 105, "申": 135, "酉": 165,
    "戌": 195, "亥": 225, "子": 255, "丑": 285,
}
ZHI_CYCLE = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

SHISHEN_NAMES = ["比肩", "劫財", "食神", "傷官", "偏財", "正財", "七殺", "正官", "偏印", "正印"]

# ---------------------------------------------------------------------------
# Astrology Constants
# ---------------------------------------------------------------------------
ASTRO_SIGNS = [
    "白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座",
]

PLANETS = [
    ("sun", "太陽"), ("moon", "月亮"), ("mercury", "水星"),
    ("venus", "金星"), ("mars", "火星"), ("jupiter barycenter", "木星"),
    ("saturn barycenter", "土星"), ("uranus barycenter", "天王星"),
    ("neptune barycenter", "海王星"), ("pluto barycenter", "冥王星"),
]

OBLIQUITY_2000 = 23.4397


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def lon_to_sign(lon_deg: float) -> Tuple[str, float]:
    idx = int(lon_deg // 30) % 12
    return ASTRO_SIGNS[idx], lon_deg % 30


def get_shishen(day_gan: str, target_gan: str) -> str:
    """Calculate 十神 of target_gan relative to day_gan."""
    dg = TIANGAN.index(day_gan)
    tg = TIANGAN.index(target_gan)
    d_wx = GAN_WUXING[dg]
    t_wx = GAN_WUXING[tg]
    d_yy = GAN_YINYANG[dg]
    t_yy = GAN_YINYANG[tg]

    if t_wx == d_wx:
        return "比肩" if t_yy == d_yy else "劫財"
    # t_wx generates d_wx?  (t is mother of d)
    if d_wx == (t_wx + 1) % 5:
        return "正印" if t_yy != d_yy else "偏印"
    # d_wx generates t_wx?  (d is mother of t)
    if t_wx == (d_wx + 1) % 5:
        return "傷官" if t_yy != d_yy else "食神"
    # t_wx overcomes d_wx?  (t is officer to d)
    if d_wx == (t_wx + 2) % 5:
        return "正官" if t_yy != d_yy else "七殺"
    # d_wx overcomes t_wx
    return "正財" if t_yy != d_yy else "偏財"


def get_shishen_for_dizhi(day_gan: str, zhi: str) -> List[Tuple[str, str, int]]:
    """Return list of (canggan, shishen, percentage) for a dizhi."""
    return [(cg, get_shishen(day_gan, cg), pct) for cg, pct in DIZHI_CANGGAN[zhi]]


# ---------------------------------------------------------------------------
# Skyfield setup (lazy load inside functions)
# ---------------------------------------------------------------------------
_sf_load = None
_sf_planets = None
_sf_ts = None


def _skyfield():
    global _sf_load, _sf_planets, _sf_ts
    if _sf_load is None:
        _sf_load = Loader("./skyfield_data")
        _sf_planets = _sf_load("de421.bsp")
        _sf_ts = _sf_load.timescale()
    return _sf_load, _sf_planets, _sf_ts


def solar_longitude(t):
    _, planets, _ = _skyfield()
    earth = planets["earth"]
    sun = planets["sun"]
    astrometric = earth.at(t).observe(sun)
    app = astrometric.apparent()
    lat, lon, dist = app.ecliptic_latlon(epoch=None)
    return lon.degrees % 360


def find_term(year: int, target_deg: int) -> Optional[datetime]:
    """Find UTC datetime when Sun reaches target_deg ecliptic longitude."""
    load, planets, ts = _skyfield()
    # Approximate dates for solar terms (month, day)
    estimates = {
        315: (2, 4), 330: (2, 19), 345: (3, 6), 0: (3, 21),
        15: (4, 5), 30: (4, 20), 45: (5, 6), 60: (5, 21),
        75: (6, 6), 90: (6, 21), 105: (7, 7), 120: (7, 23),
        135: (8, 8), 150: (8, 23), 165: (9, 8), 180: (9, 23),
        195: (10, 8), 210: (10, 23), 225: (11, 7), 240: (11, 22),
        255: (12, 7), 270: (12, 22), 285: (1, 6), 300: (1, 20),
    }
    m, d = estimates.get(target_deg, (6, 6))
    t0 = ts.utc(year, m, d - 5)
    t1 = ts.utc(year, m, d + 5)
    times = ts.linspace(t0, t1, 10 * 24 + 1)
    lons = [solar_longitude(t) for t in times]

    tg = target_deg if target_deg != 0 else 360
    for i in range(len(lons) - 1):
        a, b = lons[i], lons[i + 1]
        if b < a:
            b += 360
        if a <= tg <= b:
            frac = (tg - a) / (b - a)
            dt1 = datetime(*[int(x) for x in times[i].utc[:6]])
            dt2 = datetime(*[int(x) for x in times[i + 1].utc[:6]])
            return dt1 + (dt2 - dt1) * frac
    return None


# ---------------------------------------------------------------------------
# Bazi Core
# ---------------------------------------------------------------------------
def get_day_pillar(solar_year, solar_month, solar_day):
    """Calculate day pillar using 2000-01-01 = 戊午日 as anchor."""
    from datetime import date
    base = date(2000, 1, 1)
    target = date(solar_year, solar_month, solar_day)
    delta = (target - base).days
    base_gan = 4   # 戊
    base_zhi = 6   # 午
    gan = (base_gan + delta) % 10
    zhi = (base_zhi + delta) % 12
    return TIANGAN[gan], DIZHI[zhi]


def get_hour_zhi(hour):
    """Convert 24h hour to dizhi."""
    zhis = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    # 23:00-01:00 is 子, etc.
    idx = ((hour + 1) // 2) % 12
    return zhis[idx]


def get_hour_pillar(day_gan, hour):
    zhi = get_hour_zhi(hour)
    start_gan = WUSHU_DUN[day_gan]
    zhi_idx = DIZHI.index(zhi)
    start_idx = TIANGAN.index(start_gan)
    gan = TIANGAN[(start_idx + zhi_idx) % 10]
    return gan, zhi


def calculate_bazi(year, month, day, hour, minute, gender, tz_offset):
    """Return (year_zhu, month_zhu, day_zhu, hour_zhu, dayun_list, start_age)."""
    # 1. Day pillar (independent of solar terms)
    day_gan, day_zhi = get_day_pillar(year, month, day)

    # 2. Year pillar (depends on 立春)
    lichun = find_term(year, 315)
    birth_local = datetime(year, month, day, hour, minute)
    birth_utc = birth_local - timedelta(hours=tz_offset)
    # Compare with 立春 (UTC)
    if lichun and birth_utc < lichun:
        # Before 立春, belong to previous year
        g = (year - 1 - 4) % 10
        z = (year - 1 - 4) % 12
    else:
        g = (year - 4) % 10
        z = (year - 4) % 12
    year_gan = TIANGAN[g]
    year_zhi = DIZHI[z]

    # 3. Month pillar (depends on Jie)
    # Find which Jie the birth falls into
    jie_degs = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
    zhis = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    month_zhi = None
    for i, deg in enumerate(jie_degs):
        term = find_term(year, deg)
        if term and birth_utc >= term:
            month_zhi = zhis[i]
        else:
            break
    if month_zhi is None:
        # Before 立春 (shouldn't happen after year check unless Dec/Jan)
        month_zhi = "丑"

    # Wuhu-dun
    start_gan = WUHU_DUN[year_gan]
    zhi_idx = ZHI_CYCLE.index(month_zhi)
    start_idx = TIANGAN.index(start_gan)
    month_gan = TIANGAN[(start_idx + zhi_idx) % 10]

    # 4. Hour pillar
    hour_gan, hour_zhi = get_hour_pillar(day_gan, hour)

    # 5. Dayun (Big Luck)
    year_yy = GAN_YINYANG[TIANGAN.index(year_gan)]
    if gender == "男":
        direction = 1 if year_yy == 1 else -1
    else:
        direction = -1 if year_yy == 1 else 1

    month_gan_idx = TIANGAN.index(month_gan)
    month_zhi_idx = DIZHI.index(month_zhi)
    dayun = []
    for i in range(1, 9):
        g = (month_gan_idx + direction * i) % 10
        z = (month_zhi_idx + direction * i) % 12
        dayun.append((TIANGAN[g], DIZHI[z]))

    # Calculate start age
    if direction == 1:
        next_zhi = ZHI_CYCLE[(ZHI_CYCLE.index(month_zhi) + 1) % 12]
        next_deg = JIE_BY_ZHI[next_zhi]
        term_time = find_term(year, next_deg)
    else:
        curr_deg = JIE_BY_ZHI[month_zhi]
        term_time = find_term(year, curr_deg)

    start_age = None
    if term_time:
        delta = abs((birth_utc - term_time).total_seconds())
        delta_days = delta / 86400.0
        start_age = delta_days / 3.0  # 3 days = 1 year

    return (year_gan, year_zhi), (month_gan, month_zhi), (day_gan, day_zhi), (hour_gan, hour_zhi), dayun, start_age


# ---------------------------------------------------------------------------
# Astrology Core
# ---------------------------------------------------------------------------
@dataclass
class PlanetPos:
    name: str
    lon: float
    sign: str
    deg: float
    retro: bool = False


@dataclass
class AstroChart:
    sun: PlanetPos
    moon: PlanetPos
    asc: PlanetPos
    mc: PlanetPos
    planets: List[PlanetPos]
    houses: List[str]


def calculate_astro(year, month, day, hour, minute, tz_offset, lat, lon):
    load, planets, ts = _skyfield()
    earth = planets["earth"]
    utc_hour = hour - tz_offset
    t = ts.utc(year, month, day, utc_hour, minute, 0)
    observer = earth + wgs84.latlon(lat, lon)

    positions = []
    for key, label in PLANETS:
        p = planets[key]
        astrometric = observer.at(t).observe(p)
        app = astrometric.apparent()
        lat_ecl, lon_ecl, dist = app.ecliptic_latlon(epoch=None)
        lon_deg = lon_ecl.degrees % 360
        sign, deg = lon_to_sign(lon_deg)
        # retrograde check
        t2 = ts.utc(year, month, day, utc_hour, minute + 1, 0)
        lon2 = observer.at(t2).observe(p).apparent().ecliptic_latlon(epoch=None)[1].degrees
        retro = (lon2 - lon_deg) < -0.01
        positions.append(PlanetPos(label, lon_deg, sign, deg, retro))

    # Ascendant
    gmst = t.gmst
    lst = (gmst + lon / 15) % 24
    lst_deg = lst * 15.0
    obl = OBLIQUITY_2000 * math.pi / 180
    lat_rad = lat * math.pi / 180
    lst_rad = lst_deg * math.pi / 180
    A = math.cos(lst_rad)
    B = -(math.sin(lst_rad) * math.cos(obl) + math.tan(lat_rad) * math.sin(obl))
    asc_deg = (math.atan2(A, B) * 180 / math.pi) % 360
    asc_sign, asc_deg_in = lon_to_sign(asc_deg)
    asc = PlanetPos("上升點", asc_deg, asc_sign, asc_deg_in)

    # MC
    mc_rad = math.atan2(math.sin(lst_rad), math.cos(lst_rad) * math.cos(obl))
    mc_deg = (mc_rad * 180 / math.pi) % 360
    mc_sign, mc_deg_in = lon_to_sign(mc_deg)
    mc = PlanetPos("MC 天頂", mc_deg, mc_sign, mc_deg_in)

    # Whole Sign Houses
    asc_idx = int(asc_deg // 30)
    houses = [ASTRO_SIGNS[(asc_idx + i) % 12] for i in range(12)]

    sun = next(p for p in positions if p.name == "太陽")
    moon = next(p for p in positions if p.name == "月亮")

    return AstroChart(sun, moon, asc, mc, positions, houses)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_combined():
    print("=" * 60)
    print("🌟 多維命盤計算結果 (Astrology + Bazi)")
    print("=" * 60)

    # --- Astrology ---
    astro = calculate_astro(YEAR, MONTH, DAY, HOUR, MINUTE, TZ_OFFSET, LAT, LON)
    print("\n【西洋占星命盤】")
    print(f"  太陽: {astro.sun.sign} {astro.sun.deg:.1f}°")
    print(f"  月亮: {astro.moon.sign} {astro.moon.deg:.1f}°")
    print(f"  上升: {astro.asc.sign} {astro.asc.deg:.1f}°")
    print(f"  MC:   {astro.mc.sign} {astro.mc.deg:.1f}°")
    print("\n  行星位置:")
    for p in astro.planets:
        retro = " [逆行]" if p.retro else ""
        print(f"    {p.name:6s}: {p.sign:6s} {p.deg:5.1f}°{retro}")
    print("\n  整宮制宮位:")
    hnames = ["1宮", "2宮", "3宮", "4宮", "5宮", "6宮", "7宮", "8宮", "9宮", "10宮", "11宮", "12宮"]
    for hn, hs in zip(hnames, astro.houses):
        print(f"    {hn}: {hs}")
    print("\n  行星落宮:")
    for p in astro.planets:
        hi = (int(p.lon // 30) - int(astro.asc.lon // 30)) % 12
        print(f"    {p.name} -> {hnames[hi]} ({astro.houses[hi]})")

    # --- Bazi ---
    year_zhu, month_zhu, day_zhu, hour_zhu, dayun, start_age = calculate_bazi(
        YEAR, MONTH, DAY, HOUR, MINUTE, GENDER, TZ_OFFSET
    )
    day_gan = day_zhu[0]

    print("\n" + "-" * 60)
    print("【八字四柱命盤】")
    print("-" * 60)
    print(f"{'':>8s} {'年柱':^8s} {'月柱':^8s} {'日柱':^8s} {'時柱':^8s}")
    print(f"{'天干':>8s} {year_zhu[0]:^8s} {month_zhu[0]:^8s} {day_zhu[0]:^8s} {hour_zhu[0]:^8s}")
    print(f"{'地支':>8s} {year_zhu[1]:^8s} {month_zhu[1]:^8s} {day_zhu[1]:^8s} {hour_zhu[1]:^8s}")

    # 十神 (relative to day master)
    print(f"\n{'十神':>8s}", end="")
    for gan in [year_zhu[0], month_zhu[0], day_zhu[0], hour_zhu[0]]:
        if gan == day_gan:
            print(f" {'日主':^8s}", end="")
        else:
            print(f" {get_shishen(day_gan, gan):^8s}", end="")
    print()

    # 地支藏干 & 十神
    print("\n【地支藏干】")
    for label, zhu in [("年支", year_zhu), ("月支", month_zhu), ("日支", day_zhu), ("時支", hour_zhu)]:
        zhi = zhu[1]
        cgs = get_shishen_for_dizhi(day_gan, zhi)
        cg_str = ", ".join([f"{cg}({ss})" for cg, ss, _ in cgs])
        print(f"  {label} {zhi}: {cg_str}")

    # 大運
    print("\n【大運】")
    if start_age is not None:
        y = int(start_age)
        m = int((start_age - y) * 12)
        print(f"  起運年齡: 約 {y} 歲 {m} 個月")
    else:
        print(f"  起運年齡: 計算中...")
    print(f"  {'大運':>6s} {'天干':>4s} {'地支':>4s}")
    for i, (g, z) in enumerate(dayun[:6], 1):
        age_start = int(start_age) + (i - 1) * 10 if start_age else "?"
        age_end = int(start_age) + i * 10 if start_age else "?"
        print(f"  第{i}運 ({age_start}-{age_end}歲): {g} {z}")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# MBTI Inference (Demonstration)
# ---------------------------------------------------------------------------
def mbti_inference():
    """Print MBTI inference based on chart patterns."""
    print("\n【MBTI 傾向推測 (基於命盤交叉分析)】")
    print("-" * 60)
    print("""
根據你的命盤特徵，以下是各維度的傾向分析：

  🔹 E/I (能量來源)
     八字: 甲木偏財透時干 + 寅申驛馬沖 -> 需要與外界互動、不喜靜守
     占星: 太陽雙子(外傾) + 上升天蠍(選擇性社交) + 金星獅子10宮(渴望被看見)
     → 推測: E (外向) 或 Ambivert，但社交是「目標導向型」而非全天候外放

  🔹 S/N (資訊獲取)
     八字: 偏財甲木 + 日支寅木 -> 喜歡新鮮、抽象、可能性
     占星: 太陽雙子 + 月亮雙魚 + 水星9宮 -> 直覺、聯想、抽象思考極強
     → 推測: 強 N (直覺)

  🔹 T/F (決策方式)
     八字: 庚金日主(剛毅/原則) vs 午火正官(社會規範/和諧)
     占星: 月亮雙魚(情感豐富) + 水星巨蟹(情感思考) + 太陽8宮(控制/深度)
     → 推測: F (情感) 為內核，但帶有強烈的 T 面具。對外人理性，對親密者感性。

  🔹 J/P (生活方式)
     八字: 寅申沖 + 偏財透 -> 極度變動、討厭計畫
     占星: 太陽雙子 + 月亮雙魚 + 火星天秤猶豫 -> 隨性、適應力強
     → 推測: 強 P (感知)

  🔹 認知功能排序推測
     Ne (外向直覺): ★★★★★  (雙子太陽 + 偏財思維)
     Fi (內向情感): ★★★★☆  (月亮雙魚 + 庚金之義)
     Te (外向思考): ★★★★☆  (金星10宮/MC獅子 + 日主庚金)
     Ni (內向直覺): ★★★☆☆  (上升天蠍 + 太陽8宮)

  📌 最可能類型: ENFP (競選者) 或 ENFJ (主人公)
     - ENFP 機率較高：你的命盤充滿「變動宮」能量，且 Ne-Fi 最能解釋
       你對命理/心理學/創意的多重興趣。
     - 若你測出是 ENFJ：可能是上升天蠍 + 月亮雙魚的「深度關懷」面
       被誤判為主導功能 Fe。
     - 較不可能是 INTJ/ISTJ：你的命盤幾乎沒有「靜態守成」的能量。
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print_combined()
    mbti_inference()
