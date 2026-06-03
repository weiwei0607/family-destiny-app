"""五系統合盤評分引擎 v3

每個維度返回 (score: float 1-5, note: str)
綜合分數 = 加權平均（八字 25% + 占星 20% + 紫微 20% + 人類圖 20% + 星宿 15%）
"""

# ── 八字常數 ──
WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
}
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE    = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

# 天干六合（甲己合土、乙庚合金、丙辛合水、丁壬合木、戊癸合火）
GAN_LIUHE = {
    '甲': '己', '己': '甲',
    '乙': '庚', '庚': '乙',
    '丙': '辛', '辛': '丙',
    '丁': '壬', '壬': '丁',
    '戊': '癸', '癸': '戊',
}

ZHI_LIUHE = {
    '子': '丑', '丑': '子', '寅': '亥', '亥': '寅',
    '卯': '戌', '戌': '卯', '辰': '酉', '酉': '辰',
    '巳': '申', '申': '巳', '午': '未', '未': '午',
}
ZHI_LIUCHONG = {
    '子': '午', '午': '子', '丑': '未', '未': '丑',
    '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
    '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳',
}
SANHE_GROUPS = [
    {'申', '子', '辰'},  # 水局
    {'亥', '卯', '未'},  # 木局
    {'寅', '午', '戌'},  # 火局
    {'巳', '酉', '丑'},  # 金局
]
# 三刑（無恩之刑 + 無禮之刑）
ZHI_XING = {
    ('寅', '巳'): True, ('巳', '申'): True, ('申', '寅'): True,
    ('丑', '戌'): True, ('戌', '未'): True, ('未', '丑'): True,
    ('子', '卯'): True, ('卯', '子'): True,
}


BRANCH_WX = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
    '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水',
}


def _bz_zhis(bz):
    """從 bazi dict 提取 [年支, 月支, 日支, 時支]（原始，保留重複）"""
    return [bz.get(k, '')[-1] for k in ('year', 'month', 'day', 'hour') if bz.get(k)]


def _bz_wuxing_count(bz):
    """統計八字中各五行出現次數（天干+地支共8個字）"""
    count = {}
    for k in ('year', 'month', 'day', 'hour'):
        v = bz.get(k, '')
        if v:
            wx_g = WUXING.get(v[0], '')
            wx_z = BRANCH_WX.get(v[-1], '')
            if wx_g: count[wx_g] = count.get(wx_g, 0) + 1
            if wx_z: count[wx_z] = count.get(wx_z, 0) + 1
    return count


def _wuxing_complement_bonus(bz1, bz2):
    """
    命缺互補加分：A 命缺某五行，B 該五行出現 ≥2 次 → 天然補缺，+0.25 each
    上限 0.6，回傳 (bonus, [note_str])
    """
    all_wx = {'木', '火', '土', '金', '水'}
    cnt1 = _bz_wuxing_count(bz1)
    cnt2 = _bz_wuxing_count(bz2)
    missing1 = all_wx - set(cnt1)
    missing2 = all_wx - set(cnt2)

    bonus = 0.0
    notes = []
    for wx in missing1:
        if cnt2.get(wx, 0) >= 2:
            bonus += 0.25
            notes.append(f"補A命缺{wx}")
    for wx in missing2:
        if cnt1.get(wx, 0) >= 2:
            bonus += 0.25
            notes.append(f"補B命缺{wx}")

    return min(0.6, bonus), notes


def score_bazi(bz1, bz2):
    """
    八字合盤評分（v3）：
    - 日主五行生克（基礎分）
    - 日主天干六合優先（覆蓋克）
    - 全柱天干互合（加成）
    - 四柱地支合/沖/刑（日支加權 2×）
    - 三合局
    - 命缺五行互補（新）
    """
    dm1 = bz1.get('day_master', '')
    dm2 = bz2.get('day_master', '')
    wx1 = WUXING.get(dm1, '')
    wx2 = WUXING.get(dm2, '')

    # ① 天干六合優先判斷（合 > 克）
    gan_he_bonus = 0.0
    if GAN_LIUHE.get(dm1) == dm2:
        dm_score, dm_note = 4.3, f"{dm1}{dm2}天干合·命中注定的吸引"
    else:
        if SHENG.get(wx1) == wx2:
            dm_score, dm_note = 4.2, f"{wx1}生{wx2}·滋養型"
        elif SHENG.get(wx2) == wx1:
            dm_score, dm_note = 4.2, f"{wx2}生{wx1}·被滋養型"
        elif KE.get(wx1) == wx2:
            dm_score, dm_note = 2.0, f"{wx1}克{wx2}·制約型（有壓力）"
        elif KE.get(wx2) == wx1:
            dm_score, dm_note = 2.0, f"{wx2}克{wx1}·被制約（承壓）"
        else:
            dm_score, dm_note = 3.0, f"{wx1}與{wx2}比劫·平起平坐"

        gans1 = [bz1.get(k, '')[:1] for k in ('year', 'month', 'hour') if bz1.get(k)]
        gans2 = [bz2.get(k, '')[:1] for k in ('year', 'month', 'hour') if bz2.get(k)]
        cross_he = sum(1 for g in gans1 for g2 in gans2 if g and GAN_LIUHE.get(g) == g2)
        gan_he_bonus = min(0.4, cross_he * 0.15)

    # ② 地支互動
    all_z1 = list(set(_bz_zhis(bz1)))
    all_z2 = list(set(_bz_zhis(bz2)))
    day_z1 = bz1.get('day', '')[-1] if bz1.get('day') else ''
    day_z2 = bz2.get('day', '')[-1] if bz2.get('day') else ''

    he_count    = sum(1 for a in all_z1 for b in all_z2 if ZHI_LIUHE.get(a) == b)
    chong_count = sum(1 for a in all_z1 for b in all_z2 if ZHI_LIUCHONG.get(a) == b)
    xing_count  = sum(1 for a in all_z1 for b in all_z2 if ZHI_XING.get((a, b)))

    all_z = set(all_z1) | set(all_z2)
    sanhe_count = sum(1 for g in SANHE_GROUPS if len(g & all_z) >= 3)

    day_zhi_bonus  = 0.45 if ZHI_LIUHE.get(day_z1) == day_z2 else 0.0
    day_zhi_bonus -= 0.45 if ZHI_LIUCHONG.get(day_z1) == day_z2 else 0.0

    zhi_bonus = (
        min(he_count, 3) * 0.2
        + min(sanhe_count, 1) * 0.35
        - min(chong_count, 3) * 0.22
        - min(xing_count, 2) * 0.15
        + day_zhi_bonus
    )

    # ③ 命缺互補
    comp_bonus, comp_notes = _wuxing_complement_bonus(bz1, bz2)

    score = max(1.0, min(5.0, dm_score + gan_he_bonus + zhi_bonus + comp_bonus))

    notes = [dm_note]
    if gan_he_bonus >= 0.9:    notes.append("天干合·命中注定的吸引")
    elif gan_he_bonus > 0:     notes.append(f"天干合×{int(gan_he_bonus/0.15)}")
    if day_zhi_bonus > 0:     notes.append("日支六合（感情最深）")
    elif day_zhi_bonus < 0:   notes.append("日支六衝（情感衝突多）")
    if he_count:               notes.append(f"地支六合×{he_count}")
    if sanhe_count:            notes.append(f"三合成局×{sanhe_count}")
    if chong_count:            notes.append(f"六衝×{chong_count}")
    if xing_count:             notes.append(f"三刑×{xing_count}（需化解）")
    if comp_notes:             notes.append('五行互補：' + '·'.join(comp_notes))

    return round(score, 1), ' · '.join(notes)


# ── 占星相位 ──
ASPECTS = [
    ('合相',   0,   8, +0.8),
    ('三分相', 120,  7, +0.65),
    ('六分相',  60,  6, +0.35),
    ('對分相', 180,  8, -0.25),
    ('四分相',  90,  7, -0.45),
]
KEY_PAIRS = [
    ('太陽', '月亮'), ('月亮', '太陽'),    # Sun-Moon cross (最重要)
    ('太陽', '太陽'),                       # 雙太陽
    ('月亮', '月亮'),                       # 雙月亮
    ('金星', '火星'), ('火星', '金星'),     # 愛情軸
    ('太陽', '金星'), ('金星', '太陽'),
    ('月亮', '金星'),
    ('太陽', '上升點'), ('上升點', '太陽'), # ASC 軸（第一印象/吸引力）
    ('月亮', '上升點'), ('上升點', '月亮'), # ASC × 月亮（情感共鳴）
]


def _angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def score_astro(ast1, ast2):
    """
    占星合盤：跨盤關鍵行星相位分析

    baseline 2.5（中性），delta×0.5 讓分佈涵蓋完整 1.0~5.0 範圍。
    KEY_PAIRS 包含 ASC 軸，故需傳入含 longitude 的完整占星資料。
    """
    score = 2.5
    found_notes = []

    for p1_name, p2_name in KEY_PAIRS:
        lon1 = ast1.get(p1_name, {}).get('longitude')
        lon2 = ast2.get(p2_name, {}).get('longitude')
        if lon1 is None or lon2 is None:
            continue
        diff = _angle_diff(lon1, lon2)
        for asp_name, target, orb, delta in ASPECTS:
            if abs(diff - target) <= orb:
                s1 = ast1[p1_name].get('sign', '')
                s2 = ast2[p2_name].get('sign', '')
                found_notes.append(f"{p1_name}({s1}) {asp_name} {p2_name}({s2})")
                score += delta * 0.5
                break

    score = max(1.0, min(5.0, score))
    if not found_notes:
        sun1 = ast1.get('太陽', {}).get('sign', '')
        sun2 = ast2.get('太陽', {}).get('sign', '')
        found_notes = [f"太陽{sun1}×{sun2}·無強烈相位，各自精彩"]

    return round(score, 1), ' · '.join(found_notes[:3])


# ── 人類圖電磁吸引 + Profile 親和性 ──
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59),
    (7, 31), (9, 52), (10, 20), (10, 34), (10, 57), (11, 56),
    (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49),
    (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (25, 51),
    (26, 44), (27, 50), (28, 38), (29, 46), (30, 41), (32, 54),
    (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64),
]

# 六爻親和對：1-4、2-5、3-6 互補；相鄰爻 1-2 等較中性
HARMONIC_LINES = {(1, 4), (4, 1), (2, 5), (5, 2), (3, 6), (6, 3)}
SAME_LINES     = {(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)}

# 重要通道主題描述（電磁吸引時顯示）
CHANNEL_THEMES = {
    (1,  8): '創意表達（G中心→喉嚨）：對方能讓你的獨特天賦被看見',
    (2, 14): '生命方向（G中心→薦骨）：引導彼此活出真實使命',
    (5, 15): '韻律節奏（薦骨→G中心）：輕鬆引領對方建立穩定習慣',
    (12,22): '開放溝通（喉嚨→情緒）：情緒真實流動，直接而深刻',
    (13,33): '先知通道（G中心→喉嚨）：分享人生故事，彼此解密',
    (20,34): '混沌通道（喉嚨→薦骨）：強烈行動力，一碰就啟動',
    (29,46): '發現通道（薦骨→G中心）：共同投入後產生深刻意義',
    (35,36): '變遷通道（喉嚨→情緒）：渴望共同體驗新的情緒',
    (37,40): '社群通道（情緒→心輪）：家人般的義氣與守護',
    (6,  59): '親密通道（情緒→薦骨）：極強的情感與肢體吸引力',
    (32,54): '轉化通道（脾→根部）：推動彼此野心實現',
    (39,55): '情緒波（根部→情緒）：豐盛感的共振與流動',
    (25,51): '啟蒙通道（G中心→心輪）：一眼觸動靈魂的電流',
}


def _profile_affinity(p1, p2):
    """Profile 爻號親和加分"""
    try:
        l1 = [int(x) for x in p1.split('/')]
        l2 = [int(x) for x in p2.split('/')]
    except (ValueError, AttributeError):
        return 0.0
    bonus = 0.0
    for a in l1:
        for b in l2:
            if (a, b) in HARMONIC_LINES: bonus += 0.25
            elif (a, b) in SAME_LINES:   bonus += 0.12
    return min(0.8, bonus)


# 重要中心的 conditioning 動態描述
CENTER_DYNAMICS = {
    '情緒':    ('情緒波共振', '情緒波 conditioning（易被對方情緒牽動）'),
    '薦骨':    ('生命力加倍', '薦骨能量補充（帶來活力）'),
    '心輪':    ('意志力共振', '心輪 conditioning（易被對方意志左右）'),
    'G中心':   ('認同感共鳴', 'G中心 conditioning（認同感受影響）'),
    '喉嚨':    ('表達力加倍', '喉嚨 conditioning（說話方式受影響）'),
    '脾/直覺': ('直覺共振',   '直覺 conditioning（安全感受影響）'),
}


def score_hd(hd1, hd2):
    """人類圖合盤：電磁吸引 + Profile 親和性 + 中心相容性"""
    g1 = set(hd1.get('defined_gates', []))
    g2 = set(hd2.get('defined_gates', []))

    electromagnetic = []
    companionship   = []

    for ch_a, ch_b in CHANNELS:
        a1, b1 = ch_a in g1, ch_b in g1
        a2, b2 = ch_a in g2, ch_b in g2
        if (a1 and b2 and not b1 and not a2) or (b1 and a2 and not a1 and not b2):
            electromagnetic.append((ch_a, ch_b))
        elif a1 and b1 and a2 and b2:
            companionship.append((ch_a, ch_b))

    em  = len(electromagnetic)
    com = len(companionship)

    prof1 = hd1.get('profile', '')
    prof2 = hd2.get('profile', '')
    prof_bonus = _profile_affinity(prof1, prof2)

    # ── 中心層級相容性 ──
    dc1 = set(hd1.get('defined_centers', []))
    dc2 = set(hd2.get('defined_centers', []))

    both_defined    = dc1 & dc2                    # 雙方同時定義 → 共振
    a_conditions_b  = dc1 - dc2                    # A 定義、B 未定義 → B 受 A conditioning
    b_conditions_a  = dc2 - dc1                    # B 定義、A 未定義 → A 受 B conditioning

    center_bonus = 0.0
    center_notes = []

    for c in both_defined:
        if c in CENTER_DYNAMICS:
            label, _ = CENTER_DYNAMICS[c]
            center_notes.append(f"{c}雙定義·{label}")
            center_bonus += 0.1   # 共振但可能競爭，小加分

    # 情緒中心 conditioning 是最顯著的動態
    if '情緒' in a_conditions_b:
        center_notes.append("A情緒→B：情緒 conditioning（B易被A波動牽動）")
        center_bonus -= 0.1   # 有挑戰性
    elif '情緒' in b_conditions_a:
        center_notes.append("B情緒→A：情緒 conditioning（A易被B波動牽動）")
        center_bonus -= 0.1

    # 薦骨互補（一有一無）是理想配對
    if ('薦骨' in a_conditions_b) or ('薦骨' in b_conditions_a):
        center_notes.append("薦骨能量互補（一方帶來動力泉源）")
        center_bonus += 0.2

    center_bonus = max(-0.4, min(0.4, center_bonus))
    score = min(5.0, 2.5 + em * 0.4 + com * 0.25 + prof_bonus + center_bonus)

    type1  = hd1.get('energy_type', '')
    type2  = hd2.get('energy_type', '')
    auth1  = hd1.get('authority', '')
    auth2  = hd2.get('authority', '')

    em_themes = [CHANNEL_THEMES[ch] for ch in electromagnetic if ch in CHANNEL_THEMES][:2]

    notes = [f"{type1} {prof1} × {type2} {prof2}"]
    if em_themes:
        notes.extend(em_themes)
    elif em:
        notes.append(f"電磁吸引×{em}通道（天然火花）")
    if com:               notes.append(f"心靈共振×{com}通道")
    if prof_bonus > 0.4:  notes.append(f"Profile {prof1}×{prof2} 高度親和")
    elif prof_bonus > 0:  notes.append(f"Profile {prof1}×{prof2} 部分親和")
    if center_notes:      notes.extend(center_notes[:2])
    if not em and not com: notes.append("無強烈通道連結（獨立個體，互相學習）")
    notes.append(f"決策：{auth1}×{auth2}")

    return round(score, 1), ' · '.join(notes)


# ── 紫微夫妻宮（修正版）──
ZW_P = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
# 12 宮順序（從命宮逆時針）: 命(-0)兄(-1)夫(-2)子(-3)財(-4)疾(-5)遷(-6)奴(-7)官(-8)田(-9)福(-10)父(-11)
GOOD_STARS = {'紫微', '天府', '太陽', '太陰', '天同', '天梁', '天機'}
BAD_STARS  = {'七殺', '破軍', '廉貞', '巨門', '火星', '鈴星', '擎羊', '陀羅'}

# 四化吉凶
HUA_BONUS = {'祿': +0.6, '權': +0.4, '科': +0.3}
HUA_PENALTY = {'忌': -0.5}


def _fuqi_palace_zhi(ming_str):
    """命宮干支字串 → 夫妻宮地支（命宮逆數2位）"""
    if not ming_str or len(ming_str) < 1:
        return ''
    zhi = ming_str[-1]
    if zhi not in ZW_P:
        return ''
    idx = ZW_P.index(zhi)
    return ZW_P[(idx - 2) % 12]   # 逆數2位 = 夫妻宮


def _fuqi_sihua_bonus(zw, fuqi_zhi):
    """計算四化落入夫妻宮的吉凶加分"""
    sihua = zw.get('四化', {})
    stars = zw.get('主星', {})
    bonus = 0.0
    for hua, star_name in sihua.items():
        star_palace = stars.get(star_name, '')
        if star_palace == fuqi_zhi:
            bonus += HUA_BONUS.get(hua, 0) + HUA_PENALTY.get(hua, 0)
    return bonus


def score_ziwei(zw1, zw2):
    """
    紫微合盤（v2）：
    - 夫妻宮主星吉凶（修正為 命宮逆數2位）
    - 四化落入對方夫妻宮
    - 命宮地支六合/六衝
    """
    ming1 = zw1.get('命宮', '')
    ming2 = zw2.get('命宮', '')
    fuqi1 = _fuqi_palace_zhi(ming1)
    fuqi2 = _fuqi_palace_zhi(ming2)

    stars1 = zw1.get('主星', {})
    stars2 = zw2.get('主星', {})

    # 夫妻宮主星評分
    good, bad = 0, 0
    for star, palace in stars1.items():
        if palace == fuqi1:
            if star in GOOD_STARS: good += 1
            if star in BAD_STARS:  bad  += 1
    for star, palace in stars2.items():
        if palace == fuqi2:
            if star in GOOD_STARS: good += 1
            if star in BAD_STARS:  bad  += 1

    # 四化入夫妻宮
    sihua_b = _fuqi_sihua_bonus(zw1, fuqi1) + _fuqi_sihua_bonus(zw2, fuqi2)

    # 命宮地支六合/六衝
    mz1 = ming1[-1] if ming1 else ''
    mz2 = ming2[-1] if ming2 else ''
    ming_bonus = 0.5 if ZHI_LIUHE.get(mz1) == mz2 else (-0.4 if ZHI_LIUCHONG.get(mz1) == mz2 else 0)

    score = max(1.0, min(5.0, 3.0 + good * 0.35 - bad * 0.45 + sihua_b + ming_bonus))

    notes = [f"{ming1}命×{ming2}命"]
    if fuqi1: notes.append(f"夫妻宮 {fuqi1}/{fuqi2}")
    if good:  notes.append(f"吉星入夫妻×{good}")
    if bad:   notes.append(f"煞星入夫妻×{bad}（需化解）")
    if sihua_b > 0:  notes.append("四化祿/權入夫妻（感情有助力）")
    elif sihua_b < 0: notes.append("四化忌入夫妻（感情有阻礙）")

    return round(score, 1), ' · '.join(notes)


# ── 星宿合盤評分 ──
XINGXIU_SCORES = {
    '命之星': 3.5,   # 同宿，鏡像共鳴
    '榮親':   4.5,   # 如親如家
    '友衰':   3.5,   # 朋友般輕鬆
    '業胎':   2.5,   # 因果糾纏
    '安壞':   2.0,   # 權力不對等
    '危成':   4.0,   # 危中求成，激勵成長
    '寶義':   4.2,   # 共同價值，義氣相投
}


def score_xingxiu(xx1, xx2, relation):
    """
    星宿合盤評分
    xx1, xx2: 宿名（如 '井', '角'）
    relation: 星宿關係字串（如 '榮親', '業胎'）
    """
    sc = XINGXIU_SCORES.get(relation, 3.0)
    note = f"{xx1}宿×{xx2}宿·{relation}"
    return sc, note


# ── 綜合評分 ──
WEIGHTS = {'bazi': 0.25, 'astro': 0.20, 'ziwei': 0.20, 'hd': 0.20, 'xingxiu': 0.15}


def overall_score(scores_dict):
    """加權綜合分數 (1-5)"""
    total = sum(scores_dict[k] * WEIGHTS[k] for k in WEIGHTS if k in scores_dict)
    return round(total, 1)


# ══════════════════════════════════════════════════════════════════
# 延伸合盤模組（Bonus Insights）
# ══════════════════════════════════════════════════════════════════

# ── 桃花星 / 紅鸞天喜 ──
_ZHI_LIST = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 三合局沐浴位 = 桃花位：申子辰→酉，寅午戌→卯，巳酉丑→午，亥卯未→子
TAOHUA_MAP = {
    '子': '酉', '丑': '午', '寅': '卯', '卯': '子',
    '辰': '酉', '巳': '午', '午': '卯', '未': '子',
    '申': '酉', '酉': '午', '戌': '卯', '亥': '子',
}


def _hongluan(year_zhi):
    """出生年支 → 本命紅鸞位（子年在卯，每年逆退一位）"""
    base = 3   # 卯的 index（子年對應卯）
    idx = _ZHI_LIST.index(year_zhi)
    return _ZHI_LIST[(base - idx) % 12]


def _tianxi(year_zhi):
    """天喜 = 紅鸞對宮（+6位）"""
    hl = _hongluan(year_zhi)
    return _ZHI_LIST[(_ZHI_LIST.index(hl) + 6) % 12]


def score_taohua(bz1, bz2):
    """
    桃花星合盤評分：
    - 桃花互照：A的桃花位 == B的年/日支（反之亦然）
    - 紅鸞天喜活化：A的紅鸞/天喜 == B的年/日支（婚緣信號）
    - 雙方桃花位六合加成
    """
    y1 = bz1.get('year', '')
    y2 = bz2.get('year', '')
    d1 = bz1.get('day', '')
    d2 = bz2.get('day', '')

    yz1 = y1[-1] if y1 else ''
    yz2 = y2[-1] if y2 else ''
    dz1 = d1[-1] if d1 else ''
    dz2 = d2[-1] if d2 else ''

    b_zhis2 = {z for z in (yz2, dz2) if z}
    b_zhis1 = {z for z in (yz1, dz1) if z}

    score = 3.0
    notes = []

    # ① 桃花互照
    th1 = TAOHUA_MAP.get(yz1) or TAOHUA_MAP.get(dz1, '')
    th2 = TAOHUA_MAP.get(yz2) or TAOHUA_MAP.get(dz2, '')

    if th1 and th1 in b_zhis2:
        score += 0.6
        notes.append(f"A桃花({th1})照B命支·天生吸引力")
    if th2 and th2 in b_zhis1:
        score += 0.6
        notes.append(f"B桃花({th2})照A命支·互相燃動")

    # ② 紅鸞天喜活化
    if yz1:
        hl1 = _hongluan(yz1)
        tx1 = _tianxi(yz1)
        if hl1 in b_zhis2:
            score += 0.5
            notes.append(f"A紅鸞({hl1})被B點亮·婚緣信號強")
        if tx1 in b_zhis2:
            score += 0.4
            notes.append(f"A天喜({tx1})被B點亮·喜慶緣份")

    if yz2:
        hl2 = _hongluan(yz2)
        tx2 = _tianxi(yz2)
        if hl2 in b_zhis1:
            score += 0.5
            notes.append(f"B紅鸞({hl2})被A點亮·婚緣信號強")
        if tx2 in b_zhis1:
            score += 0.4
            notes.append(f"B天喜({tx2})被A點亮·喜慶緣份")

    # ③ 雙桃花位六合
    if th1 and th2 and ZHI_LIUHE.get(th1) == th2:
        score += 0.3
        notes.append(f"雙桃花合（{th1}×{th2}）·情愫自然流動")

    score = max(1.0, min(5.0, score))
    if not notes:
        notes = ["桃花緣份平穩，緣分始於日常累積"]

    return round(score, 1), ' · '.join(notes)


# ── 占星宮位疊加（整宮制 Equal House）──
# 感情宮位加分表（以 B 的宮位為基準）
HOUSE_LOVE_SCORE = {
    7: +0.55,   # 伴侶宮（最重要）
    5: +0.50,   # 愛情/創意宮
    1: +0.25,   # 身份認同宮
    4: +0.35,   # 家庭/安全感宮
    8: +0.15,   # 深層轉化（強烈但複雜）
    11: +0.10,  # 友誼/共同夢想
    12: -0.20,  # 隱秘/幻象（需留意）
    6: -0.10,   # 義務服務（易成習慣而非愛情）
}

HOUSE_NAMES = {
    1: '第1宮（身份）', 2: '第2宮（資源）', 3: '第3宮（溝通）',
    4: '第4宮（家庭）', 5: '第5宮（愛情）', 6: '第6宮（服務）',
    7: '第7宮（伴侶）', 8: '第8宮（轉化）', 9: '第9宮（哲學）',
    10: '第10宮（事業）', 11: '第11宮（友誼）', 12: '第12宮（隱秘）',
}

_KEY_PLANETS_OVERLAY = ['太陽', '月亮', '金星', '火星', '上升點']


def _which_house(planet_lon, asc_lon):
    """整宮制：行星落在對方的第幾宮（1-12）"""
    asc_sign_idx = int(asc_lon // 30) % 12
    planet_sign_idx = int(planet_lon // 30) % 12
    return (planet_sign_idx - asc_sign_idx) % 12 + 1


def score_house_overlay(ast1, ast2):
    """
    占星宮位疊加評分（整宮制）：
    A 的關鍵行星落入 B 的哪個宮位（反之亦然），
    以各自 ASC 黃道度數確定第 1 宮起始。
    """
    asc1 = ast1.get('上升點', {}).get('longitude')
    asc2 = ast2.get('上升點', {}).get('longitude')

    if asc1 is None or asc2 is None:
        return 3.0, 'ASC 資料不足，宮位疊加略過'

    score = 2.5
    notes = []

    # A 的行星 → 落入 B 的宮位
    for planet in _KEY_PLANETS_OVERLAY:
        lon = ast1.get(planet, {}).get('longitude')
        if lon is None:
            continue
        house = _which_house(lon, asc2)
        bonus = HOUSE_LOVE_SCORE.get(house, 0)
        if bonus != 0:
            sign = ast1[planet].get('sign', '')
            label = '✨' if bonus > 0 else '⚠️'
            notes.append(f"{label}A{planet}({sign})→B{HOUSE_NAMES[house]}")
            score += bonus

    # B 的行星 → 落入 A 的宮位
    for planet in _KEY_PLANETS_OVERLAY:
        lon = ast2.get(planet, {}).get('longitude')
        if lon is None:
            continue
        house = _which_house(lon, asc1)
        bonus = HOUSE_LOVE_SCORE.get(house, 0)
        if bonus != 0:
            sign = ast2[planet].get('sign', '')
            label = '✨' if bonus > 0 else '⚠️'
            notes.append(f"{label}B{planet}({sign})→A{HOUSE_NAMES[house]}")
            score += bonus

    score = max(1.0, min(5.0, score))
    if not notes:
        notes = ['宮位疊加平衡，彼此保有空間']

    return round(score, 1), ' · '.join(notes[:5])


# ── Composite 複合盤（西洋占星）──
_SIGNS_LIST = ['牡羊', '金牛', '雙子', '巨蟹', '獅子', '處女',
               '天秤', '天蠍', '射手', '摩羯', '水瓶', '雙魚']


def _midpoint_lon(lon1, lon2):
    """黃道中點（取較短弧）"""
    diff = (lon2 - lon1) % 360
    if diff > 180:
        return (lon1 + lon2 + 360) / 2 % 360
    return (lon1 + lon2) / 2 % 360


def score_composite(ast1, ast2):
    """
    Composite 複合盤分析：
    - 計算兩人行星黃道中點，生成「關係本身」的盤
    - 分析複合 Sun-Moon 相位（和諧度）
    - 分析複合 Venus-Mars 相位（吸引力）
    - 複合金星星座（尊弱位）加成
    """
    _planets = ['太陽', '月亮', '金星', '火星', '木星']
    composite = {}
    for p in _planets:
        l1 = ast1.get(p, {}).get('longitude')
        l2 = ast2.get(p, {}).get('longitude')
        if l1 is not None and l2 is not None:
            mid = _midpoint_lon(l1, l2)
            composite[p] = {'longitude': mid, 'sign': _SIGNS_LIST[int(mid // 30) % 12]}

    if not composite:
        return 3.0, '複合盤資料不足'

    score = 2.5
    notes = []

    c_sun   = composite.get('太陽', {})
    c_moon  = composite.get('月亮', {})
    c_venus = composite.get('金星', {})
    c_mars  = composite.get('火星', {})
    c_jup   = composite.get('木星', {})

    if c_sun.get('sign'):
        notes.append(f"複合太陽{c_sun['sign']}")
    if c_moon.get('sign'):
        notes.append(f"複合月亮{c_moon['sign']}")

    # 複合 Sun-Moon 相位
    if c_sun.get('longitude') is not None and c_moon.get('longitude') is not None:
        diff = _angle_diff(c_sun['longitude'], c_moon['longitude'])
        if diff <= 10:
            score += 0.8
            notes.append("複合日月合相·靈魂高度共鳴")
        elif abs(diff - 120) <= 8:
            score += 0.5
            notes.append("複合日月三分·輕鬆和諧")
        elif abs(diff - 60) <= 6:
            score += 0.3
            notes.append("複合日月六分·互補成長")
        elif abs(diff - 180) <= 8:
            score -= 0.2
            notes.append("複合日月對分·吸引又牽制")
        elif abs(diff - 90) <= 7:
            score -= 0.3
            notes.append("複合日月四分·關係中有張力需化解")

    # 複合 Venus-Mars 相位（吸引力核心）
    if c_venus.get('longitude') is not None and c_mars.get('longitude') is not None:
        diff = _angle_diff(c_venus['longitude'], c_mars['longitude'])
        if diff <= 10:
            score += 1.0
            notes.append(f"複合金火合相({c_venus.get('sign', '')})·磁場極強")
        elif abs(diff - 120) <= 8:
            score += 0.6
            notes.append("複合金火三分·自然流動的吸引力")
        elif abs(diff - 60) <= 6:
            score += 0.35
            notes.append("複合金火六分·浪漫舒適")
        elif abs(diff - 180) <= 8:
            score += 0.2
            notes.append("複合金火對分·張力製造吸引力")
        elif abs(diff - 90) <= 7:
            score -= 0.15
            notes.append("複合金火四分·吸引中帶摩擦")

    # 複合金星尊位加成
    if c_venus.get('sign') in ('天秤', '金牛'):
        score += 0.3
        notes.append(f"複合金星{c_venus['sign']}（尊位）·愛情能量加倍")
    elif c_venus.get('sign') in ('牡羊', '天蠍'):
        score -= 0.1
        notes.append(f"複合金星{c_venus['sign']}（陷位）·需要更多努力維繫溫柔")

    # 複合木星（祝福能量）
    if c_jup.get('sign') in ('射手', '雙魚', '巨蟹'):
        score += 0.2
        notes.append(f"複合木星{c_jup['sign']}·祝福與擴展潛能")

    score = max(1.0, min(5.0, score))
    return round(score, 1), ' · '.join(notes[:5])


# ── 合盤流年：雙方大運五行交叉影響 ──
_DY_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
_DY_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
_DY_KE    = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}


def score_synastry_year(dayun1, dayun2):
    """
    合盤流年分析：雙方當前大運天干五行的交互關係。
    回傳 (delta: float | None, note: str)
    delta 是在總分上的浮動值（-0.5 ~ +0.5），None 代表資料不足。
    """
    cur1 = (dayun1 or {}).get('current') or {}
    cur2 = (dayun2 or {}).get('current') or {}
    p1 = cur1.get('pillar', '')
    p2 = cur2.get('pillar', '')

    if not p1 or not p2:
        return None, '大運資料不足，合盤流年略過'

    wx1 = _DY_WX.get(p1[0], '')
    wx2 = _DY_WX.get(p2[0], '')
    age1 = cur1.get('age_range', '')
    age2 = cur2.get('age_range', '')

    header = f"A走{p1}大運（{wx1}，{age1}）× B走{p2}大運（{wx2}，{age2}）"
    delta = 0.0
    desc = ''

    if not wx1 or not wx2:
        return None, header + '·五行未知'

    if wx1 == wx2:
        delta = +0.2
        desc = '雙方大運同氣·步調接近，容易形成默契'
    elif _DY_SHENG.get(wx1) == wx2:
        delta = +0.4
        desc = f'A大運{wx1}滋養B大運{wx2}·此階段A是B的強力後盾'
    elif _DY_SHENG.get(wx2) == wx1:
        delta = +0.4
        desc = f'B大運{wx2}滋養A大運{wx1}·此階段B是A的貴人'
    elif _DY_KE.get(wx1) == wx2:
        delta = -0.3
        desc = f'A大運{wx1}克B大運{wx2}·A可能在此階段帶給B無形壓力，需留意溝通方式'
    elif _DY_KE.get(wx2) == wx1:
        delta = -0.3
        desc = f'B大運{wx2}克A大運{wx1}·B可能帶給A壓力，建議多給對方空間'

    return delta, f"{header}·{desc}" if desc else header
