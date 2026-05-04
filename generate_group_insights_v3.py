#!/usr/bin/env python3
"""生成特定群體的五系統深度交叉洞察報告（v3 完整版）"""

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

# 十神關係（以日主為我）
def shishen(day_master, target_stem):
    """計算十神關係"""
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
    if WUXING_CYCLE[ta_elem]['克'] == me_elem:
        return '七殺' if me_yin == ta_yin else '正官'
    return '?'


def bazi_relation_full(dm1, dm2):
    """八字完整關係分析"""
    e1, y1 = STEM_INFO[dm1]
    e2, y2 = STEM_INFO[dm2]
    
    # 日主對日主的關係
    if e1 == e2:
        relation = '比肩' if y1 == y2 else '劫財'
        desc = f"同{e1}，是競爭也是夥伴"
    elif WUXING_CYCLE[e1]['生'] == e2:
        relation = '食神' if y1 == y2 else '傷官'
        desc = f"{dm1}生{dm2}，付出與啟發"
    elif WUXING_CYCLE[e2]['生'] == e1:
        relation = '偏印' if y1 == y2 else '正印'
        desc = f"{dm2}生{dm1}，滋養與支持"
    elif WUXING_CYCLE[e1]['克'] == e2:
        relation = '偏財' if y1 == y2 else '正財'
        desc = f"{dm1}剋{dm2}，掌控與管理"
    else:
        relation = '七殺' if y1 == y2 else '正官'
        desc = f"{dm2}剋{dm1}，約束與挑戰"
    
    return relation, desc


# 二十八宿動物
XXIU_ANIMAL = {
    '角': '蛟', '亢': '龍', '氐': '貉', '房': '兔', '心': '狐', '尾': '虎', '箕': '豹',
    '斗': '獬', '牛': '牛', '女': '蝠', '虛': '鼠', '危': '燕', '室': '豬', '壁': '獝',
    '奎': '狼', '婁': '狗', '胃': '雞', '昴': '烏', '畢': '猴', '觜': '猿', '參': '虎',
    '井': '犴', '鬼': '羊', '柳': '獐', '星': '馬', '張': '鹿', '翼': '蛇', '軫': '蚓'
}

# 二十八宿五行
XXIU_WUXING = {
    '角': '木', '亢': '金', '氐': '土', '房': '火', '心': '火', '尾': '火', '箕': '水',
    '斗': '木', '牛': '金', '女': '土', '虛': '火', '危': '火', '室': '火', '壁': '水',
    '奎': '木', '婁': '金', '胃': '土', '昴': '火', '畢': '火', '觜': '火', '參': '水',
    '井': '木', '鬼': '金', '柳': '土', '星': '火', '張': '火', '翼': '火', '軫': '水'
}

# 星宿關係（簡化版）
def xingxiu_relation_detail(x1, x2):
    """詳細星宿關係"""
    wx1, wx2 = XXIU_WUXING.get(x1, ''), XXIU_WUXING.get(x2, '')
    if not wx1 or not wx2:
        return "未知", ""
    
    if wx1 == wx2:
        return f"同氣（同{wx1}）", "氣場相近，容易理解但盲點疊加"
    if WUXING_CYCLE[wx1]['生'] == wx2:
        return f"相生（{wx1}生{wx2}）", f"{x1}對{x2}有生助之力，天然互助"
    if WUXING_CYCLE[wx2]['生'] == wx1:
        return f"相生（{wx2}生{wx1}）", f"{x2}對{x1}有生助之力，天然互助"
    if WUXING_CYCLE[wx1]['克'] == wx2:
        return f"相剋（{wx1}剋{wx2}）", f"{x1}對{x2}有制約，是磨合也是成長動力"
    return f"相剋（{wx2}剋{wx1}）", f"{x2}對{x1}有制約，是磨合也是成長動力"


# 星座元素
SIGN_ELEMENT = {
    '牡羊': '火', '獅子': '火', '射手': '火',
    '金牛': '土', '處女': '土', '摩羯': '土',
    '雙子': '風', '天秤': '風', '水瓶': '風',
    '巨蟹': '水', '天蠍': '水', '雙魚': '水'
}

# 星座互動
def astro_compat(sign1, sign2):
    """星座元素互動"""
    e1, e2 = SIGN_ELEMENT.get(sign1, ''), SIGN_ELEMENT.get(sign2, '')
    if not e1 or not e2:
        return "", ""
    if e1 == e2:
        return f"同{e1}象", "理解彼此的核心驅動力，但容易在同一個洞裡跌倒"
    # 和諧：火-風、土-水
    harmonious = {('火','風'), ('風','火'), ('土','水'), ('水','土')}
    if (e1, e2) in harmonious:
        return f"{e1}-{e2}和諧", "互補且流暢，一個發起一個回應"
    # 挑戰：火-水、風-土
    challenging = {('火','水'), ('水','火'), ('風','土'), ('土','風')}
    if (e1, e2) in challenging:
        return f"{e1}-{e2}張力", "需要磨合，但張力帶來深度與成長"
    return f"{e1}-{e2}動態", "互相需要但方式不同"


# 紫微斗數命宮主星提取
def get_mingzhu(zw):
    """提取命宮主星"""
    ming = zw.get('命宮', '')
    if not ming or len(ming) < 2:
        return "未知"
    ming_zhi = ming[-1]  # 地支
    zhuxing = zw.get('主星', {})
    stars_in_ming = [s for s, z in zhuxing.items() if z == ming_zhi]
    return '、'.join(stars_in_ming) if stars_in_ming else "未知"


# 人類圖閘門對應中心
GATE_TO_CENTER = {}
for center, gates in {
    '頭腦': list(range(64, 65)) + list(range(61, 62)) + list(range(63, 64)),
    '邏輯': list(range(17, 18)) + list(range(62, 63)) + list(range(23, 24)) + list(range(56, 57)) + list(range(16, 17)) + list(range(11, 12)) + list(range(35, 36)),
    '喉嚨': list(range(8, 9)) + list(range(12, 13)) + list(range(20, 21)) + list(range(31, 32)) + list(range(33, 34)) + list(range(45, 46)) + list(range(56, 57)) + list(range(62, 63)) + list(range(23, 24)) + list(range(35, 36)) + list(range(16, 17)),
    'G中心': list(range(1, 2)) + list(range(2, 3)) + list(range(7, 8)) + list(range(10, 11)) + list(range(13, 14)) + list(range(15, 16)) + list(range(25, 26)),
    '心輪': list(range(21, 22)) + list(range(40, 41)) + list(range(26, 27)) + list(range(51, 52)),
    '情緒': list(range(6, 7)) + list(range(37, 38)) + list(range(22, 23)) + list(range(36, 37)) + list(range(49, 50)) + list(range(55, 56)),
    '薦骨': list(range(3, 4)) + list(range(5, 6)) + list(range(9, 10)) + list(range(29, 30)) + list(range(14, 15)) + list(range(34, 35)) + list(range(27, 28)) + list(range(42, 43)) + list(range(59, 60)),
    '脾/直覺': list(range(48, 49)) + list(range(18, 19)) + list(range(57, 58)) + list(range(28, 29)) + list(range(32, 33)) + list(range(44, 45)) + list(range(50, 51)),
    '根部': list(range(58, 59)) + list(range(38, 39)) + list(range(54, 55)) + list(range(53, 54)) + list(range(60, 61)) + list(range(52, 53)) + list(range(19, 20)) + list(range(39, 40)) + list(range(41, 42)),
}.items():
    for g in gates:
        GATE_TO_CENTER[g] = center

# 補充喉嚨和邏輯的閘門
GATE_TO_CENTER.update({
    8: '喉嚨', 12: '喉嚨', 20: '喉嚨', 31: '喉嚨', 33: '喉嚨', 45: '喉嚨',
    56: '邏輯', 62: '邏輯', 23: '邏輯', 35: '邏輯', 16: '邏輯',
    11: '邏輯',
    64: '頭腦', 61: '頭腦', 63: '頭腦',
    1: 'G中心', 2: 'G中心', 7: 'G中心', 10: 'G中心', 13: 'G中心', 15: 'G中心', 25: 'G中心',
    21: '心輪', 40: '心輪', 26: '心輪', 51: '心輪',
    6: '情緒', 37: '情緒', 22: '情緒', 36: '情緒', 49: '情緒', 55: '情緒',
    3: '薦骨', 5: '薦骨', 9: '薦骨', 29: '薦骨', 14: '薦骨', 34: '薦骨', 27: '薦骨', 42: '薦骨', 59: '薦骨',
    48: '脾/直覺', 18: '脾/直覺', 57: '脾/直覺', 28: '脾/直覺', 32: '脾/直覺', 44: '脾/直覺', 50: '脾/直覺',
    58: '根部', 38: '根部', 54: '根部', 53: '根部', 60: '根部', 52: '根部', 19: '根部', 39: '根部', 41: '根部',
})


def get_hd_gates_summary(hd):
    """獲取人類圖閘門摘要"""
    pg = hd['personality_gates']
    dg = hd['design_gates']
    
    # 找出重複的閘門
    all_gates = set(pg.values()) | set(dg.values())
    
    # 關鍵閘門
    sun_gate = pg.get('太陽', 0)
    moon_gate = pg.get('月亮', 0)
    earth_gate = pg.get('地球', 0)
    nodes = [pg.get('北交點', 0), pg.get('南交點', 0)]
    
    return {
        'sun': sun_gate,
        'moon': moon_gate,
        'earth': earth_gate,
        'nodes': nodes,
        'all': sorted(all_gates),
        'channels': hd['active_channels']
    }


def get_data(name, date, time, gender):
    resp = client.post('/api/analyze', json={'name': name, 'date': date, 'time': time, 'gender': gender, 'location': 'taipei'})
    return resp.get_json()


def analyze_group(members, group_name):
    """分析群體如何互相協助（五系統完整版）"""
    lines = [f"# {group_name} · 五系統深度互相協助指南（v3）\n"]
    lines.append("> 基於 **八字十神生剋** + **西洋占星星座元素** + **紫微斗數命宮主星** + **二十八宿五行關係** + **人類圖定義中心與通道互補**\n")
    
    defined_map = {}
    undefined_map = {}
    hd_gates_map = {}
    
    # ==================== 個人檔案 ====================
    lines.append("## 一、個人五系統完整檔案\n")
    
    for m in members:
        name = m['name']
        hd = m['humandesign']
        bz = m['bazi']
        astro = m['astrology']
        zw = m['ziwei']
        xx = m['xingxiu']
        
        defined = set(hd['defined_centers'])
        undefined = set(ALL_CENTERS) - defined
        defined_map[name] = defined
        undefined_map[name] = undefined
        hd_gates_map[name] = get_hd_gates_summary(hd)
        
        dm = bz['day_master']
        elem, yin = STEM_INFO[dm]
        mingzhu = get_mingzhu(zw)
        sihua = zw.get('四化', {})
        sihua_str = ' · '.join([f"{v}{k}" for k,v in sihua.items()]) if sihua else ""
        
        lines.append(f"### {name}\n")
        lines.append(f"**八字**：{bz['year']} {bz['month']} {bz['day']} {bz['hour']} · 日主 **{dm}**（{elem}·{yin}）")
        lines.append(f"**西洋占星**：☉太陽{astro['太陽']['sign']} · ☽月亮{astro['月亮']['sign']} · ☿水星{astro.get('水星',{}).get('sign','')} · ♀金星{astro.get('金星',{}).get('sign','')} · ♂火星{astro.get('火星',{}).get('sign','')}")
        lines.append(f"**紫微斗數**：命宮{zw.get('命宮','')} · 主星「{mingzhu}」 · 五行局{zw.get('五行局','')} · 身宮{zw.get('身宮','')} · 四化{sihua_str}")
        lines.append(f"**二十八宿**：{xx}宿（{XXIU_ANIMAL.get(xx, '?')}）· 五行{XXIU_WUXING.get(xx, '?')}")
        lines.append(f"**人類圖**：{hd['energy_type']} · Profile {hd['profile']} · 權威{hd['authority']} · 策略「{hd['strategy']}」 · 非自己「{hd.get('not_self','')}」")
        lines.append(f"- 定義中心（穩定能量）：{', '.join(sorted(defined))}")
        lines.append(f"- 未定義中心（開放學習）：{', '.join(sorted(undefined))}")
        lines.append(f"- 通道：{hd['active_channels']}")
        
        # 關鍵閘門
        gs = hd_gates_map[name]
        lines.append(f"- 意識太陽閘門：{gs['sun']} · 意識月亮閘門：{gs['moon']} · 設計太陽閘門：{dg.get('太陽',0) if 'dg' in dir() else hd['design_gates'].get('太陽',0)}")
        lines.append("")
    
    # ==================== 兩兩交叉分析 ====================
    lines.append("## 二、兩兩深度交叉分析\n")
    lines.append("> 每組關係從五個系統維度分析：如何協助對方在**學習成長**、**工作行動**、**情緒關係**、**決策判斷**四個場景變得更好\n")
    
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            p1, p2 = members[i], members[j]
            n1, n2 = p1['name'], p2['name']
            
            dm1 = p1['bazi']['day_master']
            dm2 = p2['bazi']['day_master']
            e1, y1 = STEM_INFO[dm1]
            e2, y2 = STEM_INFO[dm2]
            
            astro1 = p1['astrology']
            astro2 = p2['astrology']
            sun1, sun2 = astro1['太陽']['sign'], astro2['太陽']['sign']
            moon1, moon2 = astro1['月亮']['sign'], astro2['月亮']['sign']
            
            xx1, xx2 = p1['xingxiu'], p2['xingxiu']
            
            hd1 = p1['humandesign']
            hd2 = p2['humandesign']
            
            lines.append(f"### {n1} × {n2}\n")
            
            # ── 八字十神 ──
            rel, desc = bazi_relation_full(dm1, dm2)
            lines.append(f"**📿 八字十神**：{dm1}（{e1}）對 {dm2}（{e2}）→ **{rel}** · {desc}")
            
            # 反向關係
            rel2, desc2 = bazi_relation_full(dm2, dm1)
            lines.append(f"> 反過來：{dm2} 看 {dm1} 為 **{rel2}** · {desc2}")
            lines.append("")
            
            # ── 西洋占星 ──
            se_compat, se_desc = astro_compat(sun1, sun2)
            me_compat, me_desc = astro_compat(moon1, moon2)
            lines.append(f"**🔮 西洋占星**：")
            lines.append(f"- 太陽互動：{sun1} × {sun2} → {se_compat} · {se_desc}")
            lines.append(f"- 月亮互動：{moon1} × {moon2} → {me_compat} · {me_desc}")
            lines.append("")
            
            # ── 紫微斗數 ──
            mz1 = get_mingzhu(p1['ziwei'])
            mz2 = get_mingzhu(p2['ziwei'])
            lines.append(f"**⭐ 紫微斗數**：")
            lines.append(f"- {n1} 命宮主星：{mz1}")
            lines.append(f"- {n2} 命宮主星：{mz2}")
            # 四化互動
            s1 = p1['ziwei'].get('四化', {})
            s2 = p2['ziwei'].get('四化', {})
            if s1 and s2:
                lines.append(f"- {n1} 四化：{s1}")
                lines.append(f"- {n2} 四化：{s2}")
            lines.append("")
            
            # ── 二十八宿 ──
            xx_rel, xx_desc = xingxiu_relation_detail(xx1, xx2)
            lines.append(f"**🌟 二十八宿**：{xx1}（{XXIU_ANIMAL.get(xx1,'?')}·{XXIU_WUXING.get(xx1,'?')}）× {xx2}（{XXIU_ANIMAL.get(xx2,'?')}·{XXIU_WUXING.get(xx2,'?')}）→ **{xx_rel}**")
            lines.append(f"> {xx_desc}")
            lines.append("")
            
            # ── 人類圖互補 ──
            p1_can_give = defined_map[n1] & undefined_map[n2]
            p2_can_give = defined_map[n2] & undefined_map[n1]
            shared = defined_map[n1] & defined_map[n2]
            both_undef = undefined_map[n1] & undefined_map[n2]
            
            lines.append(f"**🌀 人類圖能量互補**：")
            if p1_can_give:
                lines.append(f"- {n1} 可穩定支持 {n2}：{', '.join(sorted(p1_can_give))}")
            if p2_can_give:
                lines.append(f"- {n2} 可穩定支持 {n1}：{', '.join(sorted(p2_can_give))}")
            if shared:
                lines.append(f"- 共同語言：{', '.join(sorted(shared))}（同頻共振）")
            if both_undef:
                lines.append(f"- 共同盲點：{', '.join(sorted(both_undef))}（需外部判斷）")
            lines.append("")
            
            # ── 四場景具體建議 ──
            lines.append(f"**💡 四場景協助策略**：")
            
            t1 = hd1['energy_type']
            t2 = hd2['energy_type']
            a1 = hd1['authority']
            a2 = hd2['authority']
            
            # 學習成長場景
            lines.append(f"1️⃣ **學習成長場景**：")
            if '頭腦' in defined_map[n1] or '邏輯' in defined_map[n1]:
                lines.append(f"   → {n1} 有頭腦/邏輯定義，適合擔任{n2}的知識引導者。")
            elif '頭腦' in defined_map[n2] or '邏輯' in defined_map[n2]:
                lines.append(f"   → {n2} 有頭腦/邏輯定義，適合擔任{n1}的知識引導者。")
            else:
                lines.append(f"   → 兩人頭腦/邏輯都開放，學習時容易一起迷失。建議各自獨立學習後再交流，或引入第三方資源。")
            
            # 工作行動場景
            lines.append(f"2️⃣ **工作行動場景**：")
            if '顯示生產者' in t1 or '顯示者' in t1:
                lines.append(f"   → {n1}（{t1}）有發起力，適合啟動項目；{n2}（{t2}）在回應後跟進執行。")
            elif '顯示生產者' in t2 or '顯示者' in t2:
                lines.append(f"   → {n2}（{t2}）有發起力，適合啟動項目；{n1}（{t1}）在回應後跟進執行。")
            elif t1 == t2 == '生產者':
                lines.append(f"   → 兩人都是生產者，適合並肩作戰。但需確保問題明確，讓薦骨有正確的回應對象。")
            
            # 情緒關係場景
            lines.append(f"3️⃣ **情緒關係場景**：")
            if '情緒' in defined_map[n1] and '情緒' not in defined_map[n2]:
                lines.append(f"   → {n1} 有情緒定義，能為{n2}提供情緒節奏和清晰度；{n2}不要急著在{n1}情緒高點做決定。")
            elif '情緒' in defined_map[n2] and '情緒' not in defined_map[n1]:
                lines.append(f"   → {n2} 有情緒定義，能為{n1}提供情緒節奏和清晰度；{n1}不要急著在{n2}情緒高點做決定。")
            elif '情緒' in shared:
                lines.append(f"   → 兩人都有情緒定義，能理解彼此的情緒波。但同時情緒化時，需要有人冷靜下來。")
            else:
                lines.append(f"   → 兩人情緒都開放，容易互相放大情緒。相處時保持覺察，不要讓對方的情緒變成自己的。")
            
            # 決策判斷場景
            lines.append(f"4️⃣ **決策判斷場景**：")
            if '薦骨' in a1 and '情緒' in a2:
                lines.append(f"   → {n1}（薦骨權威）用身體回應，{n2}（情緒權威）等情緒沉澱。重大決定給{n2}時間，{n1}用「是/否」問題幫{n2}釐清。")
            elif '情緒' in a1 and '薦骨' in a2:
                lines.append(f"   → {n2}（薦骨權威）用身體回應，{n1}（情緒權威）等情緒沉澱。重大決定給{n1}時間，{n2}用「是/否」問題幫{n1}釐清。")
            elif a1 == a2:
                lines.append(f"   → 兩人都是{a1}，決策語言相同，容易理解彼此的決策過程。")
            else:
                lines.append(f"   → {n1}（{a1}）與{n2}（{a2}）決策方式不同，尊重彼此的節奏，不要用自己的標準要求對方。")
            
            lines.append("")
            lines.append("---")
            lines.append("")
    
    # ==================== 群體整體策略 ====================
    lines.append("## 三、群體整體能量地圖與協作策略\n")
    
    # 八字五行分布
    wuxing_count = {}
    for m in members:
        e = STEM_INFO[m['bazi']['day_master']][0]
        wuxing_count[e] = wuxing_count.get(e, 0) + 1
    
    lines.append("### 八字五行分布\n")
    for e in ['木', '火', '土', '金', '水']:
        count = wuxing_count.get(e, 0)
        bar = '█' * count + '░' * (4 - count)
        lines.append(f"{e}：{bar} {count}人")
    lines.append("")
    
    # 占星元素分布
    astro_elem_count = {'火': 0, '土': 0, '風': 0, '水': 0}
    for m in members:
        sign = m['astrology']['太陽']['sign']
        elem = SIGN_ELEMENT.get(sign, '')
        if elem:
            astro_elem_count[elem] = astro_elem_count.get(elem, 0) + 1
    
    lines.append("### 西洋占星太陽元素分布\n")
    for e in ['火', '土', '風', '水']:
        count = astro_elem_count.get(e, 0)
        bar = '█' * count + '░' * (4 - count)
        lines.append(f"{e}象：{bar} {count}人")
    lines.append("")
    
    # 人類圖類型分布
    lines.append("### 人類圖能量類型分布\n")
    type_count = {}
    for m in members:
        t = m['humandesign']['energy_type']
        type_count[t] = type_count.get(t, 0) + 1
    for t, count in type_count.items():
        lines.append(f"- {t}：{count}人")
    lines.append("")
    
    # 定義中心覆蓋率
    all_defined = set()
    for m in members:
        all_defined |= defined_map[m['name']]
    missing = set(ALL_CENTERS) - all_defined
    lines.append("### 群體定義中心覆蓋率\n")
    lines.append(f"✅ 群體共同覆蓋：{', '.join(sorted(all_defined)) if all_defined else '無'}")
    if missing:
        lines.append(f"⚠️ 群體缺失：{', '.join(sorted(missing))} → 在這些領域群體都容易受外部影響")
    else:
        lines.append(f"✨ 群體九個中心全部覆蓋！這是一個能量完整的組合，每個領域都有人穩定支持。")
    lines.append("")
    
    # 能量錨點與脆弱點
    most_defined = max(members, key=lambda m: len(defined_map[m['name']]))
    least_defined = min(members, key=lambda m: len(defined_map[m['name']]))
    
    lines.append("### 能量角色分工\n")
    lines.append(f"🎯 **能量錨點**：{most_defined['name']}（{len(defined_map[most_defined['name']])}個定義中心）")
    lines.append(f"> 當群體混亂時，以這個人的穩定能量為基準。{most_defined['name']}的定義中心是：{', '.join(sorted(defined_map[most_defined['name']]))}")
    lines.append("")
    lines.append(f"🛡️ **最需要被保護**：{least_defined['name']}（{len(defined_map[least_defined['name']])}個定義中心）")
    lines.append(f"> 這個人最容易受群體能量影響。在情緒高壓、決策混亂時，需要有意識地給予空間。")
    lines.append("")
    
    # 各類型互動守則
    lines.append("### 人類圖類型互動守則\n")
    for m in members:
        t = m['humandesign']['energy_type']
        n = m['name']
        a = m['humandesign']['authority']
        s = m['humandesign']['strategy']
        if t == '生產者':
            lines.append(f"**{n}（生產者·{a}）**：")
            lines.append(f"- 策略：{s}")
            lines.append(f"- 互動法則：給具體選項，讓薦骨用「嗯/唔」回應。不要問「你想做什麼」。")
        elif t == '顯示生產者':
            lines.append(f"**{n}（顯示生產者·{a}）**：")
            lines.append(f"- 策略：{s}")
            lines.append(f"- 互動法則：讓他們先回應，再給行動空間。他們是群體中最佳的行動啟動者。")
        elif t == '顯示者':
            lines.append(f"**{n}（顯示者·{a}）**：")
            lines.append(f"- 策略：{s}")
            lines.append(f"- 互動法則：直接告知「我需要你幫我做X」，不要讓他們猜。他們的發起力可以帶動整個群體。")
        elif t == '投射者':
            lines.append(f"**{n}（投射者·{a}）**：")
            lines.append(f"- 策略：{s}")
            lines.append(f"- 互動法則：永遠先邀請再請求。他們需要被認可和看見。")
        elif t == '反映者':
            lines.append(f"**{n}（反映者·{a}）**：")
            lines.append(f"- 策略：{s}")
            lines.append(f"- 互動法則：給他們28天月亮週期做重大決定。他們是群體的鏡子。")
        lines.append("")
    
    # 權威互動
    lines.append("### 決策權威互動指南\n")
    authorities = {}
    for m in members:
        a = m['humandesign']['authority']
        authorities.setdefault(a, []).append(m['name'])
    for a, names in authorities.items():
        n = ', '.join(names)
        if '情緒' in a:
            lines.append(f"**{n}（情緒權威）**：重大決定等一晚，讓情緒波沉澱。不要在情緒高點或低點做決定。")
        elif '薦骨' in a:
            lines.append(f"**{n}（薦骨權威）**：用「是/否」問題啟動，聽腹部的聲音。不要聽腦袋裡的理由。")
        elif '直覺' in a:
            lines.append(f"**{n}（直覺權威）**：相信當下的身體覺知，那個「知道」只在當下存在。")
        elif '意志力' in a:
            lines.append(f"**{n}（意志力權威）**：承諾前要清楚自己的意願，不要為了證明自己而承諾。")
        elif '自我投射' in a:
            lines.append(f"**{n}（自我投射權威）**：透過說話來釐清自己，聽自己說了什麼。")
    lines.append("")
    
    # 總結
    lines.append("## 四、總結：這個群體的集體優勢與成長課題\n")
    
    lines.append("### 集體優勢\n")
    strengths = []
    if len([m for m in members if '薦骨' in defined_map[m['name']]]) >= 2:
        strengths.append("- 薦骨能量充足：群體中有強大的持續行動力與工作能量")
    if len([m for m in members if '情緒' in defined_map[m['name']]]) >= 2:
        strengths.append("- 情緒深度：群體能理解情感的複雜性，關係有深度")
    if len([m for m in members if 'G中心' in defined_map[m['name']]]) >= 1:
        strengths.append("- 方向感：有人能為群體提供身份認同與方向指引")
    if len([m for m in members if '頭腦' in defined_map[m['name']] or '邏輯' in defined_map[m['name']]]) >= 1:
        strengths.append("- 思考能力：有人能提供概念化與分析支持")
    
    for s in strengths:
        lines.append(s)
    lines.append("")
    
    lines.append("### 成長課題\n")
    challenges = []
    if missing:
        challenges.append(f"- 群體在 {', '.join(sorted(missing))} 上缺乏穩定能量，容易在這些領域受外部影響")
    
    # 檢查是否所有人都沒有某個中心
    for center in ALL_CENTERS:
        has_it = any(center in defined_map[m['name']] for m in members)
        if not has_it:
            challenges.append(f"- **{center}完全缺失**：群體中沒有人有{center}定義，這是最大盲點")
    
    # 檢查是否有多數人是同一類型可能產生的盲點
    if type_count.get('生產者', 0) >= len(members) // 2 + 1:
        challenges.append("- 生產者過多：群體傾向於回應而非發起，需要主動創造回應的機會")
    
    for c in challenges:
        lines.append(c)
    if not challenges:
        lines.append("- 群體能量分布均衡，主要課題在於協調不同決策節奏")
    lines.append("")
    
    return '\n'.join(lines)


def main():
    # 組合1：韡寧 × 衍徵 × 朋友B
    group1 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('衍徵', '1999-01-04', '00:00', '男'),
        get_data('朋友B', '1999-04-25', '00:00', '女'),
    ]
    md1 = analyze_group(group1, '韡寧 × 衍徵 × 朋友B')
    with open('group_insight_friends_v3.md', 'w', encoding='utf-8') as f:
        f.write(md1)
    print("✓ group_insight_friends_v3.md")
    
    # 組合2：韡寧 × 爸爸 × 媽媽 × 妹妹
    group2 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('爸爸', '1972-01-13', '01:08', '男'),
        get_data('媽媽', '1969-12-01', '02:00', '女'),
        get_data('妹妹', '2002-05-06', '15:00', '女'),
    ]
    md2 = analyze_group(group2, '韡寧 × 爸爸 × 媽媽 × 妹妹')
    with open('group_insight_family_v3.md', 'w', encoding='utf-8') as f:
        f.write(md2)
    print("✓ group_insight_family_v3.md")


if __name__ == '__main__':
    main()
