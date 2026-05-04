#!/usr/bin/env python3
"""生成整合畫像與交互關係報告（v3 算法）"""

from app import app, _analyze_person, _generate_relationship_matrix
from engine import integrator

client = app.test_client()

PEOPLE = [
    {'name': '韡寧', 'date': '1999-06-07', 'time': '15:30', 'gender': '女', 'location': 'taipei'},
    {'name': '衍徵', 'date': '1999-01-04', 'time': '00:00', 'gender': '男', 'location': 'taipei'},
    {'name': '朋友B', 'date': '1999-04-25', 'time': '00:00', 'gender': '女', 'location': 'taipei'},
    {'name': '學生', 'date': '2010-10-15', 'time': '04:00', 'gender': '女', 'location': 'taipei'},
    {'name': '鹽城', 'date': '2001-11-06', 'time': '07:30', 'gender': '女', 'location': 'taipei'},
    {'name': '鹽城男友', 'date': '1999-01-12', 'time': '07:00', 'gender': '男', 'location': 'taipei'},
    {'name': '鹽城爸', 'date': '1965-10-31', 'time': '08:00', 'gender': '男', 'location': 'taipei'},
    {'name': '鹽城媽', 'date': '1969-04-28', 'time': '08:00', 'gender': '女', 'location': 'taipei'},
    {'name': '爸爸', 'date': '1972-01-13', 'time': '01:08', 'gender': '男', 'location': 'taipei'},
    {'name': '媽媽', 'date': '1969-12-01', 'time': '02:00', 'gender': '女', 'location': 'taipei'},
    {'name': '妹妹', 'date': '2002-05-06', 'time': '15:00', 'gender': '女', 'location': 'taipei'},
]


def get_person_data(data):
    """獲取個人完整數據"""
    resp = client.post('/api/analyze', json=data)
    return resp.get_json()


def generate_portrait_md(person_data):
    """生成個人整合畫像 Markdown"""
    p = person_data
    name = p['name']
    bz = p['bazi']
    ast = p['astrology']
    hd = p['humandesign']
    zw = p['ziwei']
    xx = p['xingxiu']
    portrait = p.get('portrait', {})

    cards = portrait.get('integrated_cards', [])
    prescriptions = portrait.get('prescriptions', [])
    life_topic = portrait.get('life_topic', '')

    cards_md = []
    for card in cards:
        cards_md.append(f"""### {card['title']}

{card['text']}

> {card['bad']}""")

    prescriptions_md = []
    for pres in prescriptions:
        prescriptions_md.append(f"- **{pres['icon']} {pres['title']}**：{pres['desc']}")

    return f"""# {name} · 五系統整合畫像（v3）

## 核心數據

| 系統 | 關鍵指標 |
|------|---------|
| 八字日主 | {bz['day_master']}（{bz['year']}{bz['month']}{bz['day']}{bz['hour']}） |
| 西洋占星 | 太陽{ast['太陽']['sign']} · 月亮{ast['月亮']['sign']} · 上升待計 |
| 紫微斗數 | 命宮{zw.get('命宮','')} · 五行局{zw.get('五行局','')} |
| 人類圖 | {hd['energy_type']} · Profile {hd['profile']} · {hd['authority']} |
| 星宿 | {xx} |

## 五大維度解析

{chr(10).join(cards_md)}

## 人生課題

{life_topic}

## 能量處方籤

{chr(10).join(prescriptions_md)}

---

> 本畫像由五系統交叉翻譯生成，供自我覺察參考。
"""


def generate_relationships_md(people_data):
    """生成關係矩陣 Markdown"""
    matrix = _generate_relationship_matrix(people_data)

    sections = []
    for m in matrix:
        p1, p2 = m['pair']
        sections.append(f"""## {p1} × {p2}

**八字關係**：{m['bazi']['note']}（{m['bazi']['dm1']} vs {m['bazi']['dm2']}）

**占星關係**：{m['astro']['note']}

**紫微關係**：命宮{m['ziwei']['palace1']} vs 命宮{m['ziwei']['palace2']}

**人類圖關係**：{m['humandesign']['note']}

**星宿關係**：{m['xingxiu']['relation']} · {m['xingxiu']['x1']} vs {m['xingxiu']['x2']}

{m['xingxiu']['description']}

**互動動力**：{m['xingxiu']['dynamics']}

**建議**：{m['xingxiu']['advice']}

---""")

    return f"""# 關係交互矩陣（v3 算法）

> 計算日期：2026-05-04
> 共 {len(people_data)} 人，{len(matrix)} 組關係

{chr(10).join(sections)}
"""


def main():
    print("正在獲取所有人數據...")
    people_data = []
    for p in PEOPLE:
        print(f"  → {p['name']}")
        data = get_person_data(p)
        data['name'] = p['name']
        people_data.append(data)

    # 生成個人整合畫像
    print("\n生成個人整合畫像...")
    for p in people_data:
        md = generate_portrait_md(p)
        filename = f"portrait_{p['name']}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"  ✓ {filename}")

    # 生成關係矩陣
    print("\n生成關係交互矩陣...")
    rel_md = generate_relationships_md(people_data)
    with open('relationship_matrix.md', 'w', encoding='utf-8') as f:
        f.write(rel_md)
    print(f"  ✓ relationship_matrix.md（{len(people_data)} 人 · {len(_generate_relationship_matrix(people_data))} 組關係）")

    # 生成家庭/群體動態摘要
    print("\n生成群體動態摘要...")
    from app import _wuxing_element, _compatibility_note

    # 五行角色
    role_map = {
        '木': '🌲 大樹——向上、直率、有主見',
        '火': '🔥 火焰——熱情、行動力、照亮他人',
        '土': '⛰️ 高山——穩重、承載、值得信賴',
        '金': '⚔️ 刀劍——果斷、剛毅、有主見',
        '水': '💧 暗流——溫柔、內斂、適應力強',
    }

    group_lines = ["# 群體能量動態（v3）\n"]
    group_lines.append("## 五行角色分布\n")
    for p in people_data:
        wx = _wuxing_element(p['bazi']['day_master'])
        group_lines.append(f"- **{p['name']}**：{p['bazi']['day_master']}（{wx}）→ {role_map.get(wx, '')}")

    group_lines.append("\n## 人類圖類型分布\n")
    hd_types = {}
    for p in people_data:
        t = p['humandesign']['energy_type']
        hd_types[t] = hd_types.get(t, []) + [p['name']]
    for t, names in hd_types.items():
        group_lines.append(f"- **{t}**：{', '.join(names)}")

    group_lines.append("\n## 星宿關係亮點\n")
    matrix = _generate_relationship_matrix(people_data)
    best = [m for m in matrix if m['xingxiu']['relation'] in ['命之星', '榮親']]
    challenge = [m for m in matrix if m['xingxiu']['relation'] in ['安壞', '業胎']]

    if best:
        group_lines.append("### 🟢 最佳關係（命之星 / 榮親）")
        for m in best:
            group_lines.append(f"- **{' × '.join(m['pair'])}**：{m['xingxiu']['relation']} — {m['xingxiu']['advice']}")

    if challenge:
        group_lines.append("\n### 🔴 挑戰關係（安壞 / 業胎）")
        for m in challenge:
            group_lines.append(f"- **{' × '.join(m['pair'])}**：{m['xingxiu']['relation']} — {m['xingxiu']['advice']}")

    with open('group_dynamics.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(group_lines))
    print(f"  ✓ group_dynamics.md")

    print("\n全部完成！")


if __name__ == '__main__':
    main()
