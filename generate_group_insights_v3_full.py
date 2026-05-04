#!/usr/bin/env python3
"""生成特定群體的五系統深度交叉洞察報告（v3 完整細緻版）"""

from app import app
client = app.test_client()

ALL_CENTERS = ['頭腦', '邏輯', '喉嚨', 'G中心', '心輪', '情緒', '薦骨', '脾/直覺', '根部']

CENTER_HUMAN_DESIGN = {
    '頭腦': '靈感與問題的壓力中心',
    '邏輯': '概念化與理解的中心',
    '喉嚨': '溝通與行動的發起中心',
    'G中心': '方向、身份與愛的中心',
    '心輪': '意志與承諾的動力中心',
    '情緒': '情緒波與感受的動力中心',
    '薦骨': '生命力、回應與工作的能量中心',
    '脾/直覺': '當下覺知與生存本能的中心',
    '根部': '壓力與腎上腺素的動力中心'
}

# 天干五行與陰陽
STEM_INFO = {
    '甲': ('木', '陽'), '乙': ('木', '陰'), '丙': ('火', '陽'), '丁': ('火', '陰'),
    '戊': ('土', '陽'), '己': ('土', '陰'), '庚': ('金', '陽'), '辛': ('金', '陰'),
    '壬': ('水', '陽'), '癸': ('水', '陰')
}

# 五行生剋
WUXING_CYCLE = {
    '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
    '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
    '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
    '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
    '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'},
}

# 十神關係
def shishen(day_master, target_stem):
    me_elem, me_yin = STEM_INFO[day_master]
    ta_elem, ta_yin = STEM_INFO[target_stem]
    if me_elem == ta_elem:
        return '比肩' if me_yin == ta_yin else '劫財'
    if WUXING_CYCLE[me_elem]['生'] == ta_elem:
        return '食神' if me_yin == ta_yin else '傷官'
    if WUXING_CYCLE[ta_elem]['生'] == me_elem:
        return '偏印' if me_yin == ta_yin else '正印'
    if WUXING_CYCLE[me_elem]['克'] == ta_elem:
        return '偏財' if me_yin == ta_yin else '正財'
    return '七殺' if me_yin == ta_yin else '正官'


def bazi_relation_full(dm1, dm2):
    if dm1 == dm2:
        return "比劫", "同氣相助，亦敵亦友"
    e1, _ = STEM_INFO[dm1]
    e2, _ = STEM_INFO[dm2]
    if WUXING_CYCLE[e1]['生'] == e2:
        return "我生", f"{dm1}生{dm2}，付出與啟發"
    if WUXING_CYCLE[e2]['生'] == e1:
        return "生我", f"{dm2}生{dm1}，滋養與支持"
    if WUXING_CYCLE[e1]['克'] == e2:
        return "我剋", f"{dm1}剋{dm2}，掌控與管理"
    return "剋我", f"{dm2}剋{dm1}，約束與挑戰"


# 二十八宿
XXIU_ANIMAL = {
    '角': '蛟', '亢': '龍', '氐': '貉', '房': '兔', '心': '狐', '尾': '虎', '箕': '豹',
    '斗': '獬', '牛': '牛', '女': '蝠', '虛': '鼠', '危': '燕', '室': '豬', '壁': '獝',
    '奎': '狼', '婁': '狗', '胃': '雞', '昴': '烏', '畢': '猴', '觜': '猿', '參': '虎',
    '井': '犴', '鬼': '羊', '柳': '獐', '星': '馬', '張': '鹿', '翼': '蛇', '軫': '蚓'
}
XXIU_WUXING = {
    '角': '木', '亢': '金', '氐': '土', '房': '火', '心': '火', '尾': '火', '箕': '水',
    '斗': '木', '牛': '金', '女': '土', '虛': '火', '危': '火', '室': '火', '壁': '水',
    '奎': '木', '婁': '金', '胃': '土', '昴': '火', '畢': '火', '觜': '火', '參': '水',
    '井': '木', '鬼': '金', '柳': '土', '星': '火', '張': '火', '翼': '火', '軫': '水'
}


def xingxiu_relation_detail(x1, x2):
    wx1, wx2 = XXIU_WUXING.get(x1, ''), XXIU_WUXING.get(x2, '')
    if not wx1 or not wx2:
        return "未知", ""
    if wx1 == wx2:
        return f"同氣（同{wx1}）", "氣場相近，容易理解但盲點疊加"
    if WUXING_CYCLE[wx1]['生'] == wx2:
        return f"相生（{wx1}生{wx2}）", f"{x1}對{x2}有生助之力"
    if WUXING_CYCLE[wx2]['生'] == wx1:
        return f"相生（{wx2}生{wx1}）", f"{x2}對{x1}有生助之力"
    if WUXING_CYCLE[wx1]['克'] == wx2:
        return f"相剋（{wx1}剋{wx2}）", f"{x1}對{x2}有制約，需磨合"
    return f"相剋（{wx2}剋{wx1}）", f"{x2}對{x1}有制約，需磨合"


# 星座元素
SIGN_ELEMENT = {
    '牡羊': '火', '獅子': '火', '射手': '火',
    '金牛': '土', '處女': '土', '摩羯': '土',
    '雙子': '風', '天秤': '風', '水瓶': '風',
    '巨蟹': '水', '天蠍': '水', '雙魚': '水'
}


def astro_compat(sign1, sign2):
    e1, e2 = SIGN_ELEMENT.get(sign1, ''), SIGN_ELEMENT.get(sign2, '')
    if not e1 or not e2:
        return "", ""
    if e1 == e2:
        return f"同{e1}象", "理解彼此的核心驅動力，但容易在同一個洞裡跌倒"
    harmonious = {('火','風'), ('風','火'), ('土','水'), ('水','土')}
    if (e1, e2) in harmonious:
        return f"{e1}-{e2}和諧", "互補且流暢，一個發起一個回應"
    challenging = {('火','水'), ('水','火'), ('風','土'), ('土','風')}
    if (e1, e2) in challenging:
        return f"{e1}-{e2}張力", "需要磨合，但張力帶來深度與成長"
    return f"{e1}-{e2}動態", "互相需要但方式不同"


# 紫微命宮主星
def get_mingzhu(zw):
    ming = zw.get('命宮', '')
    if not ming or len(ming) < 2:
        return "未知"
    ming_zhi = ming[-1]
    zhuxing = zw.get('主星', {})
    stars = [s for s, z in zhuxing.items() if z == ming_zhi]
    return '、'.join(stars) if stars else "未知"


# ============== 人類圖通道詳解 ==============
CHANNEL_MEANING = {
    (5, 15): "**5-15 韻律通道** — 你有一個不可動搖的內在節奏。你必須按照自己的時間表生活，不能被催促。這條通道也讓你對季節、韻律、美感特別敏感。",
    (3, 60): "**3-60 突變通道** — 壓力是你創新的燃料。你能在限制和壓迫中找到突破的方式，經歷混亂後建立新秩序。你的存在本身就帶來變化。",
    (7, 31): "**7-31 領導力通道（Alpha）** — 你有天生的方向感，能為群體指引方向。但這條通道需要被邀請才能發揮，否則會變成強迫別人聽你的。",
    (10, 34): "**10-34 探索通道** — 做自己就是你的超能力。你有強大的個人力量，當你忠於自己時，能量會自然流動。這是「行動中的愛自己」。",
    (10, 57): "**10-57 完美呈現通道** — 你的直覺會指引你的行動。你不需要思考，身體當下就知道該做什麼。這是基於生存本能的優雅。",
    (16, 48): "**16-48 深度通道** — 你的才華來自於深度掌握。你不是淺嚐輒止的人，一旦投入就會鑽研到很深。技能是你的語言。",
    (19, 49): "**19-49 敏感通道** — 你對「需求」極其敏感，無論是自己的還是別人的。你有一套內在的原則來判斷誰值得被支持。",
    (27, 50): "**27-50 養育通道** — 你有教導和照顧的天賦，能將價值觀傳遞給他人。你會滋養別人，但也要記得滋養自己。",
    (30, 41): "**30-41 夢想通道** — 你被渴望驅動，想要體驗一切。你有豐富的幻想和渴望，關鍵是找到正確的體驗來回應這些渴望。",
    (34, 57): "**34-57 力量通道** — 你的力量來自當下的直覺。你不需要計畫，身體在當下就知道該怎麼做。這是生存層面的強大力量。",
    (37, 40): "**37-40 家庭/社群通道** — 你在關係中尋求承諾和回報。你願意為社群付出，但也需要感受到公平和回饋。",
    (47, 64): "**47-64 抽象通道** — 你的頭腦會從困惑中提煉意義。你經歷混亂和壓迫，但最終會理解其中的模式。這是抽象思維的禮物。",
    (21, 45): "**21-45 金錢/掌控通道** — 你有管理資源和掌控局面的天賦。你知道如何聚集和分配資源，是金錢和物質世界的管理者。",
    (4, 63): "**4-63 邏輯通道** — 你的頭腦會尋找公式化的解答。你擅長建立邏輯框架，從懷疑中找到確定的答案。",
}

# 閘門簡短含義
GATE_MEANING = {
    1: "創意 / 自我表達", 2: "方向 / 接收", 3: "秩序 / 在混亂中建立", 4: "解答 / 公式化",
    5: "固定模式 / 節奏", 6: "衝突 / 親密中的摩擦", 7: "軍隊 / 方向", 8: "貢獻 / 個人風格",
    9: "專注 / 細節處理", 10: "愛自己 / 行為", 11: "和平 / 想法", 12: "謹慎 / 停頓",
    13: "傾聽者 / 過往", 14: "技能 / 財富力量", 15: "極端 / 人類之愛", 16: "熱情 / 技能",
    17: "意見 / 跟隨", 18: "修正 / 校正", 19: "需求 / 接近", 20: "當下 / 現在",
    21: "控制 / 獵人", 22: "優雅 / 開放", 23: "分裂 / 同化", 24: "回歸 / 合理化",
    25: "無條件之愛 / 天真", 26: "偉大推手 / 累積", 27: "滋養 / 照顧", 28: "掙扎 / 冒險",
    29: "承諾 / 毅力", 30: "渴望 / 感覺", 31: "領導 / 影響", 32: "延續 / 本能",
    33: "隱退 / 隱私", 34: "力量 / 力量", 35: "進展 / 改變", 36: "危機 / 幽暗之光",
    37: "友誼 / 家庭", 38: "對抗 / 戰士", 39: "挑釁 / 阻礙", 40: "孤獨 / 交付",
    41: "幻想 / 縮減", 42: "成長 / 增加", 44: "警覺 / 過來人", 45: "聚集 / 主人",
    46: "決心 / 身體之愛", 47: "理解 / 壓迫", 48: "深度 / 井", 49: "原則 / 革命",
    50: "價值觀 / 熔爐", 51: "衝擊 / 覺醒", 52: "靜止 / 專注", 53: "發展 / 開始",
    54: "野心 / 驅動", 55: "精神 / 豐盛", 56: "刺激 / 浪遊者", 57: "直覺 / 溫柔",
    58: "活力 / 喜悅", 59: "親密 / 性", 60: "限制 / 接受", 61: "神秘 / 內在真理",
    62: "細節 / 小處著手", 63: "懷疑 / 完工後", 64: "困惑 / 多樣化",
}


def profile_detail(profile):
    """Profile 詳細解讀"""
    profiles = {
        '1/4': {
            'conscious': '1爻（研究者）—— 意識層面需要深入研究、打穩基礎才能安心',
            'unconscious': '4爻（機會主義者）—— 身體層面自然散發影響力，透過人際網絡被召喚',
            'summary': '研究者與影響者的結合。你必須先深入研究，建立信心，然後你的4爻會自然將這些知識傳播給你的人際網絡。你適合「先專精，再分享」的路徑。',
            'challenge': '容易因為覺得準備不足而永遠不開始；也可能因為4爻的網絡壓力而勉強自己社交。'
        },
        '3/5': {
            'conscious': '3爻（實驗者）—— 意識層面透過嘗試和犯錯來學習，失敗是過程的一部分',
            'unconscious': '5爻（異端者/救世主）—— 身體層面散發「可以被投射期待」的光環，別人容易對你有不切實際的期待',
            'summary': '實驗者與異端者的結合。你的人生充滿嘗試和「看起來像失敗」的經驗，但這些都是為了讓你的5爻能從中提煉出普世智慧。別人會把你當成可以解決問題的人，但你要記得你不是來拯救所有人的。',
            'challenge': '3爻的錯誤可能讓5爻的「形象」受損；別人對你的期待可能讓你感到壓力。'
        },
        '4/6': {
            'conscious': '4爻（機會主義者）—— 意識層面透過人際網絡和機會來運作',
            'unconscious': '6爻（典範/觀察者）—— 身體層面有「退居觀察」的傾向，從高處俯瞰人生',
            'summary': '機會主義者與典範的結合。你的人生分三階段：0-30歲像3爻一樣嘗試犯錯；30-50歲退居觀察，從經驗中提煉智慧；50歲後成為典範。你的4爻讓你在每個階段都有人際網絡的支持。',
            'challenge': '4爻的網絡需求與6爻的疏離傾向會拉扯；30歲後可能感到孤獨或「與人群脫節」。'
        },
        '6/2': {
            'conscious': '6爻（典範/觀察者）—— 意識層面追求成為完美的榜樣',
            'unconscious': '2爻（隱士/天賦者）—— 身體層面有「不用學就會」的天賦，但需要被召喚才會展現',
            'summary': '典範與天賦者的結合。你的人生分三階段：0-30歲像3爻一樣嘗試犯錯（因為6爻的3階段）；30-50歲退居觀察；50歲後成為完美的6爻典範。你的2爻天賦會被別人「意外發現」，然後召喚你出來。你不會主動推銷自己，但當對的人來找你的時候，你的薦骨會知道。',
            'challenge': '2爻的「懶散/獨處」可能被誤解為冷漠；6爻的完美主義可能讓你對自己的錯誤過度苛責。'
        },
    }
    return profiles.get(profile, {'conscious': '', 'unconscious': '', 'summary': '', 'challenge': ''})


def authority_detail(authority):
    details = {
        '薦骨權威': '薦骨中心會對具體的「是/否」問題發出聲音（嗯/唔）或身體感受。不要用腦袋分析，用身體回應。問越多具體問題，越清楚。',
        '情緒權威': '情緒有波動，高點和低點都不適合做決定。重大決定要睡一覺，等情緒波沉澱到「清明」的狀態再做。',
        '直覺權威': '當下的身體覺知。那個「知道」只在當下存在，過了就沒了。要學會相信第一時間的身體反應。',
        '意志力權威': '承諾前要清楚自己的意願，不要為了證明自己或討好別人而答應。',
        '自我投射權威': '透過說話來釐清自己。當你把想法說出來，聽聽自己說了什麼，就知道答案了。',
    }
    return details.get(authority, authority)


def get_hd_gates_summary(hd):
    pg = hd['personality_gates']
    dg = hd['design_gates']
    all_gates = set(pg.values()) | set(dg.values())
    return {
        'sun': pg.get('太陽', 0),
        'moon': pg.get('月亮', 0),
        'earth': pg.get('地球', 0),
        'nodes': [pg.get('北交點', 0), pg.get('南交點', 0)],
        'all': sorted(all_gates),
        'channels': hd['active_channels']
    }


def get_data(name, date, time, gender):
    resp = client.post('/api/analyze', json={'name': name, 'date': date, 'time': time, 'gender': gender, 'location': 'taipei'})
    return resp.get_json()


def analyze_person(m):
    """個人深度分析"""
    lines = []
    name = m['name']
    hd = m['humandesign']
    bz = m['bazi']
    astro = m['astrology']
    zw = m['ziwei']
    xx = m['xingxiu']
    
    dm = bz['day_master']
    elem, yin = STEM_INFO[dm]
    mingzhu = get_mingzhu(zw)
    sihua = zw.get('四化', {})
    sihua_str = ' · '.join([f"{v}{k}" for k,v in sihua.items()]) if sihua else ""
    defined = set(hd['defined_centers'])
    undefined = set(ALL_CENTERS) - defined
    gs = get_hd_gates_summary(hd)
    
    pd = profile_detail(hd['profile'])
    
    lines.append(f"## {name} 個人深度檔案\n")
    
    # 八字
    lines.append(f"### 📿 八字命理\n")
    lines.append(f"**四柱**：{bz['year']} {bz['month']} {bz['day']} {bz['hour']}")
    lines.append(f"**日主**：**{dm}**（{elem}·{yin}）")
    traits = {
        '木': "向上生長、有韌性、仁慈、喜歡規劃",
        '火': "熱情、明亮、行動力強、喜歡表達",
        '土': "穩重、包容、務實、值得信賴",
        '金': "果斷、精確、有原則、重義氣",
        '水': "靈活、智慧、適應力強、善於溝通"
    }
    lines.append(f"> 日主{dm}為{elem}性，{yin}干。{dm}日主的人通常具有{elem}的特質——{traits.get(elem, '')}")
    lines.append("")
    
    # 西洋占星
    lines.append(f"### 🔮 西洋占星\n")
    lines.append(f"**太陽**：{astro['太陽']['sign']} — 你的核心身份與人生目標")
    lines.append(f"**月亮**：{astro['月亮']['sign']} — 你的情感需求與安全感來源")
    lines.append(f"**水星**：{astro.get('水星',{}).get('sign','')} — 你的思考與溝通方式")
    lines.append(f"**金星**：{astro.get('金星',{}).get('sign','')} — 你的愛情觀與價值觀")
    lines.append(f"**火星**：{astro.get('火星',{}).get('sign','')} — 你的行動力與欲望")
    lines.append(f"**木星**：{astro.get('木星',{}).get('sign','')} — 你的擴張與成長領域")
    lines.append(f"**土星**：{astro.get('土星',{}).get('sign','')} — 你的限制與功課")
    lines.append("")
    
    # 紫微
    lines.append(f"### ⭐ 紫微斗數\n")
    lines.append(f"**命宮**：{zw.get('命宮','')} · 主星「{mingzhu}」")
    lines.append(f"**五行局**：{zw.get('五行局','')}")
    lines.append(f"**身宮**：{zw.get('身宮','')} — 後天努力與中年後的發展方向")
    lines.append(f"**四化**：{sihua_str}")
    lines.append(f"**輔星**：{', '.join([f'{k}在{v}' for k,v in zw.get('輔星',{}).items()]) if zw.get('輔星') else '無'}")
    lines.append("")
    
    # 星宿
    lines.append(f"### 🌟 二十八宿\n")
    lines.append(f"**星宿**：{xx}宿（{XXIU_ANIMAL.get(xx, '?')}）· 五行{XXIU_WUXING.get(xx, '?')}")
    lines.append("")
    
    # 人類圖 - 核心
    lines.append(f"### 🌀 人類圖核心設定\n")
    lines.append(f"**能量類型**：{hd['energy_type']}")
    lines.append(f"**人生角色 Profile**：{hd['profile']}")
    lines.append(f"> {pd.get('summary','')}")
    lines.append(f"> - 意識（上）：{pd.get('conscious','')}")
    lines.append(f"> - 無意識（下）：{pd.get('unconscious','')}")
    lines.append(f"> - 挑戰：{pd.get('challenge','')}")
    lines.append("")
    lines.append(f"**內在權威**：{hd['authority']}")
    lines.append(f"> {authority_detail(hd['authority'])}")
    lines.append("")
    lines.append(f"**策略**：{hd['strategy']}")
    lines.append(f"**非自己主題**：{hd.get('not_self','')} — 當你偏離自己的策略時，會感受到的情緒")
    lines.append("")
    
    # 人類圖 - 中心
    lines.append(f"**定義中心（穩定能量來源）**：")
    for c in sorted(defined):
        lines.append(f"- **{c}**：{CENTER_HUMAN_DESIGN[c]}")
    lines.append("")
    lines.append(f"**未定義中心（開放學習區域）**：")
    for c in sorted(undefined):
        lines.append(f"- **{c}**：{CENTER_HUMAN_DESIGN[c]} → 容易被他人能量影響，是學習區也是放大鏡")
    lines.append("")
    
    # 人類圖 - 通道
    lines.append(f"**通道**（定義了哪些中心連接，形成穩定的能量流動）：")
    for ch in hd['active_channels']:
        g1, g2 = ch
        key = tuple(sorted((g1, g2)))
        meaning = CHANNEL_MEANING.get(key, f"通道 {g1}-{g2}")
        lines.append(f"- {meaning}")
    if not hd['active_channels']:
        lines.append("- 無定義通道（反映者）")
    lines.append("")
    
    # 人類圖 - 關鍵閘門
    lines.append(f"**關鍵閘門**（行星啟動的閘門，塑造了你的核心主題）：")
    lines.append(f"- ☉ 意識太陽閘門 **{gs['sun']}**：{GATE_MEANING.get(gs['sun'], '')} — 你這輩子來體驗的主題")
    lines.append(f"- ☽ 意識月亮閘門 **{gs['moon']}**：{GATE_MEANING.get(gs['moon'], '')} — 你的驅動力與日常需求")
    lines.append(f"- 🜨 地球閘門 **{gs['earth']}**：{GATE_MEANING.get(gs['earth'], '')} — 你扎根的方向")
    lines.append(f"- ↗ 北交點閘門 **{gs['nodes'][0]}**：{GATE_MEANING.get(gs['nodes'][0], '')} — 這輩子要發展的方向")
    lines.append(f"- ↘ 南交點閘門 **{gs['nodes'][1]}**：{GATE_MEANING.get(gs['nodes'][1], '')} — 你帶來的過往天賦")
    lines.append("")
    
    # 人類圖 - 全部閘門
    lines.append(f"**全部啟動閘門**（意識+設計層）：")
    gate_strs = [f"Gate {g}（{GATE_MEANING.get(g, '?')}）" for g in gs['all']]
    for i in range(0, len(gate_strs), 3):
        lines.append("、".join(gate_strs[i:i+3]))
    lines.append("")
    
    return '\n'.join(lines)


def analyze_pair(p1, p2, defined_map, undefined_map):
    """兩兩深度分析"""
    lines = []
    n1, n2 = p1['name'], p2['name']
    dm1, dm2 = p1['bazi']['day_master'], p2['bazi']['day_master']
    e1, _ = STEM_INFO[dm1]
    e2, _ = STEM_INFO[dm2]
    astro1, astro2 = p1['astrology'], p2['astrology']
    sun1, sun2 = astro1['太陽']['sign'], astro2['太陽']['sign']
    moon1, moon2 = astro1['月亮']['sign'], astro2['月亮']['sign']
    xx1, xx2 = p1['xingxiu'], p2['xingxiu']
    hd1, hd2 = p1['humandesign'], p2['humandesign']
    
    gs1 = get_hd_gates_summary(hd1)
    gs2 = get_hd_gates_summary(hd2)
    
    lines.append(f"### {n1} × {n2}\n")
    
    # 八字
    rel, desc = bazi_relation_full(dm1, dm2)
    rel2, desc2 = bazi_relation_full(dm2, dm1)
    lines.append(f"**📿 八字十神**：{dm1}（{e1}）→ {dm2}（{e2}）= **{rel}** · {desc}")
    lines.append(f"> 反過來：{dm2} 看 {dm1} = **{rel2}** · {desc2}")
    if '生我' in rel:
        lines.append(f"> 💡 **{n2} 是 {n1} 的滋養方**：{n1} 可以向 {n2} 尋求支持與資源")
    elif '我生' in rel:
        lines.append(f"> 💡 **{n1} 是 {n2} 的付出方**：{n1} 對 {n2} 有創造啟發的作用，注意不過度消耗")
    elif '比劫' in rel:
        lines.append(f"> 💡 **比劫關係**：並肩作戰的夥伴，但要避免競爭較勁")
    elif '剋我' in rel:
        lines.append(f"> 💡 **{n2} 對 {n1} 有約束力**：壓力即動力，適當的挑戰促進成長")
    elif '我剋' in rel:
        lines.append(f"> 💡 **{n1} 對 {n2} 有影響力**：尊重對方自主性，不要過度掌控")
    lines.append("")
    
    # 西洋占星
    se_compat, se_desc = astro_compat(sun1, sun2)
    me_compat, me_desc = astro_compat(moon1, moon2)
    lines.append(f"**🔮 西洋占星**：")
    lines.append(f"- 太陽：{sun1} × {sun2} → {se_compat} · {se_desc}")
    lines.append(f"- 月亮：{moon1} × {moon2} → {me_compat} · {me_desc}")
    lines.append("")
    
    # 星宿
    xx_rel, xx_desc = xingxiu_relation_detail(xx1, xx2)
    lines.append(f"**🌟 二十八宿**：{xx1}（{XXIU_ANIMAL.get(xx1,'?')}·{XXIU_WUXING.get(xx1,'?')}）× {xx2}（{XXIU_ANIMAL.get(xx2,'?')}·{XXIU_WUXING.get(xx2,'?')}）→ **{xx_rel}**")
    lines.append(f"> {xx_desc}")
    lines.append("")
    
    # 人類圖 - 定義中心互補
    p1_can = defined_map[n1] & undefined_map[n2]
    p2_can = defined_map[n2] & undefined_map[n1]
    shared = defined_map[n1] & defined_map[n2]
    both_undef = undefined_map[n1] & undefined_map[n2]
    
    lines.append(f"**🌀 人類圖能量互補**：")
    if p1_can:
        lines.append(f"- {n1} 可穩定支持 {n2}：{', '.join(sorted(p1_can))}")
    if p2_can:
        lines.append(f"- {n2} 可穩定支持 {n1}：{', '.join(sorted(p2_can))}")
    if shared:
        lines.append(f"- ✅ 共同語言：{', '.join(sorted(shared))}（同頻共振，不需解釋）")
    if both_undef:
        lines.append(f"- ⚠️ 共同盲點：{', '.join(sorted(both_undef))}（兩人都開放，需外部判斷）")
    lines.append("")
    
    # 人類圖 - 閘門重疊
    gates1 = set(gs1['all'])
    gates2 = set(gs2['all'])
    shared_gates = gates1 & gates2
    if shared_gates:
        lines.append(f"**🌀 閘門重疊**：")
        lines.append(f"> 兩人共同啟動的閘門：{', '.join([f'Gate {g}（{GATE_MEANING.get(g, '')}）' for g in sorted(shared_gates)])}")
        lines.append(f"> 這代表你們在這些主題上有共同的頻率，容易互相理解。")
        lines.append("")
    
    # 人類圖 - 通道互補（一个人的通道中心是另一个人的未定义中心）
    lines.append(f"**🌀 通道層面的互動**：")
    for ch in hd1['active_channels']:
        g1, g2 = ch
        c1 = None
        for c, gates in {
            '頭腦': [64,61,63], '邏輯': [17,62,23,56,16,11,35],
            '喉嚨': [8,12,20,31,33,45], 'G中心': [1,2,7,10,13,15,25],
            '心輪': [21,40,26,51], '情緒': [6,37,22,36,49,55],
            '薦骨': [3,5,9,29,14,34,27,42,59], '脾/直覺': [48,18,57,28,32,44,50],
            '根部': [58,38,54,53,60,52,19,39,41],
        }.items():
            if g1 in gates or g2 in gates:
                pass
    # 簡化：直接描述每個人的通道特質如何影響關係
    if hd1['active_channels']:
        lines.append(f"- {n1} 的通道賦予其：" + "；".join([CHANNEL_MEANING.get(tuple(sorted(ch)), f"通道{ch[0]}-{ch[1]}") for ch in hd1['active_channels']]))
    if hd2['active_channels']:
        lines.append(f"- {n2} 的通道賦予其：" + "；".join([CHANNEL_MEANING.get(tuple(sorted(ch)), f"通道{ch[0]}-{ch[1]}") for ch in hd2['active_channels']]))
    lines.append("")
    
    # 四場景具體建議
    lines.append(f"**💡 如何協助對方變得更好——四場景策略**：")
    
    t1, t2 = hd1['energy_type'], hd2['energy_type']
    a1, a2 = hd1['authority'], hd2['authority']
    
    # 學習成長
    lines.append(f"\n1️⃣ **學習成長場景**：")
    brain1 = '頭腦' in defined_map[n1] or '邏輯' in defined_map[n1]
    brain2 = '頭腦' in defined_map[n2] or '邏輯' in defined_map[n2]
    if brain1 and not brain2:
        lines.append(f"   → {n1} 有頭腦/邏輯定義，適合擔任{n2}的知識引導者。{n2}在學習時容易思緒紛亂，{n1}可以幫忙建立結構。")
    elif brain2 and not brain1:
        lines.append(f"   → {n2} 有頭腦/邏輯定義，適合擔任{n1}的知識引導者。{n1}在學習時容易思緒紛亂，{n2}可以幫忙建立結構。")
    elif brain1 and brain2:
        lines.append(f"   → 兩人都有頭腦/邏輯定義，學習時可以互相激盪想法。但要注意不要一起鑽牛角尖。")
    else:
        lines.append(f"   → 兩人頭腦/邏輯都開放，學習時容易一起迷失。建議各自獨立學習後再交流，或引入第三方資源。")
    
    # 工作行動
    lines.append(f"\n2️⃣ **工作行動場景**：")
    if '顯示者' in t1:
        lines.append(f"   → {n1}（{t1}）有強大的發起力，適合啟動新項目。但要**先告知**{n1}你的需求，而不是期待{n1}自己發現。")
    if '顯示生產者' in t1:
        lines.append(f"   → {n1}（{t1}）既能回應又能發起，是群體中的行動引擎。給{n1}具體選項讓薦骨回應後，{n1}會自動帶動執行。")
    if '生產者' in t1 and '顯示' not in t1:
        lines.append(f"   → {n1}（{t1}）需要被問才能啟動。給{n1}具體的「是/否」問題，讓薦骨回應。")
    
    if '顯示者' in t2:
        lines.append(f"   → {n2}（{t2}）有強大的發起力，適合啟動新項目。但要**先告知**{n2}你的需求，而不是期待{n2}自己發現。")
    if '顯示生產者' in t2:
        lines.append(f"   → {n2}（{t2}）既能回應又能發起，是群體中的行動引擎。給{n2}具體選項讓薦骨回應後，{n2}會自動帶動執行。")
    if '生產者' in t2 and '顯示' not in t2:
        lines.append(f"   → {n2}（{t2}）需要被問才能啟動。給{n2}具體的「是/否」問題，讓薦骨回應。")
    
    # 情緒關係
    lines.append(f"\n3️⃣ **情緒關係場景**：")
    emo1 = '情緒' in defined_map[n1]
    emo2 = '情緒' in defined_map[n2]
    if emo1 and not emo2:
        lines.append(f"   → {n1} 有情緒定義，能為{n2}提供情緒的節奏和清晰度。{n2}不要把{n1}的情緒波當成「不穩定」，那是{n1}的決策過程。{n2}在情緒上開放，容易被{n1}的情緒帶著走，要學會這是{n1}的，不一定是自己的。")
    elif emo2 and not emo1:
        lines.append(f"   → {n2} 有情緒定義，能為{n1}提供情緒的節奏和清晰度。{n1}不要把{n2}的情緒波當成「不穩定」，那是{n2}的決策過程。{n1}在情緒上開放，容易被{n2}的情緒帶著走，要學會這是{n2}的，不一定是自己的。")
    elif emo1 and emo2:
        lines.append(f"   → 兩人都有情緒定義，能理解彼此的情緒波。但兩人同時情緒化時，需要有人先冷靜下來。你們的情緒週期可能不同步，要給彼此空間。")
    else:
        lines.append(f"   → 兩人情緒都開放，容易互相放大對方的情緒。相處時保持覺察：「這是我的情緒，還是我從對方那裡吸收來的？」")
    
    # 決策判斷
    lines.append(f"\n4️⃣ **決策判斷場景**：")
    if '薦骨' in a1 and '情緒' in a2:
        lines.append(f"   → {n1}（薦骨權威）用身體回應「是/否」，當下就能決定。{n2}（情緒權威）需要時間讓情緒波沉澱。{n1}不要逼{n2}當下決定；{n2}不要質疑{n1}「為什麼這麼快決定」。")
    elif '情緒' in a1 and '薦骨' in a2:
        lines.append(f"   → {n2}（薦骨權威）用身體回應「是/否」，當下就能決定。{n1}（情緒權威）需要時間讓情緒波沉澱。{n2}不要逼{n1}當下決定；{n1}不要質疑{n2}「為什麼這麼快決定」。")
    elif a1 == a2:
        lines.append(f"   → 兩人都是{a1}，決策語言相同，容易理解彼此的決策過程。")
    else:
        lines.append(f"   → {n1}（{a1}）與{n2}（{a2}）決策方式不同，尊重彼此的節奏，不要用自己的標準要求對方。")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return '\n'.join(lines)


def analyze_group_overall(members, defined_map, undefined_map):
    """群體整體分析"""
    lines = []
    lines.append("## 三、群體整體能量地圖\n")
    
    # 八字五行
    wuxing_count = {}
    for m in members:
        e = STEM_INFO[m['bazi']['day_master']][0]
        wuxing_count[e] = wuxing_count.get(e, 0) + 1
    lines.append("### 📿 八字五行分布\n")
    for e in ['木', '火', '土', '金', '水']:
        count = wuxing_count.get(e, 0)
        bar = '█' * count + '░' * (max(4 - count, 0))
        lines.append(f"{e}：{bar} {count}人")
    lines.append("")
    
    # 占星元素
    astro_elem = {'火': 0, '土': 0, '風': 0, '水': 0}
    for m in members:
        elem = SIGN_ELEMENT.get(m['astrology']['太陽']['sign'], '')
        if elem:
            astro_elem[elem] = astro_elem.get(elem, 0) + 1
    lines.append("### 🔮 太陽星座元素分布\n")
    for e in ['火', '土', '風', '水']:
        count = astro_elem.get(e, 0)
        bar = '█' * count + '░' * (max(4 - count, 0))
        lines.append(f"{e}象：{bar} {count}人")
    lines.append("")
    
    # HD 類型
    lines.append("### 🌀 人類圖類型分布\n")
    type_count = {}
    for m in members:
        t = m['humandesign']['energy_type']
        type_count[t] = type_count.get(t, 0) + 1
    for t, c in type_count.items():
        lines.append(f"- {t}：{c}人")
    lines.append("")
    
    # 定義中心覆蓋
    all_defined = set()
    for m in members:
        all_defined |= defined_map[m['name']]
    missing = set(ALL_CENTERS) - all_defined
    lines.append("### 🌀 定義中心覆蓋率\n")
    lines.append(f"✅ 群體覆蓋：{', '.join(sorted(all_defined)) if all_defined else '無'}")
    if missing:
        lines.append(f"⚠️ 群體缺失：{', '.join(sorted(missing))} → 在這些領域群體都容易受外部影響")
    else:
        lines.append(f"✨ **九個中心全部覆蓋！** 這是一個能量完整的組合，每個領域都有人穩定支持。")
    lines.append("")
    
    # 能量錨點
    most_def = max(members, key=lambda m: len(defined_map[m['name']]))
    least_def = min(members, key=lambda m: len(defined_map[m['name']]))
    lines.append("### 🌀 能量角色分工\n")
    lines.append(f"🎯 **能量錨點**：{most_def['name']}（{len(defined_map[most_def['name']])}個定義中心）")
    lines.append(f"> 當群體混亂時，以{most_def['name']}的穩定能量為基準。定義中心：{', '.join(sorted(defined_map[most_def['name']]))}")
    lines.append("")
    lines.append(f"🛡️ **最需要被保護**：{least_def['name']}（{len(defined_map[least_def['name']])}個定義中心）")
    lines.append(f"> 這個人最容易受群體能量影響。在高壓、混亂時需要有意識地給予空間。")
    lines.append("")
    
    # 互動守則
    lines.append("### 🌀 人類圖類型互動守則\n")
    for m in members:
        n = m['name']
        t = m['humandesign']['energy_type']
        a = m['humandesign']['authority']
        s = m['humandesign']['strategy']
        if t == '生產者':
            lines.append(f"**{n}（生產者·{a}）**：策略「{s}」· 給具體選項讓薦骨用「嗯/唔」回應，不要問開放式問題。")
        elif t == '顯示生產者':
            lines.append(f"**{n}（顯示生產者·{a}）**：策略「{s}」· 讓他們先回應，再給行動空間。是群體中的行動引擎。")
        elif t == '顯示者':
            lines.append(f"**{n}（顯示者·{a}）**：策略「{s}」· 直接告知「我需要你幫我做X」，不要讓他們猜。")
        elif t == '投射者':
            lines.append(f"**{n}（投射者·{a}）**：策略「{s}」· 永遠先邀請再請求，他們需要被認可。")
        elif t == '反映者':
            lines.append(f"**{n}（反映者·{a}）**：策略「{s}」· 給28天月亮週期做重大決定。")
        lines.append("")
    
    # 權威互動
    lines.append("### 🌀 決策權威互動指南\n")
    authorities = {}
    for m in members:
        a = m['humandesign']['authority']
        authorities.setdefault(a, []).append(m['name'])
    for a, names in authorities.items():
        n = ', '.join(names)
        if '情緒' in a:
            lines.append(f"**{n}（情緒權威）**：重大決定等一晚，讓情緒波沉澱。不要在情緒高點或低點決定。")
        elif '薦骨' in a:
            lines.append(f"**{n}（薦骨權威）**：用「是/否」問題啟動，聽腹部的聲音，不要聽腦袋的理由。")
        elif '直覺' in a:
            lines.append(f"**{n}（直覺權威）**：相信當下的身體覺知，那個「知道」只在當下存在。")
        elif '意志力' in a:
            lines.append(f"**{n}（意志力權威）**：承諾前要清楚自己的意願，不要為了證明自己而答應。")
        elif '自我投射' in a:
            lines.append(f"**{n}（自我投射權威）**：透過說話來釐清自己，聽聽自己說了什麼。")
    lines.append("")
    
    # 集體優勢與課題
    lines.append("## 四、集體優勢與成長課題\n")
    lines.append("### ✅ 集體優勢\n")
    strengths = []
    sacral_count = len([m for m in members if '薦骨' in defined_map[m['name']]])
    if sacral_count >= 2:
        strengths.append(f"- **薦骨能量充足**（{sacral_count}人）：群體有強大的持續行動力與工作能量")
    emo_count = len([m for m in members if '情緒' in defined_map[m['name']]])
    if emo_count >= 2:
        strengths.append(f"- **情緒深度**（{emo_count}人）：群體能理解情感的複雜性，關係有深度")
    g_count = len([m for m in members if 'G中心' in defined_map[m['name']]])
    if g_count >= 1:
        strengths.append(f"- **方向感**（{g_count}人）：有人能為群體提供身份認同與方向指引")
    brain_count = len([m for m in members if '頭腦' in defined_map[m['name']] or '邏輯' in defined_map[m['name']]])
    if brain_count >= 1:
        strengths.append(f"- **思考能力**（{brain_count}人）：有人能提供概念化與分析支持")
    for s in strengths:
        lines.append(s)
    if not strengths:
        lines.append("- 群體能量分布均衡")
    lines.append("")
    
    lines.append("### ⚠️ 成長課題\n")
    if missing:
        lines.append(f"- 群體在 **{', '.join(sorted(missing))}** 上缺乏穩定能量，容易在這些領域受外部影響")
    for center in ALL_CENTERS:
        has_it = any(center in defined_map[m['name']] for m in members)
        if not has_it:
            lines.append(f"- **{center}完全缺失**：群體中沒有人有{center}定義，這是最大盲點")
    if type_count.get('生產者', 0) >= len(members) // 2 + 1:
        lines.append("- **生產者過多**：群體傾向於回應而非發起，需要主動創造回應的機會")
    if not missing and type_count.get('生產者', 0) < len(members) // 2 + 1:
        lines.append("- 群體能量分布均衡，主要課題在於協調不同決策節奏")
    lines.append("")
    
    return '\n'.join(lines)


def generate_full_report(members, group_name):
    lines = [f"# {group_name} · 五系統深度洞察報告（v3 完整版）\n"]
    lines.append("> 基於 **八字十神** + **西洋占星行星** + **紫微斗數命盤** + **二十八宿** + **人類圖（類型·Profile·權威·通道·閘門）**\n")
    
    # 計算定義中心
    defined_map = {}
    undefined_map = {}
    for m in members:
        defined = set(m['humandesign']['defined_centers'])
        defined_map[m['name']] = defined
        undefined_map[m['name']] = set(ALL_CENTERS) - defined
    
    # 第一部分：個人深度檔案
    lines.append("# 第一部分：個人深度檔案\n")
    for m in members:
        lines.append(analyze_person(m))
    
    # 第二部分：兩兩交叉分析
    lines.append("# 第二部分：兩兩深度交叉分析\n")
    lines.append("> 每組關係從五個系統維度分析：如何協助對方在**學習成長**、**工作行動**、**情緒關係**、**決策判斷**四個場景變得更好\n")
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            lines.append(analyze_pair(members[i], members[j], defined_map, undefined_map))
    
    # 第三部分：群體整體
    lines.append("# 第三部分：群體整體能量地圖\n")
    lines.append(analyze_group_overall(members, defined_map, undefined_map))
    
    return '\n'.join(lines)


def main():
    # 組合1
    group1 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('衍徵', '1999-01-04', '00:00', '男'),
        get_data('朋友B', '1999-04-25', '00:00', '女'),
    ]
    md1 = generate_full_report(group1, '韡寧 × 衍徵 × 朋友B')
    with open('group_insight_friends_v3_full.md', 'w', encoding='utf-8') as f:
        f.write(md1)
    print("✓ group_insight_friends_v3_full.md")
    
    # 組合2
    group2 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('爸爸', '1972-01-13', '01:08', '男'),
        get_data('媽媽', '1969-12-01', '02:00', '女'),
        get_data('妹妹', '2002-05-06', '15:00', '女'),
    ]
    md2 = generate_full_report(group2, '韡寧 × 爸爸 × 媽媽 × 妹妹')
    with open('group_insight_family_v3_full.md', 'w', encoding='utf-8') as f:
        f.write(md2)
    print("✓ group_insight_family_v3_full.md")


if __name__ == '__main__':
    main()
