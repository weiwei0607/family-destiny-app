from flask import Flask, request, jsonify, render_template
from engine import core, ziwei, humandesign, xingxiu, lunar_lookup, integrator
from engine import compatibility as compat
from engine import travel as travel_engine
from engine import health as health_engine
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'service': 'family-destiny'})

TWN_TZ = timezone(timedelta(hours=8))   # 台灣時區 UTC+8

# ── 人物分析快取（以出生資料為 key，name 不影響計算）──
_person_cache: dict = {}
_CACHE_MAX = 60

# ---------- helpers ----------

def _dt_from_payload(data):
    birth_date = data.get('date', '')
    birth_time = data.get('time', '12:00')
    # 明確標注 UTC+8，避免系統時區影響 HD 計算
    return datetime.fromisoformat(f"{birth_date}T{birth_time}").replace(tzinfo=TWN_TZ)

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
    """回傳一個人的完整五系統分析 dict（附快取）"""
    loc_key = data.get('location', 'taipei')
    gender  = _gender_code(data.get('gender', '女'))
    cache_key = (data.get('date', ''), data.get('time', '12:00'), gender, loc_key)

    if cache_key in _person_cache:
        cached = dict(_person_cache[cache_key])
        cached['name'] = data.get('name', '')
        return cached

    dt = _dt_from_payload(data)
    lat, lon = _location_coords(loc_key)

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

    # 5. 人類圖（完整 Personality + Design 層）
    try:
        hd = humandesign.calculate_hd(dt)
    except Exception:
        hd = {'energy_type': '未知', 'profile': '未知', 'authority': '未知', 'strategy': '未知', 'not_self': '未知', 'definition': '未知', 'defined_gates': [], 'active_channels': [], 'defined_centers': [], 'personality_details': {}, 'design_details': {}}

    # 6. 星宿
    try:
        xx = xingxiu.get_xingxiu(lunar['lunar_month'], lunar['lunar_day'])
    except Exception:
        xx = '未知'

    # 7. 八字五行缺失分析
    _wx_map  = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    _zhx_map = {'寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水','子':'水','丑':'土'}
    present_wx = set()
    for k in ('year', 'month', 'day', 'hour'):
        v = bz.get(k, '')
        if v:
            present_wx.add(_wx_map.get(v[0], ''))
            present_wx.add(_zhx_map.get(v[-1], ''))
    present_wx.discard('')
    missing_wx = {'木', '火', '土', '金', '水'} - present_wx

    _wx_life = {'木': '成長創業', '火': '熱情表達', '土': '穩定根基',
                '金': '決斷紀律', '水': '智慧溝通與財運'}
    bazi_wuxing = {
        'present': sorted(present_wx),
        'missing': sorted(missing_wx),
        'missing_notes': [f"命缺{w}·{_wx_life.get(w,'')}" for w in missing_wx]
    }

    # 8. 八字大運（當前10年週期）
    try:
        dayun = core.bazi_dayun(dt, gender)
    except Exception:
        dayun = {'qiyun_age': 0, 'forward': True, 'sequence': [], 'current': None}

    # 9. 紫微大限（現在活在哪個宮）
    try:
        daxian = ziwei.get_current_daxian(zw, dt.year, gender)
    except Exception:
        daxian = None

    # 10. 流年干支十神分析 + 地支刑沖合
    try:
        liunian = core.bazi_liunian(dt)
    except Exception:
        liunian = None

    # 11. 八字神煞
    try:
        shengci = core.bazi_shengci(bz)
    except Exception:
        shengci = None

    # 12. 紫微小限（當年宮位）
    try:
        xiaoxian = ziwei.get_current_xiaoxian(zw, dt.year, gender)
    except Exception:
        xiaoxian = None

    # 13. 人類圖業力十字
    try:
        incarnation_cross = humandesign.get_incarnation_cross(hd)
    except Exception:
        incarnation_cross = None

    # 14. 八字格局 + 喜用神
    try:
        struct = core.bazi_structure_analysis(bz)
    except Exception:
        struct = None

    # 15. 紫微流年四化
    try:
        liunian_sihua = ziwei.get_liunian_sihua(zw, liunian['gan']) if liunian else None
    except Exception:
        liunian_sihua = None

    # 16. 人類圖通道主題
    try:
        channel_themes = humandesign.get_active_channel_themes(hd)
    except Exception:
        channel_themes = []

    # 17. 占星行星相位
    try:
        aspects = core.calc_aspects(ast)
    except Exception:
        aspects = []

    # 18. 紫微大限四化
    try:
        daxian_sihua = ziwei.get_daxian_sihua(zw, daxian) if daxian else None
    except Exception:
        daxian_sihua = None

    # 19. 流月干支十神
    from datetime import date as _date
    _today = _date.today()
    try:
        liuyue = core.bazi_liuyue(dt, current_year=_today.year, current_month=_today.month)
    except Exception:
        liuyue = None

    # 20. 八字空亡（旬空）
    try:
        kongwang = core.bazi_kongwang(bz)
    except Exception:
        kongwang = None

    # 21. 三層四化整合地圖
    try:
        sihua_map = ziwei.get_sihua_palace_map(zw, liunian_sihua, daxian_sihua)
    except Exception:
        sihua_map = {}

    # 22. 人類圖開放中心制約分析
    try:
        hd_open_centers = humandesign.get_open_center_analysis(hd)
    except Exception:
        hd_open_centers = []

    # 23. 整合畫像引擎 v7
    portrait = integrator.generate_portrait(lunar, bz, ast, zw, hd, xx,
                                             dayun=dayun, daxian=daxian,
                                             liunian=liunian, shengci=shengci,
                                             xiaoxian=xiaoxian,
                                             incarnation_cross=incarnation_cross,
                                             struct=struct,
                                             liunian_sihua=liunian_sihua,
                                             channel_themes=channel_themes,
                                             aspects=aspects,
                                             daxian_sihua=daxian_sihua,
                                             liuyue=liuyue,
                                             kongwang=kongwang)

    # 上升點（若已計算）
    asc_info = ast.get('上升點', {})
    asc_sign = asc_info.get('sign', '')

    # 能量分數
    strength_level = portrait.get('day_master_strength', {}).get('level', 'neutral')
    strength_bonus = {'strong': 15, 'slightly_strong': 8, 'neutral': 0,
                      'slightly_weak': -5, 'weak': -10}.get(strength_level, 0)
    energy_score = min(100, 60
                       + len(hd.get('defined_centers', [])) * 4
                       + len([v for v in zw.get('主星', {}).values() if v]) * 2
                       + strength_bonus)

    # 整合摘要句（含上升點）
    summary_parts = [
        f"{bz['day_master']}日主",
        f"{zw.get('命宮', '未知')}命宮",
        f"{hd.get('energy_type', '未知')}{hd.get('profile', '')}",
        f"{xx}宿",
    ]
    if asc_sign:
        summary_parts.append(f"上升{asc_sign}")
    summary = ' · '.join(summary_parts)

    result = {
        "name": data.get('name', ''),
        "gender": gender,
        "bazi": bz,
        "bazi_wuxing": bazi_wuxing,
        "bazi_dayun": dayun,
        "bazi_liunian": liunian,
        "bazi_shengci": shengci,
        "astrology": {k: {"sign": v["sign"], "degree": v["degree"]} for k, v in ast.items()},
        "astrology_full": ast,
        "ziwei": zw,
        "ziwei_daxian": daxian,
        "ziwei_xiaoxian": xiaoxian,
        "humandesign": hd,
        "hd_incarnation_cross": incarnation_cross,
        "hd_channel_themes": channel_themes,
        "bazi_structure": struct,
        "bazi_kongwang": kongwang,
        "bazi_liuyue": liuyue,
        "ziwei_liunian_sihua": liunian_sihua,
        "ziwei_daxian_sihua": daxian_sihua,
        "astro_aspects": aspects,
        "sihua_map": sihua_map,
        "hd_open_centers": hd_open_centers,
        "xingxiu": xx,
        "lunar": lunar,
        "portrait": portrait,
        "current_phase": portrait.get('current_phase', {}),
        "annual_fortune": portrait.get('annual_fortune', {}),
        "energy_score": energy_score,
        "summary": summary,
        "asc_sign": asc_sign,
    }

    # 24. 旅遊體質推薦
    try:
        result["travel_profile"] = travel_engine.get_travel_profile(
            struct or {}, bazi_wuxing, day_master=bz.get('day_master', '')
        )
    except Exception:
        result["travel_profile"] = None

    # 25. 健康體質分析
    try:
        result["health_profile"] = health_engine.get_health_profile(
            struct or {}, bazi_wuxing, day_master=bz.get('day_master', '')
        )
    except Exception:
        result["health_profile"] = None

    # 寫入快取（超過上限則淘汰最舊的一筆）
    if len(_person_cache) >= _CACHE_MAX:
        _person_cache.pop(next(iter(_person_cache)))
    _person_cache[cache_key] = result
    return result

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

    # 使用 _analyze_person 已計算的完整占星資料（含 longitude + ASC）
    ast1_full = p1.get('astrology_full', {})
    ast2_full = p2.get('astrology_full', {})

    # 五系統評分（使用新引擎）
    bazi_score,   bazi_note   = compat.score_bazi(p1['bazi'], p2['bazi'])
    astro_score,  astro_note  = compat.score_astro(ast1_full, ast2_full)
    ziwei_score,  ziwei_note  = compat.score_ziwei(p1['ziwei'], p2['ziwei'])
    hd_score,     hd_note     = compat.score_hd(p1['humandesign'], p2['humandesign'])

    xx_rel = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
    xx_detail = xingxiu.relation_detail(p1['xingxiu'], p2['xingxiu'])
    xingxiu_score, xingxiu_note = compat.score_xingxiu(p1['xingxiu'], p2['xingxiu'], xx_rel)

    # 加權總分（五大核心維度）
    scores = {'bazi': bazi_score, 'astro': astro_score, 'ziwei': ziwei_score,
              'hd': hd_score, 'xingxiu': xingxiu_score}
    total = compat.overall_score(scores)

    # ── 延伸合盤分析 ──
    taohua_score, taohua_note = compat.score_taohua(p1['bazi'], p2['bazi'])

    overlay_score, overlay_note = compat.score_house_overlay(ast1_full, ast2_full)

    composite_score, composite_note = compat.score_composite(ast1_full, ast2_full)

    year_delta, year_note = compat.score_synastry_year(
        p1.get('bazi_dayun'), p2.get('bazi_dayun')
    )

    stars = '⭐' * round(total)
    if total >= 4.5:
        summary = "靈魂伴侶等級，命中注定的契合"
    elif total >= 4.0:
        summary = "高度相容，輕鬆舒服的夥伴關係"
    elif total >= 3.5:
        summary = "互補共成長，磨合後更穩固"
    elif total >= 3.0:
        summary = "有摩擦也有成長，需要主動溝通"
    else:
        summary = "差異較大，需要更多理解與包容"

    return jsonify({
        "overall_score": total,
        "stars": stars,
        "summary": summary,
        "dimensions": {
            "bazi":     {"score": bazi_score,     "note": bazi_note},
            "astro":    {"score": astro_score,    "note": astro_note},
            "ziwei":    {"score": ziwei_score,    "note": ziwei_note},
            "hd":       {"score": hd_score,       "note": hd_note},
            "xingxiu":  {"score": xingxiu_score,  "note": xingxiu_note,
                         "description": xx_detail.get('description', ''),
                         "advice": xx_detail.get('advice', '')}
        },
        "extended": {
            "taohua": {
                "score": taohua_score,
                "note": taohua_note,
                "label": "桃花星 / 紅鸞天喜"
            },
            "house_overlay": {
                "score": overlay_score,
                "note": overlay_note,
                "label": "占星宮位疊加（整宮制）"
            },
            "composite": {
                "score": composite_score,
                "note": composite_note,
                "label": "Composite 複合盤"
            },
            "synastry_year": {
                "delta": year_delta,
                "note": year_note,
                "label": "合盤流年（大運交叉）"
            }
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
    """生成多人群體的關係矩陣（完整五系統評分）"""
    n = len(people)
    matrix = []
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = people[i], people[j]
            dm1, dm2 = p1['bazi']['day_master'], p2['bazi']['day_master']

            bazi_score, bazi_note = compat.score_bazi(p1['bazi'], p2['bazi'])
            hd_score,   hd_note   = compat.score_hd(p1['humandesign'], p2['humandesign'])
            zw_score,   zw_note   = compat.score_ziwei(p1['ziwei'], p2['ziwei'])
            # 使用完整占星資料（含黃經）才能計算相位
            astro_score, astro_note = compat.score_astro(
                p1.get('astrology_full', p1['astrology']),
                p2.get('astrology_full', p2['astrology']),
            )

            xx_rel    = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
            xx_detail = xingxiu.relation_detail(p1['xingxiu'], p2['xingxiu'])
            xx_score, xx_note = compat.score_xingxiu(p1['xingxiu'], p2['xingxiu'], xx_rel)

            overall = compat.overall_score({
                'bazi': bazi_score, 'hd': hd_score, 'ziwei': zw_score,
                'astro': astro_score, 'xingxiu': xx_score,
            })

            sun1 = p1['astrology'].get('太陽', {}).get('sign', '')
            sun2 = p2['astrology'].get('太陽', {}).get('sign', '')

            matrix.append({
                "pair": [p1['name'], p2['name']],
                "overall_score": overall,
                "bazi":  {"dm1": dm1, "dm2": dm2, "score": bazi_score, "note": bazi_note},
                "astro": {"sign1": sun1, "sign2": sun2, "score": astro_score, "note": astro_note},
                "ziwei": {"palace1": p1['ziwei'].get('命宮',''), "palace2": p2['ziwei'].get('命宮',''),
                          "score": zw_score, "note": zw_note},
                "humandesign": {"type1": p1['humandesign'].get('energy_type',''),
                                "type2": p2['humandesign'].get('energy_type',''),
                                "score": hd_score, "note": hd_note},
                "xingxiu": {
                    "x1": p1['xingxiu'], "x2": p2['xingxiu'],
                    "relation": xx_rel, "score": xx_score,
                    "description": xx_detail.get('description', ''),
                    "dynamics":    xx_detail.get('dynamics', ''),
                    "advice":      xx_detail.get('advice', ''),
                },
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
        cp = p.get('current_phase', {})
        wuxing_roles.append({
            "name": p['name'],
            "day_master": p['bazi']['day_master'],
            "element": wx,
            "role": role_map.get(wx, ''),
            "energy_score": p['energy_score'],
            "summary": p['summary'],
            "current_dayun": cp.get('dayun', {}).get('pillar', '') + ' ' + cp.get('dayun', {}).get('age_range', '') if cp.get('dayun') else '',
            "current_daxian": cp.get('daxian', {}).get('palace_name', '') if cp.get('daxian') else '',
        })
    
    # 家庭動態摘要
    same_dm = []
    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            if people[i]['bazi']['day_master'] == people[j]['bazi']['day_master']:
                same_dm.append(f"{people[i]['name']}與{people[j]['name']}同為{people[i]['bazi']['day_master']}日主")

    # 找出最強/最挑戰關係（含合盤總分）
    sorted_matrix = sorted(matrix, key=lambda m: m.get('overall_score', 0), reverse=True)
    best_rels      = [m for m in sorted_matrix if m.get('overall_score', 0) >= 3.8][:3]
    challenge_rels = [m for m in sorted_matrix if m.get('overall_score', 0) < 3.0][:3]

    # 五行均衡分析
    wx_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    for p in people:
        wx = _wuxing_element(p['bazi']['day_master'])
        if wx in wx_count:
            wx_count[wx] += 1

    max_wx = max(wx_count, key=wx_count.get)
    min_wx = min(wx_count, key=wx_count.get)
    wx_roles = {'木': '創意創業', '火': '熱情行動', '土': '穩定承載',
                '金': '決斷執行', '水': '智慧溝通'}

    wx_balance = {
        "distribution": wx_count,
        "dominant": {
            "element": max_wx, "count": wx_count[max_wx],
            "note": f"家庭{wx_roles.get(max_wx, max_wx)}能量充足"
                    + ("，但可能過於同頻、缺乏衝突性成長" if wx_count[max_wx] >= len(people) // 2 + 1 else "")
        },
        "missing": {
            "element": min_wx, "count": wx_count[min_wx],
            "note": f"家庭{'缺' if wx_count[min_wx] == 0 else '弱'}{wx_roles.get(min_wx, min_wx)}能量，"
                    f"{'建議從外部補充此能量的朋友或環境' if wx_count[min_wx] == 0 else '需留意此面向的不足'}"
        },
        "balance_score": round(
            1.0 - (max(wx_count.values()) - min(wx_count.values())) / max(len(people), 1), 2
        )
    }

    # 群體角色：誰是黏著劑（最多合關係）？誰是火花（最多衝）？
    person_he_count   = {p['name']: 0 for p in people}
    person_chong_count = {p['name']: 0 for p in people}
    for m in matrix:
        bz_note = m['bazi'].get('note', '')
        for name in m['pair']:
            if '六合' in bz_note or '天干合' in bz_note:
                person_he_count[name] = person_he_count.get(name, 0) + 1
            if '六衝' in bz_note:
                person_chong_count[name] = person_chong_count.get(name, 0) + 1

    glue_person   = max(person_he_count, key=person_he_count.get)
    spark_person  = max(person_chong_count, key=person_chong_count.get)

    # 大運/大限生命週期摘要
    lifecycle_insights = []
    for p in people:
        cp = p.get('current_phase', {})
        dy = cp.get('dayun', {})
        dx = cp.get('daxian', {})
        if dy.get('desc'):
            lifecycle_insights.append({
                "name": p['name'],
                "type": "dayun",
                "summary": dy['desc'],
                "relation": dy.get('relation', ''),
            })
        if dx.get('desc'):
            lifecycle_insights.append({
                "name": p['name'],
                "type": "daxian",
                "summary": dx['desc'],
                "palace": dx.get('palace_name', ''),
            })

    return {
        "report_type": "family",
        "member_count": len(people),
        "members": wuxing_roles,
        "relationship_matrix": sorted_matrix,
        "wuxing_balance": wx_balance,
        "lifecycle_insights": lifecycle_insights,
        "family_dynamics": {
            "same_day_masters": same_dm,
            "glue_person": {"name": glue_person, "note": "最多六合關係，是家庭的黏著劑"},
            "spark_person": {"name": spark_person, "note": "最多六衝關係，帶來動力但也是摩擦來源"},
            "best_relationships": [
                {"pair": m['pair'], "score": m.get('overall_score'), "note": m['bazi']['note']}
                for m in best_rels
            ],
            "challenge_relationships": [
                {"pair": m['pair'], "score": m.get('overall_score'), "note": m['bazi']['note']}
                for m in challenge_rels
            ]
        }
    }


def _generate_friends_report(friends_data):
    """生成閨蜜報告（2-3人）"""
    people = [_analyze_person(f) for f in friends_data]
    matrix = _generate_relationship_matrix(people)
    
    # 群體化學反應
    energy_types = [p['humandesign'].get('energy_type', '') for p in people]
    type_summary = "、".join(set(energy_types))

    # 找出黏著劑（最高平均合盤分）和火花（最多高分對）
    authorities = [p['humandesign'].get('authority', '') for p in people]
    glue_candidates = [p['name'] for p in people if p['humandesign'].get('authority') in ('情緒權威', '薦骨權威')]

    # 日主生剋 + 合分析
    dm_chain = []
    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            dm1, dm2 = people[i]['bazi']['day_master'], people[j]['bazi']['day_master']
            wx1, wx2 = _wuxing_element(dm1), _wuxing_element(dm2)
            bz_s, bz_n = compat.score_bazi(people[i]['bazi'], people[j]['bazi'])
            dm_chain.append({
                "pair": [people[i]['name'], people[j]['name']],
                "dm": f"{dm1}({wx1}) vs {dm2}({wx2})",
                "score": bz_s,
                "note": bz_n.split(' · ')[0]
            })

    # 最佳化學組合
    best_pair = max(matrix, key=lambda m: m.get('overall_score', 0), default={})
    tension_pair = min(matrix, key=lambda m: m.get('overall_score', 5), default={})
    
    return {
        "report_type": "friends",
        "member_count": len(people),
        "members": [{
            "name": p['name'],
            "gender": p['gender'],
            "summary": p['summary'],
            "portrait": p['portrait'],
            "current_phase": p.get('current_phase', {}),
            "energy_score": p['energy_score'],
            "day_master_strength": p['portrait'].get('day_master_strength', {}),
        } for p in people],
        "relationship_matrix": sorted(matrix, key=lambda m: m.get('overall_score', 0), reverse=True),
        "group_chemistry": {
            "energy_type_mix": type_summary,
            "glue_candidates": glue_candidates,
            "authority_mix": list(set(authorities)),
            "day_master_chain": dm_chain,
            "best_pair": best_pair.get('pair', []),
            "best_pair_score": best_pair.get('overall_score'),
            "tension_pair": tension_pair.get('pair', []),
            "tension_pair_score": tension_pair.get('overall_score'),
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

    import re as _re
    _life = result['portrait'].get('life_topic', '')
    _raw  = _re.sub(r'^【[^】]*】', '', _life).strip()
    card_quote = (_raw[:68] + '⋯') if len(_raw) > 68 else _raw

    return render_template('report_personal.html',
        name=name,
        date=date,
        time=time,
        gender=gender,
        summary=result['summary'],
        energy_score=result['energy_score'],
        bazi=result['bazi'],
        bazi_wuxing=result['bazi_wuxing'],
        astrology=result['astrology'],
        ziwei=result['ziwei'],
        humandesign=result['humandesign'],
        xingxiu=result['xingxiu'],
        portrait=result['portrait'],
        card_quote=card_quote,
        bazi_structure=result['bazi_structure'],
        bazi_liunian=result['bazi_liunian'],
        bazi_liuyue=result['bazi_liuyue'],
        astro_aspects=result['astro_aspects'],
        ziwei_daxian_sihua=result['ziwei_daxian_sihua'],
        hd_incarnation_cross=result['hd_incarnation_cross'],
        hd_channel_themes=result['hd_channel_themes'],
        sihua_map=result['sihua_map'],
        hd_open_centers=result['hd_open_centers'],
        bazi_kongwang=result['bazi_kongwang'],
        travel_profile=result.get('travel_profile'),
        health_profile=result.get('health_profile'),
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
    
    p1_data = {'name': name1, 'date': date1, 'time': time1, 'gender': gender1, 'location': 'taipei'}
    p2_data = {'name': name2, 'date': date2, 'time': time2, 'gender': gender2, 'location': 'taipei'}
    p1 = _analyze_person(p1_data)
    p2 = _analyze_person(p2_data)

    ast1_full = p1.get('astrology_full', {})
    ast2_full = p2.get('astrology_full', {})

    # 五大維度評分
    bazi_score,    bazi_note    = compat.score_bazi(p1['bazi'], p2['bazi'])
    astro_score,   astro_note   = compat.score_astro(ast1_full, ast2_full)
    ziwei_score,   ziwei_note   = compat.score_ziwei(p1['ziwei'], p2['ziwei'])
    hd_score,      hd_note      = compat.score_hd(p1['humandesign'], p2['humandesign'])
    xx_rel    = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
    xx_detail = xingxiu.relation_detail(p1['xingxiu'], p2['xingxiu'])
    xingxiu_score, xingxiu_note = compat.score_xingxiu(p1['xingxiu'], p2['xingxiu'], xx_rel)

    scores = {'bazi': bazi_score, 'astro': astro_score, 'ziwei': ziwei_score,
              'hd': hd_score, 'xingxiu': xingxiu_score}
    total = compat.overall_score(scores)

    # 延伸分析
    taohua_score,    taohua_note    = compat.score_taohua(p1['bazi'], p2['bazi'])
    overlay_score,   overlay_note   = compat.score_house_overlay(ast1_full, ast2_full)
    composite_score, composite_note = compat.score_composite(ast1_full, ast2_full)
    year_delta,      year_note      = compat.score_synastry_year(
        p1.get('bazi_dayun'), p2.get('bazi_dayun')
    )

    stars = '⭐' * round(total)
    if total >= 4.5:   summary_text = "靈魂伴侶等級，命中注定的契合"
    elif total >= 4.0: summary_text = "高度相容，輕鬆舒服的夥伴關係"
    elif total >= 3.5: summary_text = "互補共成長，磨合後更穩固"
    elif total >= 3.0: summary_text = "有摩擦也有成長，需要主動溝通"
    else:              summary_text = "差異較大，需要更多理解與包容"

    relation_type = bazi_note.split('·')[0].strip()
    _raw_hl = (taohua_note if taohua_score >= 4.0 else bazi_note).split('·')[0].strip()
    card_highlight = (_raw_hl[:60] + '⋯') if len(_raw_hl) > 60 else _raw_hl

    return render_template('report_compatibility.html',
        name1=name1, name2=name2,
        p1=p1, p2=p2,
        relation_type=relation_type,
        bazi_score=bazi_score,   bazi_note=bazi_note,
        astro_score=astro_score, astro_note=astro_note,
        ziwei_score=ziwei_score, ziwei_note=ziwei_note,
        hd_score=hd_score,       hd_note=hd_note,
        xingxiu_score=xingxiu_score, xingxiu_note=xingxiu_note,
        xx_detail=xx_detail,
        total=total, stars=stars, summary_text=summary_text,
        taohua_score=taohua_score,   taohua_note=taohua_note,
        overlay_score=overlay_score, overlay_note=overlay_note,
        composite_score=composite_score, composite_note=composite_note,
        year_delta=year_delta, year_note=year_note,
        card_highlight=card_highlight,
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
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
