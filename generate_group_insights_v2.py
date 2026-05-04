#!/usr/bin/env python3
"""生成特定群體的五系統交叉洞察報告（v3）"""

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

# 八字日主五行
STEM_ELEMENT = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 五行生克
WUXING_CYCLE = {
    '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
    '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
    '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
    '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
    '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'},
}

# 二十八宿動物關係
XXIU_ANIMAL = {
    '角': '蛟', '亢': '龍', '氐': '貉', '房': '兔', '心': '狐', '尾': '虎', '箕': '豹',
    '斗': '獬', '牛': '牛', '女': '蝠', '虛': '鼠', '危': '燕', '室': '豬', '壁': '獝',
    '奎': '狼', '婁': '狗', '胃': '雞', '昴': '烏', '畢': '猴', '觜': '猿', '參': '虎',
    '井': '犴', '鬼': '羊', '柳': '獐', '星': '馬', '張': '鹿', '翼': '蛇', '軫': '蚓'
}

# 星宿關係（簡化版：根據動物判斷遠近）
def xingxiu_relation(x1, x2):
    """簡化星宿關係判斷"""
    a1, a2 = XXIU_ANIMAL.get(x1, ''), XXIU_ANIMAL.get(x2, '')
    if not a1 or not a2:
        return "未知"
    # 同類（同五行動物群）
    same_group = {
        '木': ['蛟','龍','貉','兔','狐','虎','豹'],
        '火': ['獬','牛','蝠','鼠','燕','豬','獝'],
        '土': ['狼','狗','雞','烏','猴','猿'],
        '金': ['犴','羊','獐','馬','鹿'],
        '水': ['蛇','蚓']
    }
    g1 = next((k for k,v in same_group.items() if a1 in v), '')
    g2 = next((k for k,v in same_group.items() if a2 in v), '')
    if g1 == g2:
        return f"近緣（同{g1}行）"
    # 相生
    if WUXING_CYCLE.get(g1, {}).get('生') == g2:
        return f"相生（{g1}生{g2}）"
    if WUXING_CYCLE.get(g2, {}).get('生') == g1:
        return f"相生（{g2}生{g1}）"
    # 相剋
    if WUXING_CYCLE.get(g1, {}).get('克') == g2:
        return f"相剋（{g1}克{g2}）"
    if WUXING_CYCLE.get(g2, {}).get('克') == g1:
        return f"相剋（{g2}克{g1}）"
    return "中性"


def get_data(name, date, time, gender):
    resp = client.post('/api/analyze', json={'name': name, 'date': date, 'time': time, 'gender': gender, 'location': 'taipei'})
    return resp.get_json()


def bazi_relation(dm1, dm2):
    """八字日主關係"""
    e1, e2 = STEM_ELEMENT[dm1], STEM_ELEMENT[dm2]
    if e1 == e2:
        return f"比劫（同{e1}）"
    if WUXING_CYCLE[e1]['生'] == e2:
        return f"我生（{e1}生{e2}）"
    if WUXING_CYCLE[e2]['生'] == e1:
        return f"生我（{e2}生{e1}）"
    if WUXING_CYCLE[e1]['克'] == e2:
        return f"我剋（{e1}剋{e2}）"
    if WUXING_CYCLE[e2]['克'] == e1:
        return f"剋我（{e2}剋{e1}）"
    return "?"


def zw_summary(zw):
    """紫微簡要摘要"""
    main = zw.get('主星', '')
    pattern = zw.get('格局', '')
    ming = zw.get('命宮', '')
    sihua = zw.get('四化', '')
    return f"主星{main} · 命宮{ming} · 四化{sihua}"


def analyze_group(members, group_name):
    """分析群體如何互相協助（五系統）"""
    lines = [f"# {group_name} · 五系統互相協助指南（v3）\n"]
    lines.append("> 基於 **人類圖定義中心互補** + **八字五行生剋** + **西洋占星星座互動** + **紫微主星特質** + **二十八宿關係**\n")
    
    # 每個人的五系統摘要
    defined_map = {}
    undefined_map = {}
    
    lines.append("## 個人五系統檔案\n")
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
        
        lines.append(f"### {name}\n")
        lines.append(f"**八字**：{bz['year']}{bz['month']}{bz['day']}{bz['hour']} · 日主 **{bz['day_master']}**（{STEM_ELEMENT[bz['day_master']]}）")
        lines.append(f"**西洋占星**：太陽{astro['太陽']['sign']} · 月亮{astro['月亮']['sign']}")
        lines.append(f"**紫微斗數**：主星{zw.get('主星','?')} · 命宮{zw.get('命宮','?')} · 四化{zw.get('四化','?')}")
        lines.append(f"**二十八宿**：{xx}（{XXIU_ANIMAL.get(xx, '?')}）")
        lines.append(f"**人類圖**：{hd['energy_type']} · Profile {hd['profile']} · 權威{hd['authority']}")
        lines.append(f"- 定義中心：{', '.join(sorted(defined))}")
        lines.append(f"- 未定義中心：{', '.join(sorted(undefined))}")
        lines.append("")
    
    # 兩兩交叉分析
    lines.append("## 兩兩交叉分析：如何協助對方變得更好\n")
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            p1, p2 = members[i], members[j]
            n1, n2 = p1['name'], p2['name']
            
            dm1 = p1['bazi']['day_master']
            dm2 = p2['bazi']['day_master']
            e1 = STEM_ELEMENT[dm1]
            e2 = STEM_ELEMENT[dm2]
            
            astro1 = p1['astrology']
            astro2 = p2['astrology']
            sun1, sun2 = astro1['太陽']['sign'], astro2['太陽']['sign']
            moon1, moon2 = astro1['月亮']['sign'], astro2['月亮']['sign']
            
            xx1, xx2 = p1['xingxiu'], p2['xingxiu']
            
            lines.append(f"### {n1} × {n2}\n")
            
            # 1. 八字關係
            bz_rel = bazi_relation(dm1, dm2)
            lines.append(f"**八字日主關係**：{dm1}（{e1}）× {dm2}（{e2}）→ **{bz_rel}**")
            if '生我' in bz_rel:
                lines.append(f"> 💡 {n2} 是 {n1} 的貴人/資源方，{n1} 可以向 {n2} 尋求支持與滋養。")
            elif '我生' in bz_rel:
                lines.append(f"> 💡 {n1} 是 {n2} 的付出方，{n1} 對 {n2} 有創造/啟發的作用，但要注意不要過度消耗。")
            elif '比劫' in bz_rel:
                lines.append(f"> 💡 兩人同五行，是競爭也是夥伴關係。可以並肩作戰，但要避免互相較勁。")
            elif '剋我' in bz_rel:
                lines.append(f"> 💡 {n2} 對 {n1} 有約束/挑戰作用，這是壓力也是成長動力。")
            elif '我剋' in bz_rel:
                lines.append(f"> 💡 {n1} 對 {n2} 有掌控/管理的傾向，要尊重對方的自主性。")
            lines.append("")
            
            # 2. 星宿關係
            xx_rel = xingxiu_relation(xx1, xx2)
            lines.append(f"**二十八宿關係**：{xx1}（{XXIU_ANIMAL.get(xx1,'?')}）× {xx2}（{XXIU_ANIMAL.get(xx2,'?')}）→ **{xx_rel}**")
            if '相生' in xx_rel:
                lines.append(f"> 🌟 星宿相生，兩人天然有互助能量，在一起容易互相提升運勢。")
            elif '相剋' in xx_rel:
                lines.append(f"> ⚡ 星宿相剋，需要磨合。但相剋也代表互相刺激成長，關鍵在於轉化為建設性張力。")
            elif '近緣' in xx_rel:
                lines.append(f"> 🤝 星宿同類，氣場相近，容易互相理解，但也要注意盲點疊加。")
            lines.append("")
            
            # 3. 人類圖互補
            p1_can_give = defined_map[n1] & undefined_map[n2]
            p2_can_give = defined_map[n2] & undefined_map[n1]
            shared = defined_map[n1] & defined_map[n2]
            both_undef = undefined_map[n1] & undefined_map[n2]
            
            if p1_can_give:
                lines.append(f"**{n1} 的穩定能量可支持 {n2}**：")
                for c in sorted(p1_can_give):
                    lines.append(f"- {c}：{CENTER_HUMAN_DESIGN[c]}")
                lines.append("")
            
            if p2_can_give:
                lines.append(f"**{n2} 的穩定能量可支持 {n1}**：")
                for c in sorted(p2_can_give):
                    lines.append(f"- {c}：{CENTER_HUMAN_DESIGN[c]}")
                lines.append("")
            
            if shared:
                lines.append(f"**共同語言**：{', '.join(sorted(shared))} → 同頻共振區")
            if both_undef:
                lines.append(f"**共同盲點**：{', '.join(sorted(both_undef))} → 需要外部或獨立判斷")
            lines.append("")
            
            # 4. 綜合建議
            lines.append(f"**綜合協助策略**：")
            
            # 基於HD類型
            t1 = p1['humandesign']['energy_type']
            t2 = p2['humandesign']['energy_type']
            a1 = p1['humandesign']['authority']
            a2 = p2['humandesign']['authority']
            
            strategy_lines = []
            
            # 類型互動
            if '顯示者' in t1 and '生產者' in t2:
                strategy_lines.append(f"- {n1}（顯示者）需要被告知，{n2}（生產者）可以用具體問題讓{n1}的薦骨回應。但{n1}的行動力可以帶動{n2}啟動。")
            elif '生產者' in t1 and '顯示者' in t2:
                strategy_lines.append(f"- {n2}（顯示者）需要被告知，{n1}（生產者）可以用具體問題讓{n2}的薦骨回應。但{n2}的行動力可以帶動{n1}啟動。")
            
            if '顯示生產者' in t1:
                strategy_lines.append(f"- {n1}（顯示生產者）有發起力也有回應力，是群體中最佳的行動啟動者。")
            if '顯示生產者' in t2:
                strategy_lines.append(f"- {n2}（顯示生產者）有發起力也有回應力，是群體中最佳的行動啟動者。")
            
            # 權威互動
            if '情緒' in a1 and '薦骨' in a2:
                strategy_lines.append(f"- {n1}（情緒權威）決策需要時間沉澱，{n2}（薦骨權威）不要逼{n1}當下決定；{n2}的回應可以幫{n1}釐清真實感受。")
            elif '薦骨' in a1 and '情緒' in a2:
                strategy_lines.append(f"- {n2}（情緒權威）決策需要時間沉澱，{n1}（薦骨權威）不要逼{n2}當下決定；{n1}的回應可以幫{n2}釐清真實感受。")
            
            for sl in strategy_lines:
                lines.append(sl)
            if not strategy_lines:
                lines.append(f"- 兩人都是{t1 if t1==t2 else t1+'/'+t2}，天然容易理解彼此的能量語言。")
            
            lines.append("")
            lines.append("---")
            lines.append("")
    
    # 群體整體策略
    lines.append("## 群體整體協作策略\n")
    
    # 五行分布
    wuxing_count = {}
    for m in members:
        e = STEM_ELEMENT[m['bazi']['day_master']]
        wuxing_count[e] = wuxing_count.get(e, 0) + 1
    lines.append(f"**八字五行分布**：{' / '.join([f'{k}{v}人' for k,v in wuxing_count.items()])}")
    
    # 最多/最少
    max_wx = max(wuxing_count, key=wuxing_count.get)
    min_wx = min(wuxing_count, key=wuxing_count.get)
    lines.append(f"- 群體最強能量：{max_wx}（{wuxing_count[max_wx]}人）→ 這是群體的集體優勢領域")
    if max_wx != min_wx:
        lines.append(f"- 群體最弱能量：{min_wx}（{wuxing_count[min_wx]}人）→ 這是群體需要外部補充的領域")
    lines.append("")
    
    # HD 能量錨點
    most_defined = max(members, key=lambda m: len(defined_map[m['name']]))
    least_defined = min(members, key=lambda m: len(defined_map[m['name']]))
    lines.append(f"**人類圖能量錨點**：{most_defined['name']}（{len(defined_map[most_defined['name']])}個定義中心）→ 群體混亂時以此人為穩定基準")
    lines.append(f"**最需要被支持的**：{least_defined['name']}（{len(defined_map[least_defined['name']])}個定義中心）→ 最容易受群體能量影響")
    lines.append("")
    
    # 各類型策略
    types = {}
    for m in members:
        t = m['humandesign']['energy_type']
        types.setdefault(t, []).append(m['name'])
    
    lines.append("**人類圖能量類型互動守則**：")
    for t, names in types.items():
        n = ', '.join(names)
        if t == '生產者':
            lines.append(f"- **{n}（生產者）**：給具體選項讓薦骨回應，不要問「你想做什麼」。")
        elif t == '顯示生產者':
            lines.append(f"- **{n}（顯示生產者）**：讓他們先回應，再給行動空間。既有回應力又有發起力。")
        elif t == '顯示者':
            lines.append(f"- **{n}（顯示者）**：直接告知「我需要你幫我做X」，不要讓他們猜。")
        elif t == '投射者':
            lines.append(f"- **{n}（投射者）**：永遠先邀請再請求，他們需要被認可。")
    lines.append("")
    
    # 權威
    authorities = {}
    for m in members:
        a = m['humandesign']['authority']
        authorities.setdefault(a, []).append(m['name'])
    
    lines.append("**決策權威互動**：")
    for a, names in authorities.items():
        n = ', '.join(names)
        if '情緒' in a:
            lines.append(f"- **{n}（情緒權威）**：重大決定等一晚，讓情緒波沉澱。")
        elif '薦骨' in a:
            lines.append(f"- **{n}（薦骨權威）**：用「是/否」問題啟動，聽腹部的聲音。")
    lines.append("")
    
    return '\n'.join(lines)


def main():
    # 組合1
    group1 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('衍徵', '1999-01-04', '00:00', '男'),
        get_data('朋友B', '1999-04-25', '00:00', '女'),
    ]
    md1 = analyze_group(group1, '韡寧 × 衍徵 × 朋友B')
    with open('group_insight_friends_v2.md', 'w', encoding='utf-8') as f:
        f.write(md1)
    print("✓ group_insight_friends_v2.md")
    
    # 組合2
    group2 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('爸爸', '1972-01-13', '01:08', '男'),
        get_data('媽媽', '1969-12-01', '02:00', '女'),
        get_data('妹妹', '2002-05-06', '15:00', '女'),
    ]
    md2 = analyze_group(group2, '韡寧 × 爸爸 × 媽媽 × 妹妹')
    with open('group_insight_family_v2.md', 'w', encoding='utf-8') as f:
        f.write(md2)
    print("✓ group_insight_family_v2.md")


if __name__ == '__main__':
    main()
