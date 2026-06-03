"""紫微斗數完整排盤（簡化版但結構正確）"""
ZW_P = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

NAYIN = {
    ('甲', '子'): '金', ('甲', '寅'): '水', ('甲', '辰'): '火', ('甲', '午'): '金', ('甲', '申'): '水', ('甲', '戌'): '火',
    ('乙', '丑'): '金', ('乙', '卯'): '水', ('乙', '巳'): '火', ('乙', '未'): '金', ('乙', '酉'): '水', ('乙', '亥'): '火',
    ('丙', '寅'): '火', ('丙', '辰'): '土', ('丙', '午'): '水', ('丙', '申'): '火', ('丙', '戌'): '土', ('丙', '子'): '水',
    ('丁', '卯'): '火', ('丁', '巳'): '土', ('丁', '未'): '水', ('丁', '酉'): '火', ('丁', '亥'): '土', ('丁', '丑'): '水',
    ('戊', '辰'): '木', ('戊', '午'): '火', ('戊', '申'): '土', ('戊', '戌'): '木', ('戊', '子'): '火', ('戊', '寅'): '土',
    ('己', '巳'): '木', ('己', '未'): '火', ('己', '酉'): '土', ('己', '亥'): '木', ('己', '丑'): '火', ('己', '卯'): '土',
    ('庚', '午'): '土', ('庚', '申'): '木', ('庚', '戌'): '金', ('庚', '子'): '土', ('庚', '寅'): '木', ('庚', '辰'): '金',
    ('辛', '未'): '土', ('辛', '酉'): '木', ('辛', '亥'): '金', ('辛', '丑'): '土', ('辛', '卯'): '木', ('辛', '巳'): '金',
    ('壬', '申'): '金', ('壬', '戌'): '水', ('壬', '子'): '木', ('壬', '寅'): '金', ('壬', '辰'): '水', ('壬', '午'): '木',
    ('癸', '酉'): '金', ('癸', '亥'): '水', ('癸', '丑'): '木', ('癸', '卯'): '金', ('癸', '巳'): '水', ('癸', '未'): '木',
}
JU_NUM = {'水': 2, '木': 3, '金': 4, '土': 5, '火': 6}

# ── 輔助 ──
def get_ming_shen(lunar_month, hour_idx):
    month_zw = (lunar_month - 1) % 12
    ming_zw = (month_zw - hour_idx) % 12
    shen_zw = (month_zw + hour_idx) % 12
    return ZW_P[ming_zw], ZW_P[shen_zw]


def palace_gan(ming_zw_idx, year_gan):
    tg_start = {'甲': '丙', '己': '丙', '乙': '戊', '庚': '戊', '丙': '庚', '辛': '庚', '丁': '壬', '壬': '壬', '戊': '甲', '癸': '甲'}
    start_idx = GAN.index(tg_start[year_gan])
    return GAN[(start_idx + ming_zw_idx) % 10]


# ── 紫微定位 ──
def place_ziwei(day, wuxing):
    """標準算法：生日 ÷ 局數，能整除則紫微在商數位置，否則商+1"""
    jn = JU_NUM[wuxing]
    shang = day // jn
    yu = day % jn
    pos = shang if yu == 0 else shang + 1
    # pos 是從寅(1)起算的宮位數，轉 0-index
    return (pos - 1) % 12


# ── 天府定位（中州派）──
def place_tianfu(ziwei_zw):
    """中州派：紫微 + 天府 ≡ 0 (mod 12)。紫府同宮於寅、申"""
    return (-ziwei_zw) % 12


# ── 年干系星曜 ──
def an_lucun(year_gan):
    """祿存：甲寅乙卯丙巳丁午戊巳己午庚申辛酉壬亥癸子"""
    map_ = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
            '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
    return map_[year_gan]


def an_qingyang_tuoluo(lucun_zw):
    """擎羊在祿存前一位(順)，陀羅在祿存後一位(逆)"""
    lc = ZW_P.index(lucun_zw)
    qingyang = ZW_P[(lc + 1) % 12]
    tuoluo = ZW_P[(lc - 1) % 12]
    return qingyang, tuoluo


def an_tiankui_tianyue(year_gan):
    """天魁/天鉞"""
    map_ = {
        '甲': ('丑', '未'), '乙': ('子', '申'), '丙': ('亥', '酉'),
        '丁': ('亥', '酉'), '戊': ('丑', '未'), '己': ('子', '申'),
        '庚': ('丑', '未'), '辛': ('午', '寅'), '壬': ('卯', '巳'),
        '癸': ('卯', '巳'),
    }
    return map_[year_gan]


# ── 年支系星曜 ──
def an_tianma(year_zhi):
    """天馬：寅午戌→申，申子辰→寅，巳酉丑→亥，亥卯未→巳"""
    group = {
        '寅': '申', '午': '申', '戌': '申',
        '申': '寅', '子': '寅', '辰': '寅',
        '巳': '亥', '酉': '亥', '丑': '亥',
        '亥': '巳', '卯': '巳', '未': '巳',
    }
    return group[year_zhi]


def an_huoxing_lingxing(year_zhi):
    """火星/鈴星（根據年支）"""
    huoxing = {
        '寅': '丑', '午': '丑', '戌': '丑',
        '申': '寅', '子': '寅', '辰': '寅',
        '巳': '卯', '酉': '卯', '丑': '卯',
        '亥': '酉', '卯': '酉', '未': '酉',
    }
    lingxing = {
        '寅': '卯', '午': '卯', '戌': '卯',
        '申': '戌', '子': '戌', '辰': '戌',
        '巳': '戌', '酉': '戌', '丑': '戌',
        '亥': '戌', '卯': '戌', '未': '戌',
    }
    return huoxing[year_zhi], lingxing[year_zhi]


def an_honglian_tianxi(year_zhi):
    """紅鸞/天喜"""
    idx = ZHI.index(year_zhi)
    # 紅鸞：子卯丑寅...（從子年起卯，順數）
    honglian = ZHI[(idx + 3) % 12]  # 子->卯(3), 丑->寅(2)...
    tianxi = ZHI[(idx + 3 + 6) % 12]  # 對宮
    return honglian, tianxi


# ── 時支系星曜 ──
def an_dikong_dijie(hour_idx):
    """地空/地劫：從亥起子時，地空順數，地劫逆數"""
    hai = 10  # 亥在 ZHI 中的索引
    dikong = ZHI[(hai + hour_idx) % 12]
    dijie = ZHI[(hai - hour_idx) % 12]
    return dikong, dijie


# ── 主星排布 ──
def arrange_zhuxing(ziwei_zw, tianfu_zw):
    """安十四主星"""
    stars = {}
    # 紫微系（順行）：紫微、天機、空格、太陽、武曲、天同、空格、廉貞
    zhuxi_offsets = [0, 1, None, 3, 4, 5, None, 7]
    zhuxi_names = ['紫微', '天機', None, '太陽', '武曲', '天同', None, '廉貞']
    for off, name in zip(zhuxi_offsets, zhuxi_names):
        if name:
            stars[name] = ZW_P[(ziwei_zw + off) % 12]

    # 天府系（順行）：天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍
    tianfu_names = ['天府', '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍']
    for i, name in enumerate(tianfu_names):
        stars[name] = ZW_P[(tianfu_zw + i) % 12]
    return stars


# ── 四化 ──
SIHUA = {
    '甲': {'祿': '廉貞', '權': '破軍', '科': '武曲', '忌': '太陽'},
    '乙': {'祿': '天機', '權': '天梁', '科': '紫微', '忌': '太陰'},
    '丙': {'祿': '天同', '權': '天機', '科': '文昌', '忌': '廉貞'},
    '丁': {'祿': '太陰', '權': '天同', '科': '天機', '忌': '巨門'},
    '戊': {'祿': '貪狼', '權': '太陰', '科': '右弼', '忌': '天機'},
    '己': {'祿': '武曲', '權': '貪狼', '科': '天梁', '忌': '文曲'},
    '庚': {'祿': '太陽', '權': '武曲', '科': '太陰', '忌': '天同'},
    '辛': {'祿': '巨門', '權': '太陽', '科': '文曲', '忌': '文昌'},
    '壬': {'祿': '天梁', '權': '紫微', '科': '左輔', '忌': '武曲'},
    '癸': {'祿': '破軍', '權': '巨門', '科': '太陰', '忌': '貪狼'},
}


PALACE_NAMES = [
    '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
    '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮',
]

PALACE_THEMES = {
    '命宮':  '自我認同、人生底色、個性展現',
    '兄弟宮': '手足、同儕、短期合作',
    '夫妻宮': '親密關係、婚姻、對待方式',
    '子女宮': '創意、子嗣、下屬、晚輩',
    '財帛宮': '金錢觀、財運、收入模式',
    '疾厄宮': '身體健康、心理壓力、潛在課題',
    '遷移宮': '出行、移居、外在機遇',
    '奴僕宮': '朋友、部屬、人際資源',
    '官祿宮': '事業、職涯、社會地位',
    '田宅宮': '家庭環境、不動產、根基',
    '福德宮': '精神享受、興趣、內在福氣',
    '父母宮': '長輩、文書、原生家庭影響',
}


def get_current_daxian(chart, birth_year, gender, current_year=2026):
    """計算當前大限宮位（現在活在哪個宮）"""
    # 從五行局字串取出局數，如「土5局」→ 5
    wuxing_str = chart.get('五行局', '土5局')
    ju_num = next((int(c) for c in wuxing_str if c.isdigit()), 3)

    direction = chart.get('大限走向', '順')
    xusui = current_year - birth_year + 1  # 虛歲

    # 第幾個大限（0-indexed：第0個 = 命宮大限）
    daxian_idx = 0 if xusui < ju_num else (xusui - ju_num) // 10

    ming_str = chart.get('命宮', '甲寅')
    ming_zhi = ming_str[-1]
    ming_idx = ZW_P.index(ming_zhi) if ming_zhi in ZW_P else 0

    # 大限宮地支（順行=增 index，逆行=減 index）
    if direction == '順':
        daxian_idx_zw = (ming_idx + daxian_idx) % 12
    else:
        daxian_idx_zw = (ming_idx - daxian_idx) % 12
    daxian_zhi = ZW_P[daxian_idx_zw]

    # 宮名：依逆時針距命宮的位移（傳統 12 宮逆排）
    palace_offset = (ming_idx - daxian_idx_zw) % 12
    palace_name = PALACE_NAMES[palace_offset]
    theme = PALACE_THEMES.get(palace_name, '')

    # 宮中主星 + 輔星
    stars_in_palace = []
    for star, zhi in chart.get('主星', {}).items():
        if zhi == daxian_zhi:
            stars_in_palace.append(star)
    for star, zhi in chart.get('輔星', {}).items():
        if zhi == daxian_zhi:
            stars_in_palace.append(star)

    start_age = ju_num + daxian_idx * 10
    end_age   = start_age + 9

    return {
        'palace_zhi':  daxian_zhi,
        'palace_name': palace_name,
        'theme':       theme,
        'stars':       stars_in_palace,
        'age_range':   f"{start_age}~{end_age}歲",
        'start_age':   start_age,
    }


_LIUNIAN_HUA_EFFECT = {
    '祿': '資源暢通，逢凶化吉，{palace}事務今年順遂豐盛',
    '權': '能量爆發，掌握主導，{palace}今年主動有力',
    '科': '智慧提升，貴人相助，{palace}帶來聲譽與名望',
    '忌': '需謹慎留意，{palace}今年易有阻礙、糾紛或執著',
}

_PALACE_TOPIC = {
    '命宮':'自我狀態與外在形象','兄弟宮':'手足同事關係','夫妻宮':'親密關係與婚姻',
    '子女宮':'子女創意下屬','財帛宮':'金錢收入財運','疾厄宮':'身體健康壓力',
    '遷移宮':'外出移動機遇','奴僕宮':'人際朋友資源','官祿宮':'事業職涯發展',
    '田宅宮':'居家環境根基','福德宮':'精神享受內在','父母宮':'長輩文書文件',
}


def _palace_gan_from_chart(chart, palace_zhi):
    """從命宮干支推算任意宮位天干（不需傳入出生年干）"""
    ming_str = chart.get('命宮', '')
    if len(ming_str) < 2:
        return ''
    ming_gan, ming_zhi = ming_str[0], ming_str[1]
    if ming_gan not in GAN or ming_zhi not in ZW_P:
        return ''
    start_idx = (GAN.index(ming_gan) - ZW_P.index(ming_zhi)) % 10
    p_idx = ZW_P.index(palace_zhi) if palace_zhi in ZW_P else 0
    return GAN[(start_idx + p_idx) % 10]


def get_daxian_sihua(chart, daxian_info):
    """大限宮天干四化——告訴你這10年哪個宮位特別活躍"""
    daxian_zhi = daxian_info.get('palace_zhi', '')
    if not daxian_zhi:
        return {}

    daxian_gan = _palace_gan_from_chart(chart, daxian_zhi)
    if not daxian_gan:
        return {}

    sihua = SIHUA.get(daxian_gan, {})
    ming_str = chart.get('命宮', '')
    ming_zhi = ming_str[-1] if ming_str else ''
    ming_idx = ZW_P.index(ming_zhi) if ming_zhi in ZW_P else 0

    all_stars = {**chart.get('主星', {}), **chart.get('輔星', {})}
    result = {'daxian_gan': daxian_gan, 'sihua': {}}

    for hua_type in ('祿', '權', '科', '忌'):
        star_name = sihua.get(hua_type, '')
        if not star_name:
            continue
        palace_zhi = all_stars.get(star_name)
        if not palace_zhi:
            result['sihua'][hua_type] = {
                'star': star_name, 'palace': '未入盤',
                'desc': f"大限{daxian_gan}干：{star_name}化{hua_type}（輔星）",
            }
            continue
        p_idx = ZW_P.index(palace_zhi) if palace_zhi in ZW_P else 0
        offset = (ming_idx - p_idx) % 12
        palace_name = PALACE_NAMES[offset]
        topic = _PALACE_TOPIC.get(palace_name, '')
        effect = _LIUNIAN_HUA_EFFECT.get(hua_type, '').format(palace=palace_name)
        result['sihua'][hua_type] = {
            'star':    star_name,
            'palace':  palace_name,
            'palace_zhi': palace_zhi,
            'desc':    f"大限{daxian_gan}干：{star_name}化{hua_type}→{palace_name}（{topic}）",
        }

    return result


def get_liunian_sihua(chart, liunian_gan):
    """流年天干觸發四化，分析各宮今年影響"""
    sihua = SIHUA.get(liunian_gan, {})
    if not sihua:
        return {}

    ming_str = chart.get('命宮', '')
    ming_zhi = ming_str[-1] if ming_str else ''
    ming_idx = ZW_P.index(ming_zhi) if ming_zhi in ZW_P else 0

    all_stars = {**chart.get('主星', {}), **chart.get('輔星', {})}
    result = {}
    for hua_type in ('祿', '權', '科', '忌'):
        star_name = sihua.get(hua_type, '')
        if not star_name:
            continue
        palace_zhi = all_stars.get(star_name)
        if not palace_zhi:
            result[hua_type] = {
                'star': star_name, 'palace': '未入盤',
                'desc': f"{star_name}化{hua_type}（輔星未納入定位）",
            }
            continue
        p_idx = ZW_P.index(palace_zhi) if palace_zhi in ZW_P else 0
        offset = (ming_idx - p_idx) % 12
        palace_name = PALACE_NAMES[offset]
        topic = _PALACE_TOPIC.get(palace_name, '')
        effect = _LIUNIAN_HUA_EFFECT.get(hua_type, '').format(palace=palace_name)
        result[hua_type] = {
            'star':        star_name,
            'palace':      palace_name,
            'palace_zhi':  palace_zhi,
            'desc':        f"【{star_name}化{hua_type}→{palace_name}】{effect}（{topic}）",
        }
    return result


def get_current_xiaoxian(chart, birth_year, gender, current_year=2026):
    """計算當前小限宮位（每年一宮）
    男命從寅起逆行（寅→丑→子→亥...），女命從申起順行（申→酉→戌→亥...）
    """
    xusui = current_year - birth_year + 1

    yin_start  = ZW_P.index('寅')  # 0
    shen_start = ZW_P.index('申')  # 6

    if gender == '男':
        idx = (yin_start - (xusui - 1)) % 12
    else:
        idx = (shen_start + (xusui - 1)) % 12

    xiaoxian_zhi = ZW_P[idx]

    ming_str = chart.get('命宮', '')
    ming_zhi = ming_str[-1] if ming_str else ''
    ming_idx = ZW_P.index(ming_zhi) if ming_zhi in ZW_P else 0

    palace_offset = (ming_idx - idx) % 12
    palace_name = PALACE_NAMES[palace_offset]
    theme = PALACE_THEMES.get(palace_name, '')

    stars_in_palace = []
    for star, zhi in chart.get('主星', {}).items():
        if zhi == xiaoxian_zhi:
            stars_in_palace.append(star)
    for star, zhi in chart.get('輔星', {}).items():
        if zhi == xiaoxian_zhi:
            stars_in_palace.append(star)

    star_str = '·'.join(stars_in_palace) if stars_in_palace else '空宮'
    return {
        'palace_zhi':  xiaoxian_zhi,
        'palace_name': palace_name,
        'theme':       theme,
        'stars':       stars_in_palace,
        'age':         xusui,
        'desc': (f"小限流年（{current_year}，{xusui}歲）走{palace_name}（{xiaoxian_zhi}）："
                 f"{theme}，宮中：{star_str}"),
    }


def get_sihua_palace_map(chart, liunian_sihua=None, daxian_sihua=None):
    """三層四化整合：本命+大限+流年四化投影到12宮地圖

    Returns dict[palace_name] = {layers, intensity, has_ji, has_lu, summary}
    intensity≥2 的宮位是今年最活躍、最需要關注的。
    """
    palace_layers = {name: [] for name in PALACE_NAMES}
    all_stars = {**chart.get('主星', {}), **chart.get('輔星', {})}
    ming_str  = chart.get('命宮', '')
    ming_zhi  = ming_str[-1] if ming_str else ''
    ming_idx  = ZW_P.index(ming_zhi) if ming_zhi in ZW_P else 0

    # ① 本命四化（出生年干）
    born_sihua = chart.get('四化', {})
    for hua_type in ('祿', '權', '科', '忌'):
        star_name = born_sihua.get(hua_type, '')
        if not star_name:
            continue
        palace_zhi = all_stars.get(star_name)
        if not palace_zhi or palace_zhi not in ZW_P:
            continue
        offset = (ming_idx - ZW_P.index(palace_zhi)) % 12
        palace_layers[PALACE_NAMES[offset]].append(f"本命{hua_type}（{star_name}）")

    # ② 大限四化
    if daxian_sihua:
        for hua_type, info in daxian_sihua.get('sihua', {}).items():
            pname = info.get('palace', '')
            if pname in palace_layers:
                palace_layers[pname].append(f"大限{hua_type}（{info.get('star','')}）")

    # ③ 流年四化
    if liunian_sihua:
        for hua_type, info in liunian_sihua.items():
            pname = info.get('palace', '')
            if pname in palace_layers:
                palace_layers[pname].append(f"流年{hua_type}（{info.get('star','')}）")

    result = {}
    for palace_name, layers in palace_layers.items():
        if not layers:
            continue
        has_ji = any('忌' in l for l in layers)
        has_lu = any('祿' in l for l in layers)
        intensity = len(layers)
        if intensity >= 2:
            if has_ji and has_lu:
                summary = '祿忌交戰，此宮今年變動最大'
            elif has_ji:
                summary = '多層化忌匯聚，謹慎應對此宮課題'
            elif has_lu:
                summary = '多層化祿加持，此宮今年最順遂'
            else:
                summary = '多層四化加持，此宮今年最活躍'
        else:
            summary = layers[0]
        result[palace_name] = {
            'layers':    layers,
            'intensity': intensity,
            'has_ji':    has_ji,
            'has_lu':    has_lu,
            'summary':   summary,
        }

    return dict(sorted(result.items(), key=lambda x: x[1]['intensity'], reverse=True))


# ── 主入口 ──
def ziwei_chart(year_gan, year_zhi, lunar_month, lunar_day, hour_idx, gender):
    ming_p, shen_p = get_ming_shen(lunar_month, hour_idx)
    ming_zw = ZW_P.index(ming_p)
    ming_g = palace_gan(ming_zw, year_gan)
    wuxing = NAYIN.get((ming_g, ming_p), '土')
    ju = JU_NUM[wuxing]

    zw = place_ziwei(lunar_day, wuxing)
    tf = place_tianfu(zw)

    # 主星
    stars = arrange_zhuxing(zw, tf)

    # 輔星
    fu = {
        '左輔': ZW_P[(2 + lunar_month - 1) % 12],
        '右弼': ZW_P[(8 - (lunar_month - 1)) % 12],
        '文昌': ZW_P[(8 + hour_idx) % 12],
        '文曲': ZW_P[(2 - hour_idx) % 12],
    }

    # 年干系
    lucun = an_lucun(year_gan)
    qingyang, tuoluo = an_qingyang_tuoluo(lucun)
    tiankui, tianyue = an_tiankui_tianyue(year_gan)

    # 年支系
    tianma = an_tianma(year_zhi)
    huoxing, lingxing = an_huoxing_lingxing(year_zhi)
    honglian, tianxi = an_honglian_tianxi(year_zhi)

    # 時支系
    dikong, dijie = an_dikong_dijie(hour_idx)

    # 四化
    sihua = SIHUA.get(year_gan, {})

    # 大限（根據五行局 + 陽男陰女順行/陰男陽女逆行）
    is_yang_gan = year_gan in '甲丙戊庚壬'
    is_male = gender == '男'
    da_xian_direction = '順' if (is_yang_gan == is_male) else '逆'

    return {
        '命宮': f"{ming_g}{ming_p}",
        '身宮': shen_p,
        '五行局': f"{wuxing}{ju}局",
        '大限走向': da_xian_direction,
        '紫微': ZW_P[zw],
        '天府': ZW_P[tf],
        '主星': stars,
        '輔星': fu,
        '四化': sihua,
        '祿存': lucun,
        '擎羊': qingyang,
        '陀羅': tuoluo,
        '天魁': tiankui,
        '天鉞': tianyue,
        '天馬': tianma,
        '火星': huoxing,
        '鈴星': lingxing,
        '地空': dikong,
        '地劫': dijie,
        '紅鸞': honglian,
        '天喜': tianxi,
    }
