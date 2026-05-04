"""人類圖 (Human Design) 計算模組"""

# 64閘門對應黃道度數（簡化均勻分布，Gate 41從0°開始）
# 真實人類圖曼陀羅排列複雜，此處用概念近似版
GATES = list(range(1, 65))  # 1-64

def lon_to_gate_line(longitude):
    """黃經轉閘門+爻"""
    gate_idx = int(longitude // 5.625) % 64
    gate = gate_idx + 1
    line = int((longitude % 5.625) // 0.9375) + 1
    if line > 6:
        line = 6
    return gate, line

# 9個中心對應的閘門
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
    (1,8), (2,14), (3,60), (4,63), (5,15), (6,59),
    (7,31), (9,52), (10,20), (10,34), (10,57), (11,56),
    (12,22), (13,33), (16,48), (17,62), (18,58), (19,49),
    (20,34), (20,57), (21,45), (23,43), (24,61), (25,51),
    (26,44), (27,50), (28,38), (29,46), (30,41), (32,54),
    (34,57), (35,36), (37,40), (39,55), (42,53), (47,64)
]

def calculate(planets_longitudes):
    """計算人類圖"""
    # 所有被定義的閘門
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
    
    # 計算通道連接
    active_channels = []
    for g1, g2 in CHANNELS:
        if g1 in defined_gates and g2 in defined_gates:
            active_channels.append((g1, g2))
    
    # 中心定義
    defined_centers = set()
    for center_name, gates in CENTERS.items():
        # 如果中心內有任意兩個閘門被通道連接，或閘門在通道中
        center_gates_in_channels = set()
        for g1, g2 in active_channels:
            if g1 in gates:
                center_gates_in_channels.add(g1)
            if g2 in gates:
                center_gates_in_channels.add(g2)
        # 簡化：如果中心有任何閘門被定義，視為有能量
        if any(g in defined_gates for g in gates):
            defined_centers.add(center_name)
    
    # 能量類型
    has_sacral = bool(defined_centers & {'薦骨'})
    has_throat = bool(defined_centers & {'喉嚨'})
    has_motor = bool(defined_centers & {'情緒','意志力','根','薦骨'})
    
    if has_sacral:
        energy_type = "顯示生產者" if (has_throat and has_motor) else "生產者"
    elif has_throat and has_motor:
        energy_type = "顯示者"
    elif len(defined_centers) == 0:
        energy_type = "反映者"
    else:
        energy_type = "投射者"
    
    # 人生角色
    sun_gate, sun_line = lon_to_gate_line(planets_longitudes.get('太陽', 0))
    earth_gate, earth_line = lon_to_gate_line(earth_lon)
    profile = f"{sun_line}/{earth_line}"
    
    # 內在權威
    if '情緒' in defined_centers:
        authority = "情緒權威"
    elif '薦骨' in defined_centers:
        authority = "薦骨權威"
    elif '脾/直覺' in defined_centers:
        authority = "直覺權威"
    elif '意志力' in defined_centers:
        authority = "意志力權威"
    elif 'G中心' in defined_centers:
        authority = "自我投射權威"
    elif '喉嚨' in defined_centers and len(defined_centers) == 1:
        authority = "自我表達權威"
    else:
        authority = "月亮週期權威（反映者）"
    
    return {
        'energy_type': energy_type,
        'profile': profile,
        'authority': authority,
        'defined_gates': sorted(defined_gates),
        'active_channels': active_channels,
        'defined_centers': sorted(defined_centers),
        'gate_details': gate_details
    }
