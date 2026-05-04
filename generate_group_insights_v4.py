#!/usr/bin/env python3
"""生成特定群體的五系統敘事化洞察報告（v4 故事版）"""

from app import app
client = app.test_client()

ALL_CENTERS = ['頭腦', '邏輯', '喉嚨', 'G中心', '心輪', '情緒', '薦骨', '脾/直覺', '根部']

STEM_INFO = {
    '甲': ('木', '陽'), '乙': ('木', '陰'), '丙': ('火', '陽'), '丁': ('火', '陰'),
    '戊': ('土', '陽'), '己': ('土', '陰'), '庚': ('金', '陽'), '辛': ('金', '陰'),
    '壬': ('水', '陽'), '癸': ('水', '陰')
}

WUXING_CYCLE = {
    '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
    '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
    '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
    '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
    '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'},
}

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

SIGN_ELEMENT = {
    '牡羊': '火', '獅子': '火', '射手': '火',
    '金牛': '土', '處女': '土', '摩羯': '土',
    '雙子': '風', '天秤': '風', '水瓶': '風',
    '巨蟹': '水', '天蠍': '水', '雙魚': '水'
}

# 通道完整含義
CHANNEL_MEANING = {
    (5, 15): "**5-15 韻律通道** — 你體內有一個不可動搖的內在節奏，像潮汐一樣規律。你不能被催促，也無法被拖延，你只會按照自己的時間表運作。這條通道讓你對季節轉換、音樂韻律、生活儀式特別敏感，你是那種「需要自己的節奏」才能發揮的人。",
    (3, 60): "**3-60 突變通道** — 壓力是你的燃料，限制是你的跳板。你總能在最困難的處境中找到突破的方式，經歷混亂後建立新秩序。你的存在本身就帶來變化，雖然過程看起來像是一團糟，但結果往往是創新的。",
    (7, 31): "**7-31 領導力通道（Alpha）** — 你有天生的方向感，能為群體指引前路。但這條通道的關鍵是「被邀請的領導」——當別人來問你、請你帶路時，你的領導力會自然流暢；若是強迫別人聽你的，就會遇到阻力。",
    (10, 34): "**10-34 探索通道** — 做自己，就是你的超能力。你有強大的個人力量，當你忠於自己、不迎合別人時，能量會自然流動。這是「行動中的愛自己」——你不需要任何人的許可，只要做自己，力量就會出現。",
    (10, 57): "**10-57 完美呈現通道** — 你的直覺會指引你的行動。你不需要思考、不需要計畫，身體在當下就知道該怎麼做。這是基於生存本能的優雅，你在危急時刻反而最冷靜、最有美感。",
    (16, 48): "**16-48 深度通道** — 你的才華來自於深度掌握。你不是淺嚐輒止的人，一旦投入就會鑽研到很深。別人看到你的技能時會驚嘆，但他們不知道你在背後花了多少時間沉潛。技能是你的語言，也是你的安全感。",
    (19, 49): "**19-49 敏感通道** — 你對「需求」極其敏感，無論是自己的還是別人的。你有一套內在的原則來判斷誰值得被支持、誰不值得。這讓你成為一個有原則的照顧者，但也可能因為過度敏感而感到被冒犯。",
    (27, 50): "**27-50 養育通道** — 你有教導和照顧的天賦，能將價值觀傳遞給他人。你會滋養別人，但切記也要滋養自己——這條通道的人常常忘了自己也需要被照顧。你是價值觀的守護者。",
    (30, 41): "**30-41 夢想通道** — 你被渴望驅動，想要體驗一切。你有豐富的幻想和渴望，人生對你來說是一連串的體驗。關鍵不是壓抑渴望，而是找到正確的體驗來回應它們——不是每個渴望都需要被滿足，但每個渴望都在告訴你一些事情。",
    (34, 57): "**34-57 力量通道** — 你的力量來自當下的直覺。你不需要計畫，不需要準備，身體在當下就知道該怎麼做。這是生存層面的強大力量，讓你在危機中成為那個「剛好知道怎麼做」的人。",
    (37, 40): "**37-40 家庭/社群通道** — 你在關係中尋求承諾和回報。你願意為社群付出，但也需要感受到公平和回饋。這條通道讓你成為「家庭/團隊」的黏著劑，但也可能因為過度在意「公平」而感到受傷。",
    (47, 64): "**47-64 抽象通道** — 你的頭腦會從困惑中提煉意義。你經歷混亂和壓迫，但最終會理解其中的模式。這是抽象思維的禮物——你不是線性思考的人，而是從碎片中拼出全景的人。",
    (21, 45): "**21-45 金錢/掌控通道** — 你有管理資源和掌控局面的天賦。你知道如何聚集和分配資源，是金錢和物質世界的管理者。這條通道的人天生懂得如何「掌握」——不管是掌握金錢、時間、還是局面。",
    (4, 63): "**4-63 邏輯通道** — 你的頭腦會尋找公式化的解答。你擅長建立邏輯框架，從懷疑中找到確定的答案。你總是在問「為什麼」，然後用結構化的方式回答自己。",
    (35, 36): "**35-36 變革通道** — 你渴望進展，渴望經歷不同的事物。你被危機和變化吸引，因為變化對你來說就是生命力。這條通道讓你成為「體驗的收集者」，但也可能因為不斷尋求新刺激而忽略了深耕。",
}

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


def get_mingzhu(zw):
    ming = zw.get('命宮', '')
    if not ming or len(ming) < 2:
        return "未知"
    ming_zhi = ming[-1]
    zhuxing = zw.get('主星', {})
    stars = [s for s, z in zhuxing.items() if z == ming_zhi]
    return '、'.join(stars) if stars else "未知"


def get_data(name, date, time, gender):
    resp = client.post('/api/analyze', json={'name': name, 'date': date, 'time': time, 'gender': gender, 'location': 'taipei'})
    return resp.get_json()


def portrait(m):
    """個人敘事肖像"""
    lines = []
    name = m['name']
    hd = m['humandesign']
    bz = m['bazi']
    astro = m['astrology']
    zw = m['ziwei']
    xx = m['xingxiu']
    
    dm = bz['day_master']
    elem, yin = STEM_INFO[dm]
    defined = set(hd['defined_centers'])
    undefined = set(ALL_CENTERS) - defined
    pg = hd['personality_gates']
    dg = hd['design_gates']
    all_gates = sorted(set(pg.values()) | set(dg.values()))
    
    # 核心身份敘事
    lines.append(f"## {name} 是誰\n")
    
    # 八字 + 占星 + 紫微 + 星宿 + HD 合成一句話
    sun = astro['太陽']['sign']
    moon = astro['月亮']['sign']
    mingzhu = get_mingzhu(zw)
    
    lines.append(f"> **{name}** 是 **{dm}** 日主（{elem}·{yin}）的 **{sun}** 太陽，")
    lines.append(f"> 內在住著一個 **{moon}** 月亮的情感需求，")
    lines.append(f"> 紫微命宮主星是 **{mingzhu}**，星宿是 **{xx}**（{XXIU_ANIMAL.get(xx)}），")
    lines.append(f"> 人類圖是一個 **{hd['energy_type']} · Profile {hd['profile']} · {hd['authority']}**。")
    lines.append("")
    
    # 這個人的核心故事
    lines.append(f"### 核心故事\n")
    
    if hd['profile'] == '6/2':
        lines.append(f"{name} 是一個被設計來「成為典範」的人，但這條路要先經歷大量的嘗試與犯錯。")
        lines.append(f"在 30 歲之前，{name} 會像一個實驗者，不斷試錯、跌倒、再站起來——這些不是失敗，是素材。")
        lines.append(f"{name} 的身體裡住著一個「不用學就會」的天賦者（2爻），那些天賦不會主動展現，")
        lines.append(f"而是等著被別人「意外發現」，然後召喚 {name} 出來。{name} 不會推銷自己，")
        lines.append(f"但當對的人帶著對的問題來找 {name} 時，薦骨會知道。")
    elif hd['profile'] == '4/6':
        lines.append(f"{name} 是一個「透過人際網絡成為典範」的人。")
        lines.append(f"4爻讓 {name} 天生有人脈和影響力，6爻讓 {name} 從高處觀察人生。")
        lines.append(f"0-30歲是嘗試犯錯期，30-50歲退居觀察，50歲後成為榜樣。")
        lines.append(f"{name} 的挑戰在於：4爻需要人際連結，6爻又想要疏離——這種拉扯會一直存在。")
    elif hd['profile'] == '3/5':
        lines.append(f"{name} 是一個「在錯誤中提煉智慧，又背負著他人期待」的人。")
        lines.append(f"3爻讓 {name} 必須透過嘗試和失敗來學習，沒有捷徑。")
        lines.append(f"5爻讓 {name} 散發一種「可以被投射期待」的光環，別人容易把 {name} 當成救世主。")
        lines.append(f"{name} 的功課是：允許自己犯錯，同時不為別人的期待負責。")
    elif hd['profile'] == '1/4':
        lines.append(f"{name} 是一個「先鑽研，再傳播」的人。")
        lines.append(f"1爻需要打穩基礎、深入研究才能安心；4爻又讓 {name} 天生有人脈網絡會來召喚他。")
        lines.append(f"{name} 適合的路徑是：先成為某個領域的專家，然後透過人際網絡自然傳播。")
        lines.append(f"挑戰是：可能因為覺得準備不足而永遠不開始；或為了維持人際和諧而勉強自己。")
    
    lines.append("")
    
    # 天賦
    lines.append(f"### 天賦與禮物\n")
    
    # 通道
    if hd['active_channels']:
        for ch in hd['active_channels']:
            key = tuple(sorted(ch))
            meaning = CHANNEL_MEANING.get(key, f"通道 {ch[0]}-{ch[1]}")
            lines.append(f"- {meaning}")
    
    # 關鍵閘門主題
    lines.append(f"")
    lines.append(f"**這輩子來體驗的主題**：")
    lines.append(f"- ☉ 意識太陽 **Gate {pg['太陽']}**（{GATE_MEANING.get(pg['太陽'],'')}）：{name} 的核心人生主題")
    lines.append(f"- ☽ 意識月亮 **Gate {pg['月亮']}**（{GATE_MEANING.get(pg['月亮'],'')}）：日常驅動力")
    lines.append(f"- 🜨 地球 **Gate {pg['地球']}**（{GATE_MEANING.get(pg['地球'],'')}）：扎根的方向")
    lines.append(f"- ↗ 北交點 **Gate {pg['北交點']}**（{GATE_MEANING.get(pg['北交點'],'')}）：這輩子要發展的")
    lines.append(f"- ↘ 南交點 **Gate {pg['南交點']}**（{GATE_MEANING.get(pg['南交點'],'')}）：過往帶來的")
    lines.append("")
    
    # 挑戰
    lines.append(f"### 挑戰與功課\n")
    lines.append(f"**非自己主題**：{hd.get('not_self','')} — 當 {name} 偏離自己的策略「{hd['strategy']}」時，會出現的情緒信號。")
    lines.append(f"")
    lines.append(f"**開放中心（容易受影響的領域）**：")
    for c in sorted(undefined):
        desc = {
            '頭腦': '容易覺得「必須想出答案」，被別人的問題壓力帶著走',
            '邏輯': '容易覺得「必須搞清楚」，在別人的概念中迷失',
            '喉嚨': '容易覺得「必須做點什麼/說點什麼」，被別人的行動壓力推著跑',
            'G中心': '容易迷失方向，被別人的身份和愛的標準影響',
            '心輪': '容易過度承諾，為了證明自己而答應太多',
            '情緒': '容易放大別人的情緒，把別人的情緒當成自己的',
            '薦骨': '缺乏持續工作的能量，容易疲憊，需要找到對的回應來啟動',
            '脾/直覺': '容易焦慮，對當下的危險過度敏感或過度忽視',
            '根部': '容易承受不屬於自己的壓力，被別人的急迫感帶著跑',
        }.get(c, '')
        lines.append(f"- **{c}**：{desc}")
    lines.append("")
    
    # 決策方式
    lines.append(f"### 決策方式\n")
    auth = hd['authority']
    if '薦骨' in auth:
        lines.append(f"{name} 的決策器官是**薦骨**——身體會對「是/否」問題發出聲音或感受。")
        lines.append(f"不要問開放式問題（「你想做什麼？」），要給具體選項（「你要A還是B？」）。")
        lines.append(f"聽身體的聲音，而不是腦袋裡的理由。")
    elif '情緒' in auth:
        lines.append(f"{name} 的決策器官是**情緒波**——情緒有高有低，高點和低點都不適合做決定。")
        lines.append(f"重大決定要睡一覺，等情緒沉澱到「清明」的狀態。不要當天決定。")
    lines.append("")
    
    return '\n'.join(lines)


def relationship_story(p1, p2):
    """兩人關係敘事"""
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
    
    defined1 = set(hd1['defined_centers'])
    defined2 = set(hd2['defined_centers'])
    undefined1 = set(ALL_CENTERS) - defined1
    undefined2 = set(ALL_CENTERS) - defined2
    
    # 一句話總結
    lines.append(f"## {n1} × {n2}：這段關係是什麼\n")
    
    # 八字關係敘事
    if dm1 == dm2:
        relation_desc = f"同為 {dm1} 日主，是**比劫**關係"
        relation_story = f"兩個 {e1} 人，氣場相近，可以並肩作戰，但也容易在同一個議題上較勁。"
    elif WUXING_CYCLE[e1]['生'] == e2:
        relation_desc = f"{dm1} 生 {dm2}，是**我生**關係"
        relation_story = f"{n1} 對 {n2} 有付出與啟發的作用，像老師對學生、父母對孩子。{n1} 要小心不要過度消耗自己。"
    elif WUXING_CYCLE[e2]['生'] == e1:
        relation_desc = f"{dm2} 生 {dm1}，是**生我**關係"
        relation_story = f"{n2} 是 {n1} 的滋養方，{n1} 可以向 {n2} 尋求支持與資源。"
    elif WUXING_CYCLE[e1]['克'] == e2:
        relation_desc = f"{dm1} 剋 {dm2}，是**我剋**關係"
        relation_story = f"{n1} 對 {n2} 有自然的影響力，但 {n1} 要尊重 {n2} 的自主性，不要過度掌控。"
    else:
        relation_desc = f"{dm2} 剋 {dm1}，是**剋我**關係"
        relation_story = f"{n2} 對 {n1} 有約束和挑戰的作用，這是壓力也是成長動力。"
    
    lines.append(f"**八字**：{relation_desc}。{relation_story}")
    
    # 星宿關係
    wx1, wx2 = XXIU_WUXING.get(xx1, ''), XXIU_WUXING.get(xx2, '')
    if wx1 == wx2:
        xx_story = f"兩人的星宿同為 {wx1}，氣場相近，容易互相理解。"
    elif WUXING_CYCLE.get(wx1, {}).get('生') == wx2:
        xx_story = f"{n1} 的星宿（{xx1}·{wx1}）生 {n2} 的星宿（{xx2}·{wx2}），{n1} 對 {n2} 有生助之力。"
    elif WUXING_CYCLE.get(wx2, {}).get('生') == wx1:
        xx_story = f"{n2} 的星宿（{xx2}·{wx2}）生 {n1} 的星宿（{xx1}·{wx1}），{n2} 對 {n1} 有生助之力。"
    elif WUXING_CYCLE.get(wx1, {}).get('克') == wx2:
        xx_story = f"{n1} 的星宿（{xx1}·{wx1}）剋 {n2} 的星宿（{xx2}·{wx2}），需要磨合，但磨合帶來成長。"
    else:
        xx_story = f"{n2} 的星宿（{xx2}·{wx2}）剋 {n1} 的星宿（{xx1}·{wx1}），需要磨合，但磨合帶來成長。"
    lines.append(f"**星宿**：{xx_story}")
    
    # 占星敘事
    se1, se2 = SIGN_ELEMENT.get(sun1, ''), SIGN_ELEMENT.get(sun2, '')
    if se1 == se2:
        astro_story = f"兩人的太陽同為 {se1} 象（{sun1} × {sun2}），核心驅動力相似，容易理解彼此，但也容易在同一個盲點上跌倒。"
    elif (se1, se2) in {('火','風'), ('風','火'), ('土','水'), ('水','土')}:
        astro_story = f"{sun1}（{se1}）× {sun2}（{se2}）是互補組合，一個發起、一個回應，流暢自然。"
    else:
        astro_story = f"{sun1}（{se1}）× {sun2}（{se2}）有張力，需要磨合，但張力帶來深度。"
    lines.append(f"**占星**：{astro_story}")
    lines.append("")
    
    # 人類圖互補敘事
    lines.append(f"### 能量互補地圖\n")
    
    p1_gives = defined1 & undefined2
    p2_gives = defined2 & undefined1
    shared = defined1 & defined2
    
    if p1_gives:
        centers = '、'.join(sorted(p1_gives))
        lines.append(f"{n1} 的 **{centers}** 是穩定的，可以為 {n2} 提供這些領域的錨定。")
        lines.append(f"當 {n2} 在這些領域感到混亂時，{n1} 的存在本身就是一種穩定。")
    
    if p2_gives:
        centers = '、'.join(sorted(p2_gives))
        lines.append(f"{n2} 的 **{centers}** 是穩定的，可以為 {n1} 提供這些領域的錨定。")
        lines.append(f"當 {n1} 在這些領域感到混亂時，{n2} 的存在本身就是一種穩定。")
    
    if shared:
        centers = '、'.join(sorted(shared))
        lines.append(f"兩人都有 **{centers}** 的定義 → 這是你們的「共同語言」，不需要解釋就能懂。")
    
    lines.append("")
    
    # 閘門重疊
    pg1 = set(hd1['personality_gates'].values()) | set(hd1['design_gates'].values())
    pg2 = set(hd2['personality_gates'].values()) | set(hd2['design_gates'].values())
    shared_gates = pg1 & pg2
    if shared_gates:
        gates_str = '、'.join([f"Gate {g}（{GATE_MEANING.get(g,'')}）" for g in sorted(shared_gates)])
        lines.append(f"**共同閘門**：{gates_str}")
        lines.append(f"> 這些主題是你們的天然共鳴點，聊起來會有一種「你也懂！」的感覺。")
        lines.append("")
    
    # 四場景劇本
    lines.append(f"### 四個場景的互動劇本\n")
    
    t1, t2 = hd1['energy_type'], hd2['energy_type']
    a1, a2 = hd1['authority'], hd2['authority']
    
    # 場景1：學習成長
    lines.append(f"**📚 學習成長場景**\n")
    brain1 = '頭腦' in defined1 or '邏輯' in defined1
    brain2 = '頭腦' in defined2 or '邏輯' in defined2
    if brain1 and not brain2:
        lines.append(f"{n1} 的頭腦/邏輯是穩定的，適合擔任 {n2} 的知識架構師。")
        lines.append(f"{n2} 學習時容易思緒紛亂，{n1} 可以幫忙建立結構、釐清重點。")
        lines.append(f"**建議**：{n2} 遇到不懂的，先自己摸索一輪，再帶著具體問題去問 {n1}。")
    elif brain2 and not brain1:
        lines.append(f"{n2} 的頭腦/邏輯是穩定的，適合擔任 {n1} 的知識架構師。")
        lines.append(f"{n1} 學習時容易思緒紛亂，{n2} 可以幫忙建立結構、釐清重點。")
        lines.append(f"**建議**：{n1} 遇到不懂的，先自己摸索一輪，再帶著具體問題去問 {n2}。")
    elif brain1 and brain2:
        lines.append(f"兩人都有強大的頭腦/邏輯能量，適合一起腦力激盪。")
        lines.append(f"但要注意不要一起鑽牛角尖——兩個聰明人在一起，可能會把簡單的事情複雜化。")
        lines.append(f"**建議**：設定時間限制，時間到了就停止討論，先行動再說。")
    else:
        lines.append(f"兩人的頭腦/邏輯都開放，學習時容易一起迷失在資訊中。")
        lines.append(f"**建議**：各自獨立學習後再交流，或找一個有頭腦/邏輯定義的第三人當顧問。")
    lines.append("")
    
    # 場景2：工作行動
    lines.append(f"**💼 工作行動場景**\n")
    if '顯示者' in t1:
        lines.append(f"{n1}（{t1}）適合**啟動**新項目，但必須**先被告知**需求。不要期待 {n1} 自己發現問題。")
    if '顯示生產者' in t1:
        lines.append(f"{n1}（{t1}）是行動引擎——給具體選項讓薦骨回應後，{n1} 會自動帶動執行。")
    if '生產者' in t1 and '顯示' not in t1:
        lines.append(f"{n1}（{t1}）需要被問才能啟動。給 {n1} 具體的「是/否」問題，讓薦骨回應。")
    if '顯示者' in t2:
        lines.append(f"{n2}（{t2}）適合**啟動**新項目，但必須**先被告知**需求。不要期待 {n2} 自己發現問題。")
    if '顯示生產者' in t2:
        lines.append(f"{n2}（{t2}）是行動引擎——給具體選項讓薦骨回應後，{n2} 會自動帶動執行。")
    if '生產者' in t2 and '顯示' not in t2:
        lines.append(f"{n2}（{t2}）需要被問才能啟動。給 {n2} 具體的「是/否」問題，讓薦骨回應。")
    lines.append("")
    
    # 場景3：情緒關係
    lines.append(f"**❤️ 情緒關係場景**\n")
    emo1 = '情緒' in defined1
    emo2 = '情緒' in defined2
    if emo1 and not emo2:
        lines.append(f"{n1} 的情緒是穩定的，有自然的節奏和清晰度。{n2} 的情緒是開放的，容易吸收 {n1} 的情緒。")
        lines.append(f"{n2} 要記得：{n1} 的情緒波是 {n1} 的，不一定是你的。當 {n1} 情緒高漲或低落時，不要跟著一起起伏。")
        lines.append(f"**建議**：{n1} 做重大情緒決定時，給自己時間沉澱；{n2} 學會「這是 {n1} 的情緒，我觀察但不認同」。")
    elif emo2 and not emo1:
        lines.append(f"{n2} 的情緒是穩定的，有自然的節奏和清晰度。{n1} 的情緒是開放的，容易吸收 {n2} 的情緒。")
        lines.append(f"{n1} 要記得：{n2} 的情緒波是 {n2} 的，不一定是你的。當 {n2} 情緒高漲或低落時，不要跟著一起起伏。")
        lines.append(f"**建議**：{n2} 做重大情緒決定時，給自己時間沉澱；{n1} 學會「這是 {n2} 的情緒，我觀察但不認同」。")
    elif emo1 and emo2:
        lines.append(f"兩人都有情緒定義，能理解彼此的情緒波。這是禮物也是挑戰——")
        lines.append(f"當兩人同時情緒化時，沒有人能當冷靜的那個。")
        lines.append(f"**建議**：約定一個「情緒暫停詞」，當兩人都高漲時，先各自冷靜，再回來溝通。")
    else:
        lines.append(f"兩人的情緒都開放，容易互相放大對方的情緒。")
        lines.append(f"**建議**：相處時保持覺察——「這是我的情緒，還是我從對方那裡吸收來的？」")
    lines.append("")
    
    # 場景4：決策判斷
    lines.append(f"**🎯 決策判斷場景**\n")
    if '薦骨' in a1 and '情緒' in a2:
        lines.append(f"{n1}（薦骨權威）當下就能決定，{n2}（情緒權威）需要時間。")
        lines.append(f"{n1} 不要逼 {n2} 當下決定；{n2} 不要質疑 {n1}「為什麼這麼快」。")
        lines.append(f"**建議**：重大決定由 {n2} 主導節奏，{n1} 用「是/否」問題幫 {n2} 釐清。")
    elif '情緒' in a1 and '薦骨' in a2:
        lines.append(f"{n2}（薦骨權威）當下就能決定，{n1}（情緒權威）需要時間。")
        lines.append(f"{n2} 不要逼 {n1} 當下決定；{n1} 不要質疑 {n2}「為什麼這麼快」。")
        lines.append(f"**建議**：重大決定由 {n1} 主導節奏，{n2} 用「是/否」問題幫 {n1} 釐清。")
    elif a1 == a2:
        lines.append(f"兩人都是 {a1}，決策語言相同，容易理解彼此。")
        lines.append(f"**建議**：一起決定時，用你們共同熟悉的語言——{'「是/否」問題' if '薦骨' in a1 else '等情緒沉澱'}。")
    else:
        lines.append(f"{n1}（{a1}）與 {n2}（{a2}）決策方式不同。")
        lines.append(f"**建議**：尊重彼此的節奏，不要用自己的標準要求對方。")
    lines.append("")
    
    # 衝突預警
    lines.append(f"### ⚠️ 衝突預警\n")
    both_undef = undefined1 & undefined2
    if both_undef:
        centers = '、'.join(sorted(both_undef))
        lines.append(f"兩人在 **{centers}** 上都沒有穩定能量。")
        lines.append(f"當這些領域出現問題時，兩人容易一起焦慮、一起迷失，沒有人能當錨點。")
        lines.append(f"**應對**：在這些議題上，提前約定「如果我們都亂了，就去找誰問」。")
    else:
        lines.append(f"兩人的盲點不重疊，算是互補的關係。當一方亂了，另一方通常能穩住。")
    lines.append("")
    
    # 最佳協作模式
    lines.append(f"### ✨ 最佳協作模式\n")
    lines.append(f"這段關係最順暢的運作方式是：")
    
    if p1_gives and p2_gives:
        c1 = '、'.join(sorted(p1_gives))
        c2 = '、'.join(sorted(p2_gives))
        lines.append(f"- {n1} 在 **{c1}** 上當穩定者，{n2} 在 **{c2}** 上當穩定者")
    
    if '薦骨' in a1 and '情緒' in a2:
        lines.append(f"- 日常小事：{n1} 快速決定，{n2} 跟隨")
        lines.append(f"- 重大決定：等 {n2} 情緒清明，{n1} 用身體回應確認")
    elif '情緒' in a1 and '薦骨' in a2:
        lines.append(f"- 日常小事：{n2} 快速決定，{n1} 跟隨")
        lines.append(f"- 重大決定：等 {n1} 情緒清明，{n2} 用身體回應確認")
    
    if '顯示者' in t1 or '顯示生產者' in t1:
        lines.append(f"- 行動發起：由 {n1} 啟動，但**先告知** {n1} 你的需求")
    elif '顯示者' in t2 or '顯示生產者' in t2:
        lines.append(f"- 行動發起：由 {n2} 啟動，但**先告知** {n2} 你的需求")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return '\n'.join(lines)


def group_ecology(members):
    """群體生態敘事"""
    lines = []
    
    defined_map = {}
    for m in members:
        defined_map[m['name']] = set(m['humandesign']['defined_centers'])
    
    lines.append("## 這個群體的生態系統\n")
    
    # 群體像什麼
    lines.append(f"### 群體氣場\n")
    
    # 五行分布
    wx_count = {}
    for m in members:
        e = STEM_INFO[m['bazi']['day_master']][0]
        wx_count[e] = wx_count.get(e, 0) + 1
    
    max_wx = max(wx_count, key=wx_count.get) if wx_count else ''
    lines.append(f"這個群體的集體能量偏向 **{max_wx}**（{wx_count.get(max_wx,0)}人）。")
    if max_wx == '火':
        lines.append(f"火為主導的群體：熱情、行動力強、創意豐富，但可能缺乏耐心，容易一起衝動。")
    elif max_wx == '金':
        lines.append(f"金為主導的群體：果斷、有原則、重義氣，但可能過於剛硬，需要柔軟的調和。")
    elif max_wx == '水':
        lines.append(f"水為主導的群體：靈活、智慧、適應力強，但可能缺乏定力，容易一起搖擺。")
    elif max_wx == '木':
        lines.append(f"木為主導的群體：向上生長、有規劃、仁慈，但可能過於理想化。")
    elif max_wx == '土':
        lines.append(f"土為主導的群體：穩重、務實、包容，但可能過於保守，需要火的推動。")
    lines.append("")
    
    # 角色分工
    lines.append(f"### 角色分工\n")
    
    # 能量錨點
    most_def = max(members, key=lambda m: len(defined_map[m['name']]))
    least_def = min(members, key=lambda m: len(defined_map[m['name']]))
    
    lines.append(f"**🎯 穩定錨點：{most_def['name']}**")
    lines.append(f"> {most_def['name']} 有 {len(defined_map[most_def['name']])} 個定義中心（{', '.join(sorted(defined_map[most_def['name']]))}）。")
    lines.append(f"> 當群體混亂時，這個人是天然的穩定器。大家會不自覺地看向 {most_def['name']}。")
    lines.append("")
    
    lines.append(f"**🛡️ 需要被保護：{least_def['name']}**")
    lines.append(f"> {least_def['name']} 只有 {len(defined_map[least_def['name']])} 個定義中心。")
    lines.append(f"> 這個人最容易受群體能量影響，在高壓時需要被有意識地給予空間。")
    lines.append("")
    
    # 誰是什麼角色
    for m in members:
        n = m['name']
        t = m['humandesign']['energy_type']
        a = m['humandesign']['authority']
        if t == '生產者':
            lines.append(f"**{n}：執行者** — 給對的問題，就會產出對的行動。是群體的引擎。")
        elif t == '顯示生產者':
            lines.append(f"**{n}：發起型執行者** — 既能回應又能發起，是群體的行動火車頭。")
        elif t == '顯示者':
            lines.append(f"**{n}：發起者** — 有新點子、能開新局，但需要被告知需求。不要讓 {n} 猜。")
        elif t == '投射者':
            lines.append(f"**{n}：引導者** — 能看到別人看不到的，但需要被邀請才開口。")
    lines.append("")
    
    # 定義中心覆蓋
    all_defined = set()
    for m in members:
        all_defined |= defined_map[m['name']]
    missing = set(ALL_CENTERS) - all_defined
    
    lines.append(f"### 群體能量覆蓋\n")
    if missing:
        lines.append(f"⚠️ 這個群體在 **{', '.join(sorted(missing))}** 上沒有穩定能量。")
        lines.append(f"> 當議題涉及這些領域時，群體容易一起迷失。建議在這些議題上引入外部資源或顧問。")
    else:
        lines.append(f"✨ **九個中心全部覆蓋！**")
        lines.append(f"> 這是一個能量完整的群體，每個領域都有人穩定支持。你們在一起，很少會有「沒有人懂這個」的時刻。")
    lines.append("")
    
    # 決策生態
    lines.append(f"### 群體決策生態\n")
    auth_groups = {}
    for m in members:
        a = m['humandesign']['authority']
        auth_groups.setdefault(a, []).append(m['name'])
    
    for a, names in auth_groups.items():
        n = ', '.join(names)
        if '情緒' in a:
            lines.append(f"- **{n}（{a}）**：重大決定需要等一晚。這 {len(names)} 個人是群體的「剎車」，不要嫌他們慢。")
        elif '薦骨' in a:
            lines.append(f"- **{n}（{a}）**：當下就能決定。這 {len(names)} 個人是群體的「油門」，問對問題就會動。")
    lines.append("")
    
    # 集體優勢與課題
    lines.append(f"### 集體優勢\n")
    if len([m for m in members if '薦骨' in defined_map[m['name']]]) >= 2:
        lines.append(f"- ✅ 持續行動力：群體中有強大的薦骨能量，能長期執行")
    if len([m for m in members if '情緒' in defined_map[m['name']]]) >= 2:
        lines.append(f"- ✅ 情感深度：群體能理解複雜情緒，關係有厚度")
    if len([m for m in members if 'G中心' in defined_map[m['name']]]) >= 1:
        lines.append(f"- ✅ 方向感：有人能提供身份認同與方向指引")
    if len([m for m in members if '頭腦' in defined_map[m['name']] or '邏輯' in defined_map[m['name']]]) >= 1:
        lines.append(f"- ✅ 思考能力：有人能建立概念與分析框架")
    lines.append("")
    
    lines.append(f"### 成長課題\n")
    if missing:
        lines.append(f"- ⚠️ 在 **{', '.join(sorted(missing))}** 上，群體缺乏穩定能量。這是最大盲點。")
    type_count = {}
    for m in members:
        t = m['humandesign']['energy_type']
        type_count[t] = type_count.get(t, 0) + 1
    if type_count.get('生產者', 0) >= len(members) // 2 + 1:
        lines.append(f"- ⚠️ 生產者過多：群體傾向回應而非發起，需要主動創造回應機會")
    if not missing:
        lines.append(f"- 群體能量完整，主要課題在於協調不同決策節奏")
    lines.append("")
    
    return '\n'.join(lines)


def generate_report(members, group_name):
    lines = [f"# {group_name} · 五系統敘事洞察報告（v4）\n"]
    lines.append("> 這不是數據報告，這是關於「你是誰」和「你們在一起會發生什麼」的故事。\n")
    
    lines.append("---\n")
    lines.append("# 上卷：每個人是誰\n")
    for m in members:
        lines.append(portrait(m))
    
    lines.append("---\n")
    lines.append("# 中卷：兩兩關係劇本\n")
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            lines.append(relationship_story(members[i], members[j]))
    
    lines.append("---\n")
    lines.append("# 下卷：群體生態系統\n")
    lines.append(group_ecology(members))
    
    return '\n'.join(lines)


def main():
    group1 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('衍徵', '1999-01-04', '00:00', '男'),
        get_data('朋友B', '1999-04-25', '00:00', '女'),
    ]
    md1 = generate_report(group1, '韡寧 × 衍徵 × 朋友B')
    with open('group_insight_friends_v4.md', 'w', encoding='utf-8') as f:
        f.write(md1)
    print("✓ group_insight_friends_v4.md")
    
    group2 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('爸爸', '1972-01-13', '01:08', '男'),
        get_data('媽媽', '1969-12-01', '02:00', '女'),
        get_data('妹妹', '2002-05-06', '15:00', '女'),
    ]
    md2 = generate_report(group2, '韡寧 × 爸爸 × 媽媽 × 妹妹')
    with open('group_insight_family_v4.md', 'w', encoding='utf-8') as f:
        f.write(md2)
    print("✓ group_insight_family_v4.md")


if __name__ == '__main__':
    main()
