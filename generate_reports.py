#!/usr/bin/env python3
"""批量重新生成所有 v2 報告"""

import os
from app import app

client = app.test_client()

PEOPLE = [
    ('韡寧', '1999-06-07', '15:30', '女', 'taipei'),
    ('衍徵', '1999-01-04', '00:00', '男', 'taipei'),
    ('朋友B', '1999-04-25', '00:00', '女', 'taipei'),
    ('學生', '2010-10-15', '04:00', '女', 'taipei'),
    ('鹽城男友', '1999-01-12', '07:00', '男', 'taipei'),
    ('鹽城', '2001-11-06', '07:30', '女', 'taipei'),
    ('鹽城爸', '1965-10-31', '08:00', '男', 'taipei'),
    ('鹽城媽', '1969-04-28', '08:00', '女', 'taipei'),
    ('爸爸', '1972-01-13', '01:08', '男', 'taipei'),
    ('媽媽', '1969-12-01', '02:00', '女', 'taipei'),
    ('妹妹', '2002-05-06', '15:00', '女', 'taipei'),
]


def generate_report(name, date, time, gender, location):
    resp = client.post('/api/analyze', json={
        'name': name, 'date': date, 'time': time,
        'gender': gender, 'location': location
    })
    data = resp.get_json()

    bz = data['bazi']
    ast = data['astrology']
    zw = data['ziwei']
    hd = data['humandesign']
    xx = data['xingxiu']

    # 格式化紫微主星
    main_stars = []
    if '主星' in zw:
        for palace, stars in zw['主星'].items():
            if stars:
                main_stars.append(f"{palace}({' '.join(stars)})")

    # 格式化吉曜/煞曜（ziwei.py 返回結構中各星為獨立鍵）
    auspicious_keys = ['祿存', '天魁', '天鉞', '天馬', '紅鸞', '天喜']
    malefic_keys = ['擎羊', '陀羅', '火星', '鈴星', '地空', '地劫']
    sihua = zw.get('四化', {})

    ausp_items = []
    for k in auspicious_keys:
        v = zw.get(k)
        if v:
            ausp_items.append(f"{k} {v}")
    ausp_str = ' · '.join(ausp_items) if ausp_items else '無'

    male_items = []
    for k in malefic_keys:
        v = zw.get(k)
        if v:
            male_items.append(f"{k} {v}")
    male_str = ' · '.join(male_items) if male_items else '無'

    sihua_str = ' · '.join([f"{v}{k}" for k, v in sihua.items()]) if sihua else '無'

    # 西洋占星表格
    ast_rows = []
    for planet, info in ast.items():
        ast_rows.append(f"| {planet} | {info['sign']} | {info['degree']}° |")

    # 人類圖閘門詳情
    hd_personality = hd.get('personality_details', {})
    hd_design = hd.get('design_details', {})
    hd_gates = []
    for k, v in hd_personality.items():
        hd_gates.append(f"| {k} (P) | Gate {v['gate']} Line {v['line']} |")
    for k, v in hd_design.items():
        hd_gates.append(f"| {k} (D) | Gate {v['gate']} Line {v['line']} |")

    report = f"""# {name} · 五系統命理解讀報告（v3 修正版）

> 計算日期：2026-05-04
> 出生：{date} {time} · {gender} · {location}
> 算法版本：八字精確節氣 / 占星黃道經度 / 紫微中州派 / 人類圖 Rave Mandala v3

---

## 一、八字

| 柱 | 干支 |
|---|---|
| 年柱 | {bz['year']} |
| 月柱 | {bz['month']} |
| 日柱 | {bz['day']} |
| 時柱 | {bz['hour']} |

**日主：{bz['day_master']}**

## 二、西洋占星

| 行星 | 星座 | 度數 |
|---|---|---|
{chr(10).join(ast_rows)}

## 三、紫微斗數

| 項目 | 內容 |
|---|---|
| 命宮 | {zw.get('命宮', '未知')} |
| 身宮 | {zw.get('身宮', '未知')} |
| 五行局 | {zw.get('五行局', '未知')} |
| 紫微 | {zw.get('紫微', '未知')} |
| 天府 | {zw.get('天府', '未知')} |
| 大限走向 | {zw.get('大限走向', '未知')} |

### 主星

{' · '.join(main_stars) if main_stars else '無'}

### 吉曜

{ausp_str}

### 煞曜

{male_str}

### 四化

{sihua_str}

## 四、人類圖

| 項目 | 內容 |
|---|---|
| 能量類型 | {hd['energy_type']} |
| 人生角色 | {hd['profile']} |
| 內在權威 | {hd['authority']} |
| 策略 | {hd['strategy']} |
| 定義 | {hd.get('definition', '未知')} |
| 非自己 | {hd.get('not_self', '未知')} |
| 定義中心 | {'、'.join(hd['defined_centers'])} |
| 定義閘門 | {', '.join(map(str, hd['defined_gates']))} |
| 激活通道 | {' · '.join([f'{a}-{b}' for a, b in hd['active_channels']])} |

### 閘門詳情

| 天體 | 閘門/爻 |
|---|---|
{chr(10).join(hd_gates)}

## 五、星宿

{xx}

---

> ⚠️ 本報告為數學計算結果。整合敘事與生活建議需另行生成。
"""
    return report


def main():
    for name, date, time, gender, location in PEOPLE:
        safe_name = name.replace(' ', '_')
        filename = f"report_{safe_name}.md"
        print(f"生成 {name} ...")
        try:
            content = generate_report(name, date, time, gender, location)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {filename}")
        except Exception as e:
            print(f"  ✗ 錯誤: {e}")


if __name__ == '__main__':
    main()
