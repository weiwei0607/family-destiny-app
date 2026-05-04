"""人類圖 (Human Design) 計算模組 — 真實 Rave Mandala"""

# Rave Mandala 閘門順序（從 0° Aries 開始，逆時針排列）
# 每個閘門 5.625°，每條爻 (line) 0.9375°
RAVE_MANDALA = [
    41, 19, 13, 49, 30, 55, 37, 63,   # 0° - 45°
    22, 36, 25, 17, 21, 51, 42, 3,    # 45° - 90°
    27, 24, 2, 23, 8, 20, 16, 35,     # 90° - 135°
    45, 12, 15, 52, 39, 53, 62, 56,   # 135° - 180°
    31, 33, 7, 4, 29, 59, 40, 64,     # 180° - 225°
    47, 6, 46, 18, 48, 57, 32, 50,    # 225° - 270°
    28, 44, 1, 43, 14, 34, 9, 5,      # 270° - 315°
    26, 11, 10, 58, 38, 54, 61, 60,   # 315° - 360°
]

GATE_DEGREE = 5.625
LINE_DEGREE = 0.9375

# 九個中心對應的閘門
CENTERS = {
    '頭腦': [61, 63, 64],
    '邏輯': [47, 24, 4, 17, 43, 11],
    '喉嚨': [62, 23, 56, 16, 35, 12, 45, 33, 20, 31, 8, 7],
    'G中心': [1, 13, 25, 46, 10, 15, 7, 2],
    '意志力': [26, 44, 51, 21, 40],
    '情緒': [36, 22, 37, 6, 49, 55, 30],
    '薦骨': [9, 5, 52, 53, 29, 14, 34, 57, 27, 50, 59, 3, 42, 44],
    '脾/直覺': [48, 57, 18, 28, 44, 50, 32],
    '根': [58, 38, 54, 19, 39, 41, 60, 52]
}

# 36條通道（閘門對）
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59),
    (7, 31), (9, 52), (10, 20), (10, 34), (10, 57), (11, 56),
    (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49),
    (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (25, 51),
    (26, 44), (27, 50), (28, 38), (29, 46), (30, 41), (32, 54),
    (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64)
]


def lon_to_gate_line(longitude):
    """黃經轉 Rave Mandala 閘門+爻"""
    normalized = longitude % 360
    gate_idx = int(normalized // GATE_DEGREE) % 64
    gate = RAVE_MANDALA[gate_idx]
    line = int((normalized % GATE_DEGREE) // LINE_DEGREE) + 1
    if line > 6:
        line = 6
    return gate, line


def calculate(planets_longitudes):
    """計算人類圖 BodyGraph"""
    defined_gates = set()
    gate_details = {}

    for name, lon in planets_longitudes.items():
        g, l = lon_to_gate_line(lon)
        defined_gates.add(g)
        gate_details[name] = {'gate': g, 'line': l}

    # 地球（對宮）
    earth_lon = (planets_longitudes.get('太陽', 0) + 180) % 360
    earth_g, earth_l = lon_to_gate_line(earth_lon)
    defined_gates.add(earth_g)
    gate_details['地球'] = {'gate': earth_g, 'line': earth_l}

    # 計算激活通道（兩端閘門都被定義）
    active_channels = []
    for g1, g2 in CHANNELS:
        if g1 in defined_gates and g2 in defined_gates:
            active_channels.append((g1, g2))

    # 中心定義：有完整通道連接的才算定義
    # 先找出所有被通道「連接」的閘門
    connected_gates = set()
    for g1, g2 in active_channels:
        connected_gates.add(g1)
        connected_gates.add(g2)

    defined_centers = set()
    for center_name, gates in CENTERS.items():
        # 中心內有至少一條完整通道才算定義
        center_connected = any(g in connected_gates for g in gates)
        if center_connected:
            defined_centers.add(center_name)

    # 能量類型
    has_sacral = '薦骨' in defined_centers
    has_throat = '喉嚨' in defined_centers
    has_motor = bool(defined_centers & {'情緒', '意志力', '根'})
    # 薦骨也算 motor，但上面已經分開判斷
    motor_to_throat = has_motor and has_throat
    sacral_to_throat = has_sacral and has_throat

    if has_sacral:
        if sacral_to_throat or (has_motor and motor_to_throat):
            energy_type = "顯示生產者"
        else:
            energy_type = "生產者"
    elif has_throat and has_motor:
        energy_type = "顯示者"
    elif len(defined_centers) == 0:
        energy_type = "反映者"
    else:
        energy_type = "投射者"

    # 人生角色 = 太陽爻 / 地球爻
    sun_line = gate_details['太陽']['line']
    earth_line = gate_details['地球']['line']
    profile = f"{sun_line}/{earth_line}"

    # 內在權威
    if '情緒' in defined_centers:
        authority = "情緒權威"
    elif '薦骨' in defined_centers:
        authority = "薦骨權威"
    elif '脾/直覺' in defined_centers:
        authority = "直覺權威"
    elif '意志力' in defined_centers:
        authority = "意志力權威（ ego )"
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
