"""人類圖 (Human Design) 計算模組 — 真實 Rave Mandala

使用 Swiss Ephemeris 計算 Personality（出生時）和 Design（出生前約 88° 太陽弧）
兩層共 26 個天體位置（13 conscious + 13 unconscious）
"""

import swisseph as swe
import pytz
from datetime import datetime, timedelta

# Rave Mandala 閘門順序（從雙魚座 28°15′ 開始，順時針排列）
# 每個閘門 5.625°，每條爻 (line) 0.9375°
# 基於標準人類圖 Rave Mandala 映射（參考 Barney+flow 等權威來源）
GATE_ORDER = [
    25, 17, 21, 51, 42, 3, 27, 24,
    2, 23, 8, 20, 16, 35, 45, 12,
    15, 52, 39, 53, 62, 56, 31, 33,
    7, 4, 29, 59, 40, 64, 47, 6,
    46, 18, 48, 57, 32, 50, 28, 44,
    1, 43, 14, 34, 9, 5, 26, 11,
    10, 58, 38, 54, 61, 60, 41, 19,
    13, 49, 30, 55, 37, 63, 22, 36
]

# 各閘門精確起點（黃道經度，單位：度）
GATE_START = {
    25: 358.25, 17: 3.875, 21: 9.5, 51: 15.125, 42: 20.75, 3: 26.375,
    27: 32.0, 24: 37.625, 2: 43.125, 23: 48.625, 8: 54.125, 20: 60.125,
    16: 65.75, 35: 71.375, 45: 77.0, 12: 82.625, 15: 88.125, 52: 93.875,
    39: 99.5, 53: 105.125, 62: 110.75, 56: 116.375, 31: 122.0, 33: 127.625,
    7: 133.25, 4: 138.875, 29: 144.5, 59: 150.125, 40: 155.75, 64: 161.375,
    47: 167.0, 6: 172.625, 46: 178.25, 18: 183.875, 48: 189.5, 57: 195.125,
    32: 200.75, 50: 206.375, 28: 212.0, 44: 217.625, 1: 223.25, 43: 228.875,
    14: 234.5, 34: 240.125, 9: 245.75, 5: 251.375, 26: 257.0, 11: 262.625,
    10: 268.125, 58: 273.875, 38: 279.5, 54: 285.125, 61: 290.75, 60: 296.375,
    41: 302.0, 19: 307.625, 13: 313.125, 49: 318.625, 30: 324.125, 55: 330.125,
    37: 335.75, 63: 341.375, 22: 347.0, 36: 352.625
}

GATE_DEGREE = 5.625
LINE_DEGREE = 0.9375

# 九個中心對應的閘門
CENTERS = {
    '頭腦': [61, 63, 64],
    '邏輯': [47, 24, 4, 17, 43, 11],
    '喉嚨': [62, 23, 56, 16, 35, 12, 45, 33, 20, 31, 8, 7],
    'G中心': [1, 13, 25, 46, 10, 15, 7, 2],
    '心輪': [26, 44, 51, 21, 40],
    '情緒': [36, 22, 37, 6, 49, 55, 30],
    '薦骨': [9, 5, 52, 53, 29, 14, 34, 27, 50, 59, 3, 42, 44],
    '脾/直覺': [48, 57, 18, 28, 44, 50, 32],
    '根部': [58, 38, 54, 19, 39, 41, 60, 52]
}

# 36 條標準通道（閘門對）
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59),
    (7, 31), (9, 52), (10, 20), (10, 34), (10, 57), (11, 56),
    (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49),
    (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (25, 51),
    (26, 44), (27, 50), (28, 38), (29, 46), (30, 41), (32, 54),
    (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64)
]

PLANET_IDS = {
    '太陽': swe.SUN,
    '月亮': swe.MOON,
    '水星': swe.MERCURY,
    '金星': swe.VENUS,
    '火星': swe.MARS,
    '木星': swe.JUPITER,
    '土星': swe.SATURN,
    '天王星': swe.URANUS,
    '海王星': swe.NEPTUNE,
    '冥王星': swe.PLUTO,
    '北交點': swe.MEAN_NODE,
}


def lon_to_gate_line(longitude):
    """黃經轉 Rave Mandala 閘門+爻（使用精確閘門起點）"""
    lon = longitude % 360
    # Gate 25 跨越 360° 邊界（358.25° ~ 3.875°）
    if lon >= 358.25 or lon < 3.875:
        gate = 25
        offset = lon - 358.25 if lon >= 358.25 else lon + 360 - 358.25
        line = int(offset // LINE_DEGREE) + 1
        return gate, min(line, 6)
    # 線性搜尋（64 個閘門，效率完全足夠）
    for gate in GATE_ORDER[1:]:
        start = GATE_START[gate]
        if start <= lon < start + GATE_DEGREE:
            offset = lon - start
            line = int(offset // LINE_DEGREE) + 1
            return gate, min(line, 6)
    return 25, 1


def _find_design_date(birth_dt):
    """找到 Design 日期：出生前太陽回退 88° 的時刻"""
    # 先轉 UTC
    dt_utc = birth_dt.astimezone(pytz.UTC)
    jd_birth = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                          dt_utc.hour + dt_utc.minute / 60)
    sun_birth = swe.calc_ut(jd_birth, swe.SUN)[0][0]

    # 估計約 88-92 天前（太陽每天約 0.9856°）
    low = dt_utc - timedelta(days=120)
    high = dt_utc - timedelta(days=60)

    for _ in range(50):
        mid = low + (high - low) / 2
        jd_mid = swe.julday(mid.year, mid.month, mid.day,
                            mid.hour + mid.minute / 60)
        sun_mid = swe.calc_ut(jd_mid, swe.SUN)[0][0]

        # 太陽回退角度（Personality - Design），處理 360° 環繞
        diff = (sun_birth - sun_mid) % 360
        if diff > 180:
            diff -= 360

        if diff < 88:
            high = mid
        else:
            low = mid

    return high


def _calc_layer(dt_utc):
    """計算某一層（Personality 或 Design）的 13 個天體閘門位置"""
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute / 60)

    longitudes = {}
    for name, pid in PLANET_IDS.items():
        lon = swe.calc_ut(jd, pid)[0][0]
        longitudes[name] = lon

    # 地球 = 太陽對宮
    longitudes['地球'] = (longitudes['太陽'] + 180) % 360
    # 南交點 = 北交點對宮
    longitudes['南交點'] = (longitudes['北交點'] + 180) % 360

    gates = {}
    details = {}
    for name, lon in longitudes.items():
        g, l = lon_to_gate_line(lon)
        gates[name] = g
        details[name] = {'gate': g, 'line': l, 'longitude': round(lon, 2)}

    return gates, details


def calculate_hd(birth_dt):
    """
    計算完整人類圖（Personality + Design）

    birth_dt: timezone-aware datetime
    """
    design_dt = _find_design_date(birth_dt)
    dt_utc = birth_dt.astimezone(pytz.UTC)
    design_utc = design_dt.astimezone(pytz.UTC)

    p_gates, p_details = _calc_layer(dt_utc)
    d_gates, d_details = _calc_layer(design_utc)

    # 所有定義閘門（Personality + Design 的聯集）
    all_gates = set(p_gates.values()) | set(d_gates.values())

    # 激活通道
    active_channels = []
    for g1, g2 in CHANNELS:
        if g1 in all_gates and g2 in all_gates:
            active_channels.append((g1, g2))

    # 中心定義：有完整通道連接的才算定義
    connected_gates = set()
    for g1, g2 in active_channels:
        connected_gates.add(g1)
        connected_gates.add(g2)

    defined_centers = set()
    for center_name, gates in CENTERS.items():
        if any(g in connected_gates for g in gates):
            defined_centers.add(center_name)

    # Profile = Personality 太陽爻 / Design 太陽爻
    profile = f"{p_details['太陽']['line']}/{d_details['太陽']['line']}"

    # 能量類型
    has_sacral = '薦骨' in defined_centers
    has_throat = '喉嚨' in defined_centers
    has_motor = bool(defined_centers & {'情緒', '心輪', '根部'})

    # 顯示生產者需要「薦骨到喉嚨」的通道，或薦骨 + 動力中心有通道連到喉嚨
    # 簡化判定：薦骨定義 + 喉嚨定義 + 兩者之間有連接（通過通道間接或直接）
    # 由於我們已經計算了 active_channels，檢查是否有從薦骨中心到喉嚨中心的路徑
    sacral_to_throat = _has_path_between_centers('薦骨', '喉嚨', defined_centers, active_channels)

    if has_sacral:
        if sacral_to_throat and has_motor:
            energy_type = "顯示生產者"
        else:
            energy_type = "生產者"
    elif has_throat and has_motor:
        energy_type = "顯示者"
    elif len(defined_centers) == 0:
        energy_type = "反映者"
    else:
        energy_type = "投射者"

    # 內在權威（優先順序）
    if '情緒' in defined_centers:
        authority = "情緒權威"
    elif '薦骨' in defined_centers:
        authority = "薦骨權威"
    elif '脾/直覺' in defined_centers:
        authority = "直覺權威"
    elif '心輪' in defined_centers:
        authority = "意志力權威"
    elif 'G中心' in defined_centers:
        authority = "自我投射權威"
    elif len(defined_centers) == 0:
        authority = "月亮週期權威（反映者）"
    else:
        authority = "無內在權威（環境/頭腦）"

    # 策略
    if energy_type == "生產者":
        strategy = "等待回應"
    elif energy_type == "顯示生產者":
        strategy = "等待回應，再行動"
    elif energy_type == "顯示者":
        strategy = "告知後行動"
    elif energy_type == "投射者":
        strategy = "等待邀請"
    else:
        strategy = "等待 28 天月亮週期"

    # 非自己主題
    if energy_type in ("生產者", "顯示生產者"):
        not_self = "挫敗感"
    elif energy_type == "顯示者":
        not_self = "憤怒"
    elif energy_type == "投射者":
        not_self = "苦澀"
    else:
        not_self = "失望"

    return {
        'energy_type': energy_type,
        'profile': profile,
        'authority': authority,
        'strategy': strategy,
        'not_self': not_self,
        'definition': _definition_type(len(defined_centers), active_channels),
        'defined_gates': sorted(all_gates),
        'active_channels': active_channels,
        'defined_centers': sorted(defined_centers),
        'personality_gates': p_gates,
        'design_gates': d_gates,
        'personality_details': p_details,
        'design_details': d_details,
        'design_date': design_utc.strftime('%Y-%m-%d %H:%M UTC'),
    }


def _has_path_between_centers(c1, c2, defined_centers, active_channels):
    """檢查兩個中心之間是否有通道路徑（簡化版 BFS）"""
    if c1 not in defined_centers or c2 not in defined_centers:
        return False

    # 建立中心之間的通道連接圖
    center_of_gate = {}
    for cn, gates in CENTERS.items():
        for g in gates:
            center_of_gate[g] = cn

    # 直接通道
    for g1, g2 in active_channels:
        c1_g = center_of_gate.get(g1)
        c2_g = center_of_gate.get(g2)
        if (c1_g == c1 and c2_g == c2) or (c1_g == c2 and c2_g == c1):
            return True

    # 間接路徑（BFS，最多經過 2 個中轉中心）
    from collections import deque
    queue = deque([c1])
    visited = {c1}
    steps = 0
    while queue and steps < 5:
        for _ in range(len(queue)):
            current = queue.popleft()
            if current == c2:
                return True
            # 找到從 current 中心出發的所有通道另一端中心
            for g1, g2 in active_channels:
                cg1 = center_of_gate.get(g1)
                cg2 = center_of_gate.get(g2)
                if cg1 == current and cg2 not in visited:
                    visited.add(cg2)
                    queue.append(cg2)
                elif cg2 == current and cg1 not in visited:
                    visited.add(cg1)
                    queue.append(cg1)
        steps += 1
    return False


def _definition_type(num_centers, channels):
    """計算定義類型（一分人 / 二分人 / 三分人 / 四分人）"""
    if num_centers == 0:
        return "無定義"
    # 檢查所有定義中心是否通過通道連成一片
    center_of_gate = {}
    for cn, gates in CENTERS.items():
        for g in gates:
            center_of_gate[g] = cn

    # 建立中心連接圖
    adj = {c: set() for c in CENTERS.keys()}
    for g1, g2 in channels:
        c1 = center_of_gate.get(g1)
        c2 = center_of_gate.get(g2)
        if c1 and c2 and c1 != c2:
            adj[c1].add(c2)
            adj[c2].add(c1)

    # 找到所有在 active_channels 中出現的中心
    defined = set()
    for g1, g2 in channels:
        defined.add(center_of_gate.get(g1))
        defined.add(center_of_gate.get(g2))
    defined.discard(None)

    if not defined:
        return "無定義"

    # BFS 計算連通分量
    visited = set()
    components = 0
    for start in defined:
        if start in visited:
            continue
        components += 1
        queue = [start]
        visited.add(start)
        while queue:
            cur = queue.pop()
            for nxt in adj[cur]:
                if nxt in defined and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

    defs = {1: "一分人", 2: "二分人", 3: "三分人", 4: "四分人"}
    return defs.get(components, f"{components}分人")


# 向後兼容：保留舊接口
def calculate(planets_longitudes):
    """舊接口（僅 Personality 層，7 個行星）— 向後兼容"""
    defined_gates = set()
    gate_details = {}

    for name, lon in planets_longitudes.items():
        g, l = lon_to_gate_line(lon)
        defined_gates.add(g)
        gate_details[name] = {'gate': g, 'line': l}

    earth_lon = (planets_longitudes.get('太陽', 0) + 180) % 360
    earth_g, earth_l = lon_to_gate_line(earth_lon)
    defined_gates.add(earth_g)
    gate_details['地球'] = {'gate': earth_g, 'line': earth_l}

    active_channels = []
    for g1, g2 in CHANNELS:
        if g1 in defined_gates and g2 in defined_gates:
            active_channels.append((g1, g2))

    connected_gates = set()
    for g1, g2 in active_channels:
        connected_gates.add(g1)
        connected_gates.add(g2)

    defined_centers = set()
    for center_name, gates in CENTERS.items():
        if any(g in connected_gates for g in gates):
            defined_centers.add(center_name)

    has_sacral = '薦骨' in defined_centers
    has_throat = '喉嚨' in defined_centers
    has_motor = bool(defined_centers & {'情緒', '心輪', '根部'})

    if has_sacral:
        if has_motor:
            energy_type = "顯示生產者"
        else:
            energy_type = "生產者"
    elif has_throat and has_motor:
        energy_type = "顯示者"
    elif len(defined_centers) == 0:
        energy_type = "反映者"
    else:
        energy_type = "投射者"

    profile = f"{gate_details['太陽']['line']}/{gate_details['地球']['line']}"

    if '情緒' in defined_centers:
        authority = "情緒權威"
    elif '薦骨' in defined_centers:
        authority = "薦骨權威"
    elif '脾/直覺' in defined_centers:
        authority = "直覺權威"
    elif '心輪' in defined_centers:
        authority = "意志力權威"
    elif 'G中心' in defined_centers:
        authority = "自我投射權威"
    elif len(defined_centers) == 0:
        authority = "月亮週期權威"
    else:
        authority = "無內在權威"

    if energy_type == "生產者":
        strategy = "等待回應"
    elif energy_type == "顯示生產者":
        strategy = "等待回應，再行動"
    elif energy_type == "顯示者":
        strategy = "告知後行動"
    elif energy_type == "投射者":
        strategy = "等待邀請"
    else:
        strategy = "等待 28 天月亮週期"

    return {
        'energy_type': energy_type,
        'profile': profile,
        'authority': authority,
        'strategy': strategy,
        'defined_gates': sorted(defined_gates),
        'active_channels': active_channels,
        'defined_centers': sorted(defined_centers),
        'gate_details': gate_details
    }
