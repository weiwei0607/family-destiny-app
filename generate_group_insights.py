#!/usr/bin/env python3
"""生成特定群體的「如何協助他人變得更好」深度分析"""

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


def get_data(name, date, time, gender):
    resp = client.post('/api/analyze', json={'name': name, 'date': date, 'time': time, 'gender': gender, 'location': 'taipei'})
    return resp.get_json()


def analyze_group(members, group_name):
    """分析群體如何互相協助"""
    lines = [f"# {group_name} · 互相協助指南（v3）\n"]
    lines.append("> 基於人類圖定義中心互補 + 八字五行關係 + 星宿互動\n")
    
    # 每個人的定義/未定義
    defined_map = {}
    undefined_map = {}
    for m in members:
        defined = set(m['humandesign']['defined_centers'])
        undefined = set(ALL_CENTERS) - defined
        defined_map[m['name']] = defined
        undefined_map[m['name']] = undefined
    
    # 組合定義中心
    all_defined = set()
    for m in members:
        all_defined |= defined_map[m['name']]
    
    lines.append("## 群體能量地圖\n")
    lines.append(f"**群體共同定義中心**：{', '.join(sorted(all_defined)) if all_defined else '無'}\n")
    
    for m in members:
        name = m['name']
        hd = m['humandesign']
        bz = m['bazi']
        lines.append(f"### {name} · {hd['energy_type']} · Profile {hd['profile']}\n")
        lines.append(f"- **八字日主**：{bz['day_master']}（{bz['year']}{bz['month']}{bz['day']}{bz['hour']}）")
        lines.append(f"- **定義中心**：{', '.join(sorted(defined_map[name]))}")
        lines.append(f"- **未定義中心**：{', '.join(sorted(undefined_map[name]))}")
        lines.append(f"- **權威**：{hd['authority']} → 決策方式是 **{hd['strategy']}**")
        lines.append(f"- **非自己主題**：{hd.get('not_self', '無')}")
        lines.append("")
    
    # 兩兩互補分析
    lines.append("## 兩兩互補策略：如何協助對方變得更好\n")
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            p1, p2 = members[i], members[j]
            n1, n2 = p1['name'], p2['name']
            
            # 定義互補
            p1_can_give = defined_map[n1] & undefined_map[n2]
            p2_can_give = defined_map[n2] & undefined_map[n1]
            
            lines.append(f"### {n1} × {n2}\n")
            
            if p1_can_give:
                lines.append(f"**{n1} 可以穩定支持 {n2} 的方面**：")
                for c in sorted(p1_can_give):
                    lines.append(f"- **{c}**：{CENTER_HUMAN_DESIGN[c]}")
                lines.append("")
            
            if p2_can_give:
                lines.append(f"**{n2} 可以穩定支持 {n1} 的方面**：")
                for c in sorted(p2_can_give):
                    lines.append(f"- **{c}**：{CENTER_HUMAN_DESIGN[c]}")
                lines.append("")
            
            # 共同定義 = 可以互相理解的領域
            shared = defined_map[n1] & defined_map[n2]
            if shared:
                lines.append(f"**共同語言**：{', '.join(sorted(shared))} → 在這些領域你們能「同頻共振」，不需要解釋就能理解對方。")
                lines.append("")
            
            # 都未定義 = 兩人共同的學習領域（容易一起迷失）
            both_undefined = undefined_map[n1] & undefined_map[n2]
            if both_undefined:
                lines.append(f"**共同盲點**：{', '.join(sorted(both_undefined))} → 兩人在這些領域都「開放」，容易互相放大焦慮或不確定感。需要引入第三方或獨立判斷。")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # 群體整體策略
    lines.append("## 群體整體協作策略\n")
    
    # 找出群體中最有定義的人
    most_defined = max(members, key=lambda m: len(defined_map[m['name']]))
    least_defined = min(members, key=lambda m: len(defined_map[m['name']]))
    
    lines.append(f"**能量錨點**：{most_defined['name']}（{len(defined_map[most_defined['name']])} 個定義中心）→ 當群體混亂時，以這個人的穩定能量為基準。")
    lines.append("")
    lines.append(f"**最需要被支持的**：{least_defined['name']}（{len(defined_map[least_defined['name']])} 個定義中心）→ 這個人最容易受群體能量影響，需要被有意識地保護。")
    lines.append("")
    
    # 各種能量類型的協作建議
    types = {}
    for m in members:
        t = m['humandesign']['energy_type']
        types.setdefault(t, []).append(m['name'])
    
    lines.append("**能量類型互動守則**：")
    for t, names in types.items():
        if t == '生產者':
            lines.append(f"- **{', '.join(names)}（生產者）**：不要問他們「你想做什麼」，而是給他們具體選項，讓薦骨用「嗯/唔」回應。他們的能量需要被正確的問題啟動。")
        elif t == '顯示生產者':
            lines.append(f"- **{', '.join(names)}（顯示生產者）**：他們既有薦骨的回應力，又有發起力。讓他們先回應，再給予行動空間。不要在他們回應前逼他們行動。")
        elif t == '顯示者':
            lines.append(f"- **{', '.join(names)}（顯示者）**：他們需要「被告知」才能順暢行動。與其讓他們猜測，不如直接說：「我需要你幫我做 X。」")
        elif t == '投射者':
            lines.append(f"- **{', '.join(names)}（投射者）**：永遠先邀請，再請求。他們的能量需要被認可和看見，否則會感到苦澀。")
    lines.append("")
    
    # 權威互動
    authorities = {}
    for m in members:
        a = m['humandesign']['authority']
        authorities.setdefault(a, []).append(m['name'])
    
    lines.append("**決策權威互動**：")
    for a, names in authorities.items():
        if '情緒' in a:
            lines.append(f"- **{', '.join(names)}（情緒權威）**：他們需要時間讓情緒波沉澱。重大決定不要當天做，給他們睡一覺的時間。")
        elif '薦骨' in a:
            lines.append(f"- **{', '.join(names)}（薦骨權威）**：問他們可以用「是/否」回答的問題。聽他們腹部發出的聲音，而不是腦袋裡的理由。")
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
    with open('group_insight_friends.md', 'w', encoding='utf-8') as f:
        f.write(md1)
    print("✓ group_insight_friends.md")
    
    # 組合2：韡寧 × 爸爸 × 媽媽 × 妹妹
    group2 = [
        get_data('韡寧', '1999-06-07', '15:30', '女'),
        get_data('爸爸', '1972-01-13', '01:08', '男'),
        get_data('媽媽', '1969-12-01', '02:00', '女'),
        get_data('妹妹', '2002-05-06', '15:00', '女'),
    ]
    
    md2 = analyze_group(group2, '韡寧 × 爸爸 × 媽媽 × 妹妹')
    with open('group_insight_family.md', 'w', encoding='utf-8') as f:
        f.write(md2)
    print("✓ group_insight_family.md")


if __name__ == '__main__':
    main()
