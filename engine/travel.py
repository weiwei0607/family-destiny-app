# engine/travel.py — 旅遊體質推薦引擎
# 根據喜用神、體質傾向、五行缺失，產出旅遊建議

# ── 五行 → 季節 ──────────────────────────────────────────────
_WX_SEASON = {
    '木': '春（3–5月）',
    '火': '夏（6–8月）',
    '土': '換季（3·6·9·12月初）',
    '金': '秋（9–11月）',
    '水': '冬（12–2月）',
}

# 忌神最旺的季節 → 對本命最消耗（忌什麼，該季就避）
_WX_SEASON_PEAK = {
    '木': '春（木旺，對忌木者壓力大）',
    '火': '夏（火旺，對忌火者過熱耗能）',
    '土': '換季時節（土旺，對忌土者易滯）',
    '金': '秋（金旺，對忌金者受制）',
    '水': '冬（水旺，對忌水者寒涼壓制）',
}

# ── 五行 → 環境/地景 ─────────────────────────────────────────
_WX_ENVIRONMENT = {
    '木': ['山林步道', '森林公園', '溫帶雨林', '田園鄉村', '竹林古道'],
    '火': ['熱帶島嶼', '溫泉湯屋', '南國陽光海灘', '燈火城市夜景', '火山地景'],
    '土': ['高原草原', '沙漠奇景', '歷史古城', '農莊體驗', '黃土大地'],
    '金': ['現代都會', '高山峰頂', '秋楓山景', '礦山溶洞', '清爽涼城'],
    '水': ['郵輪海洋', '湖泊河川', '北歐峽灣', '潛水浮潛', '溫帶雨季'],
}

# ── 五行 → 具體目的地（亞洲區為主）──────────────────────────
_WX_DESTINATION = {
    '木': {
        'top': ['日本（春·賞櫻）', '北海道（夏·薰衣草）', '清邁（叢林）', '張家界（森林峰柱）'],
        'cruise': None,
        'note': '適合山林系、步道健行、古樸溫泉鄉',
    },
    '火': {
        'top': ['峇里島', '泰國（清邁/普吉）', '沖繩', '台灣南部（墾丁）'],
        'cruise': '地中海郵輪（夏季）',
        'note': '適合熱帶海島、陽光充足、能量旺盛的地方',
    },
    '土': {
        'top': ['京都（古寺巷弄）', '西安（歷史古城）', '尼泊爾', '土耳其（卡帕多奇亞）'],
        'cruise': None,
        'note': '適合慢節奏、文化底蘊深厚、踏實感強的地方',
    },
    '金': {
        'top': ['東京（秋楓）', '首爾（秋）', '香港', '北海道（秋色）', '北阿爾卑斯'],
        'cruise': '日本沿岸郵輪（秋季）',
        'note': '適合現代都會、秋天高地、清爽乾燥氣候',
    },
    '水': {
        'top': ['北歐（冰島·挪威峽灣）', '斯堪地那維亞', '加拿大落磯山脈（冬）', '沖繩潛水'],
        'cruise': '北歐郵輪·阿拉斯加郵輪·地中海郵輪（春秋）',
        'note': '喜歡郵輪、海洋、湖泊、清涼水氣環境',
    },
}

# ── 體質標籤 ────────────────────────────────────────────────
_WX_CONSTITUTION = {
    '木': {
        'label': '木調型·生長體質',
        'traits': '喜歡有生機、帶綠意的環境，身體需要伸展空間，久坐易鬱悶，戶外活動補能量',
        'climate': '溫和濕潤、四季分明',
        'avoid': '過度乾燥或金屬感強的城市環境',
    },
    '火': {
        'label': '火調型·陽性體質',
        'traits': '需要光和熱，陰冷潮濕容易消沉，在溫暖陽光環境下最有活力',
        'climate': '溫暖、日照充足',
        'avoid': '嚴寒、長期水氣重（會壓火）',
    },
    '土': {
        'label': '土調型·穩定體質',
        'traits': '需要踏實感，適應力強但不喜變動，慢遊文化旅行比走馬看花更適合',
        'climate': '乾燥溫和，避免潮濕',
        'avoid': '過於潮濕的熱帶或多雨氣候',
    },
    '金': {
        'label': '金調型·清爽體質',
        'traits': '喜歡乾淨、有秩序感的環境，悶熱潮濕讓人不舒服，高地冷涼最舒適',
        'climate': '乾冷清爽，秋天最佳',
        'avoid': '夏天悶熱、過度潮濕',
    },
    '水': {
        'label': '水調型·流動體質',
        'traits': '對海洋、水域有天然親近感，需要流動感，待在同一個地方太久容易不安',
        'climate': '涼爽、水氣充足',
        'avoid': '過熱乾燥的沙漠型氣候',
    },
}

# ── 極光建議 ────────────────────────────────────────────────
# 看極光需冬天去北歐/加拿大，五行：水極旺、極寒
_AURORA_WX_FIT = {
    '水': ('非常適合', '水調體質天然親近極北水域，冬季能量強，心靈最放鬆'),
    '金': ('適合', '金生水，金調體質耐寒，秋冬能量本就充沛，極光旅行有充電感'),
    '木': ('尚可', '水生木，極北水氣對木有一定滋養，但冬日少光照對木調型略有影響'),
    '火': ('不太適合', '水克火，嚴冬極北最耗火調體質的能量，需帶足暖爐和心理準備'),
    '土': ('不太適合', '冬水旺克土，土調型在寒濕極北容易身體不適，建議找其他時節'),
}


# ── 日主 → 行程風格（怎麼旅遊）────────────────────────────
_DM_ITINERARY = {
    '甲': {
        'itinerary_type': '目標征服型',
        'itinerary_desc': '每站都有意義，喜歡帶著目標出發（登頂、打卡某個清單）',
        'itinerary_pace': '穩健快攻',
        'tag': '有意義的景點 > 隨機閒晃',
    },
    '乙': {
        'itinerary_type': '隨緣漫遊型',
        'itinerary_desc': '行程不必排滿，跟著感覺轉彎，意外驚喜最好',
        'itinerary_pace': '慢慢走',
        'tag': '小巷咖啡店 > 大景點排隊',
    },
    '丙': {
        'itinerary_type': '衝動說走就走型',
        'itinerary_desc': '計畫是有的，但隨時可以臨時改變，能量爆棚不怕累',
        'itinerary_pace': '快且彈性',
        'tag': '氣氛對了比計畫重要',
    },
    '丁': {
        'itinerary_type': '精緻體驗型',
        'itinerary_desc': '寧可少去幾個地方，每個地方都要有品質，不追數量追感受',
        'itinerary_pace': '慢中帶質',
        'tag': '一間好餐廳 > 三間普通的',
    },
    '戊': {
        'itinerary_type': '穩紮穩打型',
        'itinerary_desc': '事前規劃充分，按時走，不喜歡趕路，每個點都想待夠',
        'itinerary_pace': '慢遊不趕',
        'tag': '住三天比住一天好',
    },
    '己': {
        'itinerary_type': '細心蒐集型',
        'itinerary_desc': '做足功課，有攻略，但執行時保有彈性，擅長找到隱藏版景點',
        'itinerary_pace': '中速有規劃',
        'tag': '攻略先備好，到現場再靈活',
    },
    '庚': {
        'itinerary_type': '特種兵效率型',
        'itinerary_desc': '行程精密計畫，準時到準時走，效率最大化，一天能塞十個景點',
        'itinerary_pace': '高速衝刺',
        'tag': '08:00景點開門就到，18:00結束完美收尾',
    },
    '辛': {
        'itinerary_type': '精品少而精型',
        'itinerary_desc': '不追景點數量，追旅程質感，住的好吃的好比什麼都重要',
        'itinerary_pace': '緩慢精緻',
        'tag': '一個精品飯店 > 五個普通景點',
    },
    '壬': {
        'itinerary_type': '冒險探索型',
        'itinerary_desc': '喜歡自助、喜歡未知，大範圍移動，沒去過的地方才有趣',
        'itinerary_pace': '快且隨興',
        'tag': '地圖上沒標的地方最想去',
    },
    '癸': {
        'itinerary_type': '沉浸感受型',
        'itinerary_desc': '不在乎去了幾個地方，在乎那個地方有沒有觸動自己，情調勝過效率',
        'itinerary_pace': '慢且感性',
        'tag': '一個日落值得等三小時',
    },
}


def get_travel_profile(bazi_struct: dict, bazi_wuxing: dict, day_master: str = '') -> dict:
    """
    根據喜用神 + 五行缺失 + 日主個性 → 旅遊體質完整建議（兩層）

    bazi_struct : core.bazi_structure_analysis() 的輸出
    bazi_wuxing : _analyze_person() 裡的 bazi_wuxing（含 missing）
    day_master  : 日主天干（如 '庚'）
    """
    xiyong   = bazi_struct.get('xiyong', [])
    jishen   = bazi_struct.get('jishen', [])
    missing  = bazi_wuxing.get('missing', [])
    tiaohou  = bazi_struct.get('tiaohou', '')
    strength = bazi_struct.get('strength', 'neutral')

    # 主喜用神（調候優先）
    primary = tiaohou if tiaohou else (xiyong[0] if xiyong else '')

    # 體質
    constitution = _WX_CONSTITUTION.get(primary, {
        'label': '均衡型',
        'traits': '五行均衡，適應力強，各類環境皆可',
        'climate': '無特定偏好',
        'avoid': '無特定禁忌',
    })

    # 最佳季節
    best_season_wx = list(dict.fromkeys(
        ([primary] if primary else []) +
        [wx for wx in xiyong if wx != primary] +
        [wx for wx in missing if wx not in jishen]
    ))
    best_seasons = [_WX_SEASON[wx] for wx in best_season_wx if wx in _WX_SEASON]

    # 避開季節
    avoid_seasons = list(dict.fromkeys(
        _WX_SEASON_PEAK[wx] for wx in jishen if wx in _WX_SEASON_PEAK
    ))

    # 推薦環境
    environments = []
    for wx in best_season_wx[:3]:
        environments.extend(_WX_ENVIRONMENT.get(wx, []))

    # 推薦目的地
    dest_info      = _WX_DESTINATION.get(primary, {})
    top_destinations = dest_info.get('top', [])
    cruise_rec     = dest_info.get('cruise')
    dest_note      = dest_info.get('note', '')
    secondary_wx   = xiyong[1] if len(xiyong) > 1 else ''
    secondary_dest = _WX_DESTINATION.get(secondary_wx, {}).get('top', [])[:2]

    # 極光
    aurora_fit, aurora_note = _AURORA_WX_FIT.get(primary, ('尚可', ''))

    # 層一：環境偏好（喜用神決定）
    env_style = _env_style(primary, strength)

    # 層二：行程風格（日主個性決定）
    itinerary = _DM_ITINERARY.get(day_master, {
        'itinerary_type': '彈性自由型',
        'itinerary_desc': '沒有特定模式，隨心安排',
        'itinerary_pace': '彈性',
        'tag': '走到哪算到哪',
    })

    # 合體標籤
    combo_label = _combo_label(primary, day_master)

    return {
        'primary_wx':        primary,
        'xiyong':            xiyong,
        'jishen':            jishen,
        'constitution':      constitution,
        'best_seasons':      best_seasons[:3],
        'avoid_seasons':     avoid_seasons[:2],
        'environments':      list(dict.fromkeys(environments))[:6],
        'top_destinations':  top_destinations,
        'secondary_dest':    secondary_dest,
        'cruise_rec':        cruise_rec,
        'dest_note':         dest_note,
        'aurora_fit':        aurora_fit,
        'aurora_note':       aurora_note,
        'style':             env_style,        # 舊欄位保留相容
        'itinerary':         itinerary,
        'combo_label':       combo_label,
    }


def _env_style(primary_wx: str, strength: str) -> dict:
    styles = {
        '木': {'type': '自然系探索者', 'pace': '中速', 'prefer': '登山健行・古道・森林浴・農村民宿'},
        '火': {'type': '陽光能量旅人', 'pace': '快節奏', 'prefer': '海島度假・夜市・派對氛圍・活動豐富'},
        '土': {'type': '文化深度旅者', 'pace': '慢遊', 'prefer': '古城漫步・博物館・在地美食・長住型'},
        '金': {'type': '都會精品旅人', 'pace': '中速有計畫', 'prefer': '現代城市・購物・設計感住宿・秋楓美景'},
        '水': {'type': '海洋漂流者', 'pace': '隨興流動', 'prefer': '郵輪・潛水・湖邊小屋・北歐極地'},
    }
    base = dict(styles.get(primary_wx, {'type': '萬能旅人', 'pace': '彈性', 'prefer': '各類型皆適合'}))
    if strength in ('weak', 'slightly_weak'):
        base['note'] = '身弱：少量多次勝過長途跋涉，旅途中要留白'
    elif strength in ('strong', 'slightly_strong'):
        base['note'] = '身強：能量充沛，高強度行程反而補血'
    else:
        base['note'] = '中和：彈性高，行程密度隨當下狀態調整'
    return base


def _combo_label(primary_wx: str, dm: str) -> str:
    """環境偏好 × 行程風格 → 合體標籤"""
    env_keywords = {
        '木': '山林系', '火': '陽光系', '土': '文化系',
        '金': '都市系', '水': '海洋系',
    }
    pace_keywords = {
        '甲': '目標征服', '乙': '隨緣漫遊', '丙': '衝動快攻',
        '丁': '精緻慢品', '戊': '穩紮穩打', '己': '蒐集攻略',
        '庚': '特種兵', '辛': '精品少精', '壬': '冒險探索', '癸': '沉浸感受',
    }
    env  = env_keywords.get(primary_wx, '萬能')
    pace = pace_keywords.get(dm, '自由')
    return f"{env} · {pace}"
