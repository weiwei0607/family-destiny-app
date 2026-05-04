from flask import Flask, request, jsonify, render_template
from engine import core, ziwei, humandesign, xingxiu, lunar_lookup, integrator
from datetime import datetime

app = Flask(__name__)

# ---------- helpers ----------

def _dt_from_payload(data):
    birth_date = data.get('date', '')
    birth_time = data.get('time', '12:00')
    return datetime.fromisoformat(f"{birth_date}T{birth_time}")

def _location_coords(loc_key):
    return {
        'taipei': (25.0330, 121.5654),
        'taichung': (24.1477, 120.6736),
        'kaohsiung': (22.6273, 120.3014),
    }.get(loc_key, (25.0330, 121.5654))

def _hour_idx(dt):
    return ((dt.hour + 1) // 2) % 12

def _gender_code(g):
    return '男' if g in ('男', 'male', 'M', 'm') else '女'

def _analyze_person(data):
    """回傳一個人的完整五系統分析 dict"""
    dt = _dt_from_payload(data)
    loc_key = data.get('location', 'taipei')
    lat, lon = _location_coords(loc_key)
    gender = _gender_code(data.get('gender', '女'))

    # 1. 八字
    bz = core.bazi_pillars(dt)

    # 2. 占星（同時取得黃經給人類圖）
    ast = core.western_astrology(dt, lat, lon)
    planets_longitudes = {k: v['longitude'] for k, v in ast.items()}

    # 3. 農曆（紫微、星宿需要）
    lunar = lunar_lookup.get_lunar_date(dt.year, dt.month, dt.day)
    if lunar is None:
        # fallback: 用農曆近似（農曆表查不到時）
        lunar = {'lunar_year': dt.year, 'lunar_month': dt.month, 'lunar_day': dt.day, 'lunar_year_gz': bz['year'], 'is_leap_month': False}

    # 4. 紫微斗數
    try:
        year_gan = bz['year'][0]
        year_zhi = bz['year'][1]
        zw = ziwei.ziwei_chart(
            year_gan=year_gan,
            year_zhi=year_zhi,
            lunar_month=lunar['lunar_month'],
            lunar_day=lunar['lunar_day'],
            hour_idx=_hour_idx(dt),
            gender=gender
        )
    except Exception:
        zw = {'命宮': '未知', '身宮': '未知', '五行局': '未知', '紫微': '未知', '天府': '未知', '主星': {}, '輔星': {}, '四化': {}}

    # 5. 人類圖
    try:
        hd = humandesign.calculate(planets_longitudes)
    except Exception:
        hd = {'energy_type': '未知', 'profile': '未知', 'authority': '未知', 'defined_gates': [], 'active_channels': [], 'defined_centers': [], 'gate_details': {}}

    # 6. 星宿
    try:
        xx = xingxiu.get_xingxiu(lunar['lunar_month'], lunar['lunar_day'])
    except Exception:
        xx = '未知'

    # 7. 整合畫像引擎 (NEW)
    portrait = integrator.generate_portrait(lunar, bz, ast, zw, hd, xx)
    
    # 簡易能量分數（根據定義中心數量 + 主星數量 + 八字日主強弱概念）
    energy_score = min(100, 60 + len(hd.get('defined_centers', [])) * 5 + len([v for v in zw.get('主星', {}).values() if v]) * 2)

    # 整合摘要句
    summary_parts = [
        f"{bz['day_master']}日主",
        f"{zw.get('命宮', '未知')}命宮",
        f"{hd.get('energy_type', '未知')}{hd.get('profile', '')}",
        f"{xx}宿"
    ]
    summary = ' · '.join(summary_parts)

    return {
        "name": data.get('name', ''),
        "gender": gender,
        "bazi": bz,
        "astrology": {k: {"sign": v["sign"], "degree": v["degree"]} for k, v in ast.items()},
        "ziwei": zw,
        "humandesign": hd,
        "xingxiu": xx,
        "lunar": lunar,
        "portrait": portrait, # 傳送整合後的結果
        "energy_score": energy_score,
        "summary": summary
    }

# ---------- routes ----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """個人分析 API（免費）"""
    data = request.get_json()
    result = _analyze_person(data)
    return jsonify(result)

@app.route('/api/compatibility', methods=['POST'])
def compatibility():
    """合盤分析 API（免費預覽 + 付費牆提示由前端控制）"""
    data = request.get_json()
    p1_data = data.get('person1', {})
    p2_data = data.get('person2', {})

    # 真正計算兩個人
    p1 = _analyze_person(p1_data)
    p2 = _analyze_person(p2_data)

    # 八字合盤（日主生剋）
    wuxing = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    dm1 = wuxing.get(p1['bazi']['day_master'], '')
    dm2 = wuxing.get(p2['bazi']['day_master'], '')
    if sheng.get(dm1) == dm2:
        bazi_note = f"{dm1}生{dm2} · 你滋養對方"
        bazi_score = 4
    elif ke.get(dm1) == dm2:
        bazi_note = f"{dm1}剋{dm2} · 你制約對方"
        bazi_score = 3
    elif sheng.get(dm2) == dm1:
        bazi_note = f"{dm2}生{dm1} · 對方滋養你"
        bazi_score = 4
    elif ke.get(dm2) == dm1:
        bazi_note = f"{dm2}剋{dm1} · 對方制約你"
        bazi_score = 3
    else:
        bazi_note = f"{dm1}與{dm2}比劫 · 平起平坐"
        bazi_score = 3

    # 占星合盤（太陽星座落差）
    sun1 = p1['astrology'].get('太陽', {}).get('sign', '')
    sun2 = p2['astrology'].get('太陽', {}).get('sign', '')
    if sun1 == sun2:
        astro_note = f"同{sun1} · 節奏同步"
        astro_score = 5
    else:
        astro_note = f"{sun1}與{sun2} · 互補視角"
        astro_score = 3

    # 紫微合盤
    zw1 = p1['ziwei'].get('命宮', '未知')
    zw2 = p2['ziwei'].get('命宮', '未知')
    ziwei_note = f"{zw1}與{zw2} · 雙紫府格"
    ziwei_score = 4

    # 人類圖合盤
    hd1 = p1['humandesign'].get('energy_type', '')
    hd2 = p2['humandesign'].get('energy_type', '')
    if hd1 == hd2:
        hd_note = f"雙{hd1} · 容易共振"
        hd_score = 3
    else:
        hd_note = f"{hd1}與{hd2} · 互補能量"
        hd_score = 4

    # 星宿關係
    xx_rel = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
    xingxiu_note = f"{p1['xingxiu']}與{p2['xingxiu']} · {xx_rel}"
    xingxiu_score = 4 if xx_rel in ['命之星','榮親','友衰'] else 3

    # 總分
    total = (bazi_score + astro_score + ziwei_score + hd_score + xingxiu_score) / 5
    stars = '⭐' * round(total)
    if total >= 4.5:
        summary = "靈魂伴侶等級，珍惜彼此"
    elif total >= 4:
        summary = "輕鬆舒服，需要主動經營深度"
    elif total >= 3:
        summary = "有摩擦也有成長，磨合後更穩"
    else:
        summary = "差異較大，需要更多理解與包容"

    return jsonify({
        "overall_score": round(total, 1),
        "stars": stars,
        "summary": summary,
        "dimensions": {
            "bazi": {"score": bazi_score, "note": bazi_note},
            "astro": {"score": astro_score, "note": astro_note},
            "ziwei": {"score": ziwei_score, "note": ziwei_note},
            "hd": {"score": hd_score, "note": hd_note},
            "xingxiu": {"score": xingxiu_score, "note": xingxiu_note}
        },
        "person1_summary": p1['summary'],
        "person2_summary": p2['summary']
    })


# ---------- family & friends report generators ----------

def _wuxing_element(gan):
    return {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}.get(gan, '')

def _compatibility_note(dm1, dm2):
    """八字日主關係描述"""
    wx1, wx2 = _wuxing_element(dm1), _wuxing_element(dm2)
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    if wx1 == wx2:
        return f"同{wx1}·比劫", "命之星"
    if sheng.get(wx1) == wx2:
        return f"{wx1}生{wx2}·你滋養對方", "榮親"
    if sheng.get(wx2) == wx1:
        return f"{wx2}生{wx1}·對方滋養你", "榮親"
    if ke.get(wx1) == wx2:
        return f"{wx1}剋{wx2}·你制約對方", "安壞"
    if ke.get(wx2) == wx1:
        return f"{wx2}剋{wx1}·對方制約你", "安壞"
    return "比劫", "命之星"


def _generate_relationship_matrix(people):
    """生成多人群體的關係矩陣"""
    n = len(people)
    matrix = []
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = people[i], people[j]
            dm1, dm2 = p1['bazi']['day_master'], p2['bazi']['day_master']
            wx_note, _ = _compatibility_note(dm1, dm2)
            
            sun1 = p1['astrology'].get('太陽', {}).get('sign', '')
            sun2 = p2['astrology'].get('太陽', {}).get('sign', '')
            astro_note = f"同{sun1}" if sun1 == sun2 else f"{sun1}與{sun2}"
            
            xx_rel = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
            xx_detail = xingxiu.relation_detail(p1['xingxiu'], p2['xingxiu'])
            
            hd1 = p1['humandesign'].get('energy_type', '')
            hd2 = p2['humandesign'].get('energy_type', '')
            hd_note = f"同{hd1}" if hd1 == hd2 else f"{hd1}與{hd2}"
            
            matrix.append({
                "pair": [p1['name'], p2['name']],
                "bazi": {"dm1": dm1, "dm2": dm2, "note": wx_note},
                "astro": {"sign1": sun1, "sign2": sun2, "note": astro_note},
                "ziwei": {"palace1": p1['ziwei'].get('命宮',''), "palace2": p2['ziwei'].get('命宮','')},
                "humandesign": {"type1": hd1, "type2": hd2, "note": hd_note},
                "xingxiu": {
                    "x1": p1['xingxiu'], "x2": p2['xingxiu'],
                    "relation": xx_rel,
                    "description": xx_detail['description'],
                    "dynamics": xx_detail['dynamics'],
                    "advice": xx_detail['advice']
                }
            })
    return matrix


def _generate_family_report(members_data):
    """生成家庭報告（3-6人）"""
    people = [_analyze_person(m) for m in members_data]
    matrix = _generate_relationship_matrix(people)
    
    # 五行角色分配
    role_map = {
        '木': '🌲 大樹——向上、直率、有主見',
        '火': '🔥 火焰——熱情、行動力、照亮他人',
        '土': '⛰️ 高山——穩重、承載、值得信賴',
        '金': '⚔️ 刀劍——果斷、剛毅、有主見',
        '水': '💧 暗流——溫柔、內斂、適應力強',
    }
    
    wuxing_roles = []
    for p in people:
        wx = _wuxing_element(p['bazi']['day_master'])
        wuxing_roles.append({
            "name": p['name'],
            "day_master": p['bazi']['day_master'],
            "element": wx,
            "role": role_map.get(wx, ''),
            "energy_score": p['energy_score'],
            "summary": p['summary']
        })
    
    # 家庭動態摘要
    same_dm = []
    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            if people[i]['bazi']['day_master'] == people[j]['bazi']['day_master']:
                same_dm.append(f"{people[i]['name']}與{people[j]['name']}同為{people[i]['bazi']['day_master']}日主")
    
    # 找出最強的關係（命之星/榮親）和最挑戰的（安壞）
    best_rels = [m for m in matrix if m['xingxiu']['relation'] in ['命之星', '榮親']]
    challenge_rels = [m for m in matrix if m['xingxiu']['relation'] in ['安壞', '業胎']]
    
    return {
        "report_type": "family",
        "member_count": len(people),
        "members": wuxing_roles,
        "relationship_matrix": matrix,
        "family_dynamics": {
            "same_day_masters": same_dm,
            "best_relationships": [{"pair": m['pair'], "relation": m['xingxiu']['relation'], "advice": m['xingxiu']['advice']} for m in best_rels],
            "challenge_relationships": [{"pair": m['pair'], "relation": m['xingxiu']['relation'], "advice": m['xingxiu']['advice']} for m in challenge_rels]
        }
    }


def _generate_friends_report(friends_data):
    """生成閨蜜報告（2-3人）"""
    people = [_analyze_person(f) for f in friends_data]
    matrix = _generate_relationship_matrix(people)
    
    # 群體化學反應
    energy_types = [p['humandesign'].get('energy_type', '') for p in people]
    type_summary = "、".join(set(energy_types))
    
    # 找出三人中的「黏著劑」（情緒權威或中間角色）
    authorities = [p['humandesign'].get('authority', '') for p in people]
    glue_candidates = [p['name'] for p in people if p['humandesign'].get('authority') == '情緒權威']
    
    # 日主生剋鏈
    dm_chain = []
    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            dm1, dm2 = people[i]['bazi']['day_master'], people[j]['bazi']['day_master']
            wx1, wx2 = _wuxing_element(dm1), _wuxing_element(dm2)
            dm_chain.append(f"{people[i]['name']}({dm1}/{wx1}) vs {people[j]['name']}({dm2}/{wx2})")
    
    return {
        "report_type": "friends",
        "member_count": len(people),
        "members": [{
            "name": p['name'],
            "gender": p['gender'],
            "summary": p['summary'],
            "portrait": p['portrait'],
            "energy_score": p['energy_score']
        } for p in people],
        "relationship_matrix": matrix,
        "group_chemistry": {
            "energy_type_mix": type_summary,
            "glue_candidates": glue_candidates,
            "authority_mix": list(set(authorities)),
            "day_master_chain": dm_chain
        }
    }


# ---------- new routes ----------

@app.route('/api/family-report', methods=['POST'])
def family_report():
    """家庭報告 API（3-6人）
    
    Payload:
    {
        "members": [
            {"name": "韡寧", "date": "1999-06-07", "time": "15:30", "gender": "女", "location": "taipei", "role": "self"},
            {"name": "妹妹", "date": "2002-05-06", "time": "13:15", "gender": "女", "location": "taipei", "role": "sister"},
            ...
        ]
    }
    """
    data = request.get_json()
    members = data.get('members', [])
    if len(members) < 2 or len(members) > 6:
        return jsonify({"error": "家庭成員數量需在 2-6 人之間"}), 400
    
    result = _generate_family_report(members)
    return jsonify(result)


@app.route('/api/friends-report', methods=['POST'])
def friends_report():
    """閨蜜報告 API（2-3人）
    
    Payload:
    {
        "friends": [
            {"name": "韡寧", "date": "1999-06-07", "time": "15:30", "gender": "女", "location": "taipei"},
            {"name": "朋友A", "date": "1999-01-04", "time": "00:08", "gender": "女", "location": "taipei"},
            {"name": "朋友B", "date": "1999-04-25", "time": "00:00", "gender": "女", "location": "taipei"}
        ]
    }
    """
    data = request.get_json()
    friends = data.get('friends', [])
    if len(friends) < 2 or len(friends) > 3:
        return jsonify({"error": "閨蜜人數需在 2-3 人之間"}), 400
    
    result = _generate_friends_report(friends)
    return jsonify(result)


# ---------- report routes ----------

@app.route('/report/personal')
def report_personal():
    """個人完整報告頁面（含付費牆）"""
    name = request.args.get('name', '訪客')
    date = request.args.get('date', '2000-01-01')
    time = request.args.get('time', '12:00')
    gender = request.args.get('gender', '女')
    location = request.args.get('location', 'taipei')
    
    data = {'name': name, 'date': date, 'time': time, 'gender': gender, 'location': location}
    result = _analyze_person(data)
    
    return render_template('report_personal.html',
        name=name,
        date=date,
        time=time,
        gender=gender,
        summary=result['summary'],
        energy_score=result['energy_score'],
        bazi=result['bazi'],
        astrology=result['astrology'],
        ziwei=result['ziwei'],
        humandesign=result['humandesign'],
        xingxiu=result['xingxiu'],
        portrait=result['portrait']
    )


@app.route('/report/compatibility')
def report_compatibility():
    """雙人合盤報告頁面（含付費牆）"""
    name1 = request.args.get('name1', 'A')
    date1 = request.args.get('date1', '2000-01-01')
    time1 = request.args.get('time1', '12:00')
    gender1 = request.args.get('gender1', '女')
    
    name2 = request.args.get('name2', 'B')
    date2 = request.args.get('date2', '2000-01-01')
    time2 = request.args.get('time2', '12:00')
    gender2 = request.args.get('gender2', '女')
    
    p1 = _analyze_person({'name': name1, 'date': date1, 'time': time1, 'gender': gender1, 'location': 'taipei'})
    p2 = _analyze_person({'name': name2, 'date': date2, 'time': time2, 'gender': gender2, 'location': 'taipei'})
    
    # Simple compatibility calc
    wuxing = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    dm1 = wuxing.get(p1['bazi']['day_master'], '')
    dm2 = wuxing.get(p2['bazi']['day_master'], '')
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    
    if sheng.get(dm1) == dm2:
        relation_type = f"{dm1}生{dm2}"
        relation_desc = "你滋養對方，付出型關係"
    elif ke.get(dm1) == dm2:
        relation_type = f"{dm1}剋{dm2}"
        relation_desc = "你制約對方，引導型關係"
    elif sheng.get(dm2) == dm1:
        relation_type = f"{dm2}生{dm1}"
        relation_desc = "對方滋養你，被照顧型關係"
    elif ke.get(dm2) == dm1:
        relation_type = f"{dm2}剋{dm1}"
        relation_desc = "對方制約你，被引導型關係"
    else:
        relation_type = "比劫"
        relation_desc = "平起平坐，競爭與合作並存"
    
    return render_template('report_compatibility.html',
        name1=name1, name2=name2,
        p1=p1, p2=p2,
        relation_type=relation_type,
        relation_desc=relation_desc
    )


@app.route('/report/family', methods=['GET', 'POST'])
def report_family():
    """家庭報告頁面（含付費牆）"""
    if request.method == 'POST':
        names = request.form.getlist('names[]')
        genders = request.form.getlist('genders[]')
        dates = request.form.getlist('dates[]')
        times = request.form.getlist('times[]')
    else:
        names = request.args.getlist('names[]')
        genders = request.args.getlist('genders[]')
        dates = request.args.getlist('dates[]')
        times = request.args.getlist('times[]')
    
    if len(names) < 2 or len(names) > 6:
        return "家庭成員數量需在 2-6 人之間", 400
    
    members_data = []
    for i in range(len(names)):
        members_data.append({
            'name': names[i],
            'gender': genders[i] if i < len(genders) else '女',
            'date': dates[i] if i < len(dates) else '2000-01-01',
            'time': times[i] if i < len(times) else '12:00',
            'location': 'taipei'
        })
    
    result = _generate_family_report(members_data)
    return render_template('report_family.html',
        members=result['members'],
        matrix=result['relationship_matrix'],
        dynamics=result['family_dynamics']
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
