"""五系統整合畫像引擎 v3

更新：
- 大運天干十神分析（動態運勢解讀）
- 紫微大限宮整合進 life_topic
- 紫微命宮主星人格解讀
- 跨系統交叉驗證強化（6+ 信號）
- strength_note 格式清理
- generate_portrait 接受 dayun/daxian 參數
"""

WUXING_MAP = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
}

ZHI_MAIN_WX = {
    '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火',
    '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水',
    '子': '水', '丑': '土',
}

SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE    = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}


def _day_master_strength(bazi):
    """
    旺弱分析 v2：掃描全部 8 個字（3個非日主天干 + 4個地支主氣），
    統計幫扶力 vs 耗克力，給出5級旺弱結論。
    """
    dm = bazi.get('day_master', '')
    dm_wx = WUXING_MAP.get(dm, '')
    if not dm_wx:
        return 'neutral', '日主未知'

    help_score = 0.0
    hurt_score = 0.0

    for key in ('year', 'month', 'hour'):
        g = bazi.get(key, '')[:1]
        if not g:
            continue
        wx = WUXING_MAP.get(g, '')
        if not wx:
            continue
        if wx == dm_wx:              help_score += 1.0
        elif SHENG.get(wx) == dm_wx: help_score += 1.5
        elif SHENG.get(dm_wx) == wx: hurt_score += 0.8
        elif KE.get(wx) == dm_wx:    hurt_score += 1.2
        elif KE.get(dm_wx) == wx:    hurt_score += 0.4

    for key in ('year', 'month', 'day', 'hour'):
        z = bazi.get(key, '')[-1:]
        if not z:
            continue
        wx = ZHI_MAIN_WX.get(z, '')
        if not wx:
            continue
        if wx == dm_wx:              help_score += 0.8
        elif SHENG.get(wx) == dm_wx: help_score += 1.0
        elif SHENG.get(dm_wx) == wx: hurt_score += 0.6
        elif KE.get(wx) == dm_wx:    hurt_score += 0.8
        elif KE.get(dm_wx) == wx:    hurt_score += 0.3

    diff = help_score - hurt_score
    if diff >= 2.0:
        level, note = 'strong',         '身強'
    elif diff >= 0.5:
        level, note = 'slightly_strong','偏旺'
    elif diff <= -2.0:
        level, note = 'weak',           '身弱'
    elif diff <= -0.5:
        level, note = 'slightly_weak',  '偏弱'
    else:
        level, note = 'neutral',        '中和'

    return level, note


# ── 外在人格地圖 ──
OUTER_MAP = {
    '甲': '參天大樹，正直、有向上心，渴望被看見',
    '乙': '柔美藤蔓，靈活、適應力強，善於借力',
    '丙': '燦爛陽光，熱情、感染力強，天生領袖氣場',
    '丁': '溫暖燭火，細膩、服務心強，點亮他人',
    '戊': '厚重高山，穩重、值得信賴，承載一切',
    '己': '濕潤田園，包容、孕育力強，潤物細無聲',
    '庚': '剛硬金屬，果斷、有義氣，不願妥協',
    '辛': '閃耀珠寶，精緻、自尊心強，追求完美',
    '壬': '奔騰江河，大氣、洞察力強，格局開闊',
    '癸': '靈動雨露，溫柔、直覺敏銳，富有創意',
}

# ── 紫微命宮主星人格意涵 ──
MINGONG_STAR_DESC = {
    '紫微': ('天生領導者，有貴氣與帝王格局', '掌控欲強，需學會分權'),
    '天機': ('智慧謀士，思維靈活，擅長策略規劃', '想太多，容易患得患失'),
    '太陽': ('陽光外放，天生服務公眾，事業心強', '過度付出，需要學會接受'),
    '武曲': ('行動力強的財星，務實、重效率', '直接而缺乏耐心，需溝通技巧'),
    '天同': ('福星入命，享樂主義，追求舒適平和', '過於安逸，缺乏衝勁'),
    '廉貞': ('才藝明星，多才多藝，情感豐富', '情緒易波動，感情路多波折'),
    '天府': ('財庫守護，穩健持重，物質豐足', '保守，不善冒險'),
    '太陰': ('感性細膩，直覺強，夜晚能量佳', '情緒敏感，月亮心境易起伏'),
    '貪狼': ('桃花入命，多才多藝，人緣旺盛', '欲望多元，容易三心二意'),
    '巨門': ('口才星，善辯，思維深刻', '容易多是非，需謹言'),
    '天相': ('印星入命，得長輩助力，重情重義', '易受他人影響，需獨立判斷'),
    '天梁': ('蔭星，有慈悲心，擅長解難', '操心命，習慣幫別人扛'),
    '七殺': ('將星入命，衝勁十足，天生開創者', '孤剋性重，不喜被束縛'),
    '破軍': ('改革星，變動性強，不安於現狀', '破壞與建設並存，需學會收尾'),
}


def _dayun_analysis(dayun, dm):
    """
    分析當前大運天干對日主的十神關係與影響方向。
    回傳 (relation_name, desc_str)
    """
    if not dayun or not dayun.get('current'):
        return '', ''

    pillar = dayun['current'].get('pillar', '')
    if not pillar or len(pillar) < 2:
        return '', ''

    dy_g = pillar[0]
    age_range = dayun['current'].get('age_range', '')
    wx_dm = WUXING_MAP.get(dm, '')
    wx_dy = WUXING_MAP.get(dy_g, '')

    if not wx_dm or not wx_dy:
        return '', ''

    if wx_dy == wx_dm:
        same_yin_yang = (dy_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        relation = '比肩' if same_yin_yang else '劫財'
        desc = (f"【{pillar}大運 {age_range}】{dy_g}運（{wx_dy}）與日主{dm}同氣——"
                f"自我意識強，{relation}運旺盛，適合強化個人品牌、獨立開創")
    elif SHENG.get(wx_dy) == wx_dm:
        relation = '正印' if (dy_g in '甲丙戊庚壬') != (dm in '甲丙戊庚壬') else '偏印'
        desc = (f"【{pillar}大運 {age_range}】{dy_g}運（{wx_dy}生{wx_dm}）——"
                f"{relation}大運，學習運與貴人運旺盛，適合進修、考試、接受前輩指導")
    elif SHENG.get(wx_dm) == wx_dy:
        relation = '傷官' if (dy_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬') else '食神'
        desc = (f"【{pillar}大運 {age_range}】{dy_g}運（{wx_dm}生{wx_dy}）——"
                f"{relation}大運，創意表達、才藝展現的高峰期，適合創作輸出與副業發展")
    elif KE.get(wx_dm) == wx_dy:
        relation = '偏財' if (dy_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬') else '正財'
        desc = (f"【{pillar}大運 {age_range}】{dy_g}運（{wx_dm}克{wx_dy}）——"
                f"{relation}大運，財運與物質機會升溫，適合投資、理財、拓展業務")
    elif KE.get(wx_dy) == wx_dm:
        relation = '七殺' if (dy_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬') else '正官'
        desc = (f"【{pillar}大運 {age_range}】{dy_g}運（{wx_dy}克{wx_dm}）——"
                f"{relation}大運，壓力與機遇並存，適合面對挑戰、爭取晉升或認證")
    else:
        relation, desc = '', ''

    return relation, desc


def _mingong_stars(ziwei):
    """從紫微排盤提取命宮中的主星列表"""
    ming_str = ziwei.get('命宮', '')
    if not ming_str:
        return []
    ming_zhi = ming_str[-1]
    stars = []
    for star, zhi in ziwei.get('主星', {}).items():
        if zhi == ming_zhi:
            stars.append(star)
    return stars


def _cross_validate(dm, sun_sign, hd_type, authority, moon_sign='', ming_stars=None, dayun_relation=''):
    """跨系統信號交叉驗證 v2：找出一致性與矛盾點"""
    signals = []
    conflicts = []
    ming_stars = ming_stars or []

    # ① 行動力：八字陰陽干 vs HD 類型
    active_dm = dm in '甲丙庚壬'
    active_hd = hd_type in ('顯示者', '顯示生產者')
    if active_dm and active_hd:
        signals.append('八字×人類圖：雙重主動型，天生適合發起與推進')
    elif not active_dm and not active_hd:
        signals.append('八字×人類圖：雙重回應型，等待時機出手比主動衝更有力')
    elif active_dm and not active_hd:
        conflicts.append(f'八字{dm}陽干主動 vs 人類圖「{hd_type}」建議等待——內有矛盾，練習先感受再行動')
    elif not active_dm and active_hd:
        conflicts.append(f'八字{dm}陰干偏被動 vs 人類圖「{hd_type}」需主動告知——需刻意練習清晰表達意圖')

    # ② HD 權威與月亮星座一致性
    if '情緒' in authority and moon_sign in ('天蠍', '雙魚', '巨蟹', '天秤'):
        signals.append(f'HD情緒權威×月亮{moon_sign}：情感敏銳度超高，需要充足消化時間再做決定')
    elif '薦骨' in authority:
        signals.append(f'HD薦骨權威：腹部直覺「嗯/不」是最準確的導航系統')
    elif '直覺' in authority:
        signals.append(f'HD直覺權威×月亮{moon_sign}：瞬間直覺比反覆思考更可靠')

    # ③ 太陽星座與八字日主五行的一致/矛盾
    dm_wx = WUXING_MAP.get(dm, '')
    fire_signs  = ('牡羊', '獅子', '射手')
    earth_signs = ('金牛', '處女', '摩羯')
    air_signs   = ('雙子', '天秤', '水瓶')
    water_signs = ('巨蟹', '天蠍', '雙魚')

    if dm_wx == '火' and sun_sign in fire_signs:
        signals.append(f'八字火{dm}×太陽{sun_sign}：火系能量爆滿，熱情感染力是你最大武器')
    elif dm_wx == '水' and sun_sign in water_signs:
        signals.append(f'八字水{dm}×太陽{sun_sign}：水系直覺極深，情感洞察力超乎常人')
    elif dm_wx == '木' and sun_sign in air_signs:
        signals.append(f'八字木{dm}×太陽{sun_sign}：思維靈動，創新與溝通是你的核心競爭力')
    elif dm_wx == '金' and sun_sign in earth_signs:
        signals.append(f'八字金{dm}×太陽{sun_sign}：務實精準，天生適合需要紀律與決斷的領域')

    # ④ 紫微命宮主星與八字日主的交叉
    STAR_DM_SYNERGY = {
        ('紫微', '壬'): '紫微命宮×壬水日主：帝王格局加上江河氣度，天生領導大格局',
        ('紫微', '庚'): '紫微命宮×庚金日主：霸氣加鋒芒，執行力超強，適合管理層',
        ('天機', '甲'): '天機命宮×甲木日主：謀略加上成長性，適合長線規劃',
        ('太陽', '丙'): '太陽命宮×丙火日主：雙重陽光能量，公眾影響力強',
        ('七殺', '庚'): '七殺命宮×庚金日主：雙重剛烈，衝勁滿點，需注意衝動決策',
        ('破軍', '壬'): '破軍命宮×壬水日主：破舊立新，適合在動盪環境中開創',
        ('貪狼', '癸'): '貪狼命宮×癸水日主：才華橫溢，桃花運與藝術天分俱佳',
        ('天梁', '己'): '天梁命宮×己土日主：慈悲包容，天生輔導與照顧他人的能力',
    }
    for star in ming_stars:
        key = (star, dm)
        if key in STAR_DM_SYNERGY:
            signals.append(STAR_DM_SYNERGY[key])
            break

    # ⑤ 大運十神對整體命局的影響評語
    if dayun_relation in ('食神', '傷官'):
        signals.append(f'大運走{dayun_relation}：創意與表達進入高峰，副業/創作是此階段重點')
    elif dayun_relation in ('正財', '偏財'):
        signals.append(f'大運走{dayun_relation}：財星入運，物質機遇明顯，適合理財投資')
    elif dayun_relation in ('正印', '偏印'):
        signals.append(f'大運走{dayun_relation}：學習與貴人運旺，適合進修充電')
    elif dayun_relation in ('正官', '七殺'):
        signals.append(f'大運走{dayun_relation}：事業壓力增大但也帶來晉升機遇，適合積極求職/升職')

    return signals, conflicts


def generate_portrait(lunar, bazi, astrology, ziwei, humandesign, xingxiu,
                      dayun=None, daxian=None,
                      liunian=None, shengci=None,
                      xiaoxian=None, incarnation_cross=None,
                      struct=None, liunian_sihua=None,
                      channel_themes=None,
                      aspects=None, daxian_sihua=None,
                      liuyue=None, kongwang=None):
    """五系統整合畫像引擎 v7"""

    dm          = bazi.get('day_master', '')
    sun_sign    = astrology.get('太陽',  {}).get('sign', '')
    moon_sign   = astrology.get('月亮',  {}).get('sign', '')
    venus_sign  = astrology.get('金星',  {}).get('sign', '')
    mercury_sign= astrology.get('水星',  {}).get('sign', '')
    hd_type     = humandesign.get('energy_type', '')
    authority   = humandesign.get('authority', '')
    profile     = humandesign.get('profile', '')
    zw_ming     = ziwei.get('命宮', '')

    # 旺弱分析
    strength, strength_label = _day_master_strength(bazi)
    dm_desc = OUTER_MAP.get(dm, '獨特的能量')

    # 命宮主星
    ming_stars = _mingong_stars(ziwei)
    ming_star_primary = ming_stars[0] if ming_stars else ''
    ming_star_desc, ming_star_warn = MINGONG_STAR_DESC.get(ming_star_primary, ('', '')) if ming_star_primary else ('', '')

    # 大運分析
    dayun_relation, dayun_desc = _dayun_analysis(dayun, dm)

    # 跨系統交叉驗證
    signals, conflicts = _cross_validate(
        dm, sun_sign, hd_type, authority,
        moon_sign=moon_sign,
        ming_stars=ming_stars,
        dayun_relation=dayun_relation,
    )

    # ── 缺點（依旺弱調整）──
    if strength in ('strong', 'slightly_strong'):
        weakness_map = {
            '庚': '過強則剛愎、難以妥協，遇挫容易走極端',
            '甲': '旺木易固執，看不慣別人的節奏',
            '丙': '旺火發散、說多做少，容易過度承諾',
            '壬': '旺水話多、方向太多反而無法落地',
            '戊': '旺土過於自我，執行力強但不善傾聽',
        }
        weakness = weakness_map.get(dm, f"{'旺' if strength=='strong' else '偏旺'}時容易自我中心、忽略他人感受")
    elif strength in ('weak', 'slightly_weak'):
        weakness_map = {
            '乙': '弱木缺根基，容易被他人意見左右',
            '己': '弱土缺能量，承擔過多後容易崩潰',
            '丁': '弱火容易情緒化，過度在意外在評價',
            '癸': '弱水直覺敏銳但信心不足，決策常猶豫',
            '辛': '弱金易受傷，玻璃心需要刻意建立安全感',
        }
        weakness = weakness_map.get(dm, f"{'身弱' if strength=='weak' else '偏弱'}時需要外力支持，自信心是終生課題")
    else:
        weakness = "中和命局：優點與缺點都在中庸範圍，但也容易缺乏鮮明個性"

    # ── 五大維度整合卡片 ──
    outer_text = f"{dm_desc} ／ 太陽{sun_sign}座 ／ {strength_label}命格"
    if ming_star_primary:
        inner_text = (f"月亮{moon_sign}座的安全感需求 ／ 紫微{zw_ming}命宮"
                      f"（{ming_star_primary}：{ming_star_desc}）")
    else:
        inner_text = f"月亮{moon_sign}座的安全感需求，搭配紫微{zw_ming}的人生格局"
    action_text = (
        f"{hd_type} {profile} · 策略：{humandesign.get('strategy', '未知')}"
        f" · 權威：{authority}"
    )
    think_text = (
        f"水星{mercury_sign}座思維模式："
        + ('直覺跳躍式' if mercury_sign in ('射手', '水瓶', '雙子')
           else '情感導向' if mercury_sign in ('巨蟹', '雙魚', '天蠍')
           else '實事求是型')
    )
    relation_text = (
        f"金星{venus_sign}座："
        + ('渴望刺激與自由' if venus_sign in ('射手', '雙子', '水瓶')
           else '忠誠穩定型' if venus_sign in ('金牛', '摩羯')
           else '深度連結型')
        + f"，星宿{xingxiu}宿能量加持"
    )

    # ── 五行缺失 ──
    _zhx_map = {
        '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水', '子': '水', '丑': '土',
    }
    present = set()
    for k in ('year', 'month', 'day', 'hour'):
        v = bazi.get(k, '')
        if v:
            present.add(WUXING_MAP.get(v[0], ''))
            present.add(_zhx_map.get(v[-1], ''))
    present.discard('')
    missing_wx = {'木', '火', '土', '金', '水'} - present

    _wx_remedy = {
        '木': ('🌿', '補木：多接觸植物、學習創意技能，或培養長期目標感'),
        '火': ('🕯️', '補火：增加社交活動、運動排汗，或找到讓你興奮的事'),
        '土': ('🪨', '補土：建立日常規律、學習理財，或照料一個生命（植物/動物）'),
        '金': ('⚔️', '補金：學習一項需要紀律的技藝，斷捨離，或培養決策力'),
        '水': ('💧', '補水：多喝水、閱讀哲學/心理/財務類書籍，或靠近水邊'),
    }

    # ── 處方籤 ──
    prescriptions = []
    wx_actions = {
        '木': ('🌲', '接地森林療法', '每週走進山林，或在室內擺放真植——木系能量讓你思路清晰。'),
        '火': ('🔥', '陽光排汗法', '每天 20 分鐘陽光 + 適度運動，火系能量需要流動才不會過熱。'),
        '土': ('⛰️', '接地氣', '赤腳踩草地或沙灘，大地穩定土系能量，排解堆積的壓力。'),
        '金': ('💎', '極簡斷捨離', '定期清空桌面與手機，金系需要純淨空間才能發揮鋒芒。'),
        '水': ('💧', '流水冥想', '泡澡或聽流水聲，水系靈魂需要流動——靜止會停滯。'),
    }
    wx_desc = WUXING_MAP.get(dm, '')
    if wx_desc in wx_actions:
        icon, title, desc = wx_actions[wx_desc]
        prescriptions.append({'icon': icon, 'title': title, 'desc': desc})

    if '情緒' in authority:
        prescriptions.append({'icon': '😴', 'title': '重大決定睡一覺', 'desc': '情緒波需要沉澱。晚上 11 點後不回重要訊息，隔天再說。'})
    elif '薦骨' in authority:
        prescriptions.append({'icon': '🤔', 'title': '聽腹部的聲音', 'desc': '不需要理由，薦骨的「嗯」或「唔唔」就是最準確的GPS。'})
    elif '直覺' in authority:
        prescriptions.append({'icon': '⚡', 'title': '相信第一直覺', 'desc': '你的脾/直覺中心反應最快，過度思考反而會偏離最佳答案。'})

    prescriptions.append({'icon': '✨', 'title': f'{xingxiu}宿冥想', 'desc': f'你是{xingxiu}宿，天生帶有特定宇宙使命。每晚入睡前靜心三分鐘，接通本命能量。'})

    for wx in sorted(missing_wx):
        if wx in _wx_remedy:
            icon, desc = _wx_remedy[wx]
            prescriptions.append({'icon': icon, 'title': f'命缺{wx}·補充建議', 'desc': desc})

    # ── 跨系統信號摘要 ──
    insight_lines = []
    if signals:
        insight_lines.append('✅ 多系統一致信號：' + ' / '.join(signals[:3]))
    if conflicts:
        insight_lines.append('⚠️ 系統矛盾點：' + ' / '.join(conflicts[:2]))
    if missing_wx:
        insight_lines.append(
            '🔍 命缺五行：' + '、'.join(f'{w}行' for w in sorted(missing_wx))
            + '——這些是你人生中需要刻意補充的能量維度'
        )
    if ming_star_warn:
        insight_lines.append(f'🌟 命宮{ming_star_primary}提醒：{ming_star_warn}')

    # ── 人生課題（靜態命格）──
    if strength == 'strong':
        life_topic = (f"【身強命格】{dm_desc}，能量充沛——課題是「放手」。"
                      f"學會讓他人有空間，不用你的方式為所有人解決問題。"
                      f"{sun_sign}座是你的舞台，{moon_sign}月亮提醒你也要向內看。")
    elif strength == 'slightly_strong':
        life_topic = (f"【偏旺命格】{dm_desc}——有足夠能量推動理想，課題是「適時休息」。"
                      f"不要把忙碌當成自我價值，{sun_sign}座的能量需要出口，而非永遠向外燃燒。")
    elif strength == 'weak':
        life_topic = (f"【身弱命格】{dm_desc}的本質需要環境滋養——課題是「找到你的貴人」。"
                      f"接受幫助不是軟弱，而是智慧。{sun_sign}座指出方向，{moon_sign}月亮的安全感是你的地基。")
    elif strength == 'slightly_weak':
        life_topic = (f"【偏弱命格】{dm_desc}——課題是「建立內在根基」。"
                      f"比起外在成就，先確立自己的價值觀和邊界線。"
                      f"{sun_sign}座的夢想是真實的，只是需要更長的醞釀時間。")
    else:
        life_topic = (f"【中和命格】{dm_desc}，能量平穩——課題是「找到你真正想要的」。"
                      f"既不極旺也不極弱，最大的風險反而是平平過一生。{sun_sign}座在提醒你勇敢選擇。")

    # ── 當前人生階段（大運 + 大限動態）──
    current_phase = {}
    if dayun and dayun.get('current'):
        cur = dayun['current']
        current_phase['dayun'] = {
            'pillar':     cur['pillar'],
            'age_range':  cur['age_range'],
            'relation':   dayun_relation,
            'desc':       dayun_desc,
        }
    if daxian:
        star_str = '·'.join(daxian.get('stars', [])) or '空宮'
        current_phase['daxian'] = {
            'palace_name': daxian['palace_name'],
            'palace_zhi':  daxian['palace_zhi'],
            'theme':       daxian['theme'],
            'stars':       star_str,
            'age_range':   daxian['age_range'],
            'desc': (f"紫微{daxian['palace_name']}大限（{daxian['age_range']}）：{daxian['theme']}"
                     f"，宮中：{star_str}"),
        }

    # ── 格局/喜用神洞察 ──
    if struct:
        ju = struct.get('ju', '')
        xiyong = struct.get('xiyong', [])
        jishen = struct.get('jishen', [])
        xi_roles = struct.get('xi_roles', [])
        if ju:
            insight_lines.append(
                f"📐 命局格局：{ju}｜喜{'、'.join(xiyong) or '—'}行（{'/'.join(xi_roles)}）"
                + (f"｜忌{'、'.join(jishen)}行" if jishen else "")
            )
        sanhe = struct.get('sanhe', [])
        banhe = struct.get('banhe', [])
        if sanhe:
            insight_lines.append(f"🔯 地支三合：{'、'.join(sanhe)}，命盤合局特殊加持")
        elif banhe:
            insight_lines.append(f"🔯 地支半合：{'、'.join(banhe)}，部分合化加持")
        # 若流年喜用神命中
        if liunian and xiyong:
            ly_wx = liunian.get('wx_gan', '')
            if ly_wx in xiyong:
                insight_lines.append(
                    f"✅ {liunian['year']}流年{liunian['pillar']}走喜用神{ly_wx}——命局利年，宜積極行動"
                )
            elif ly_wx in jishen:
                insight_lines.append(
                    f"⚠️ {liunian['year']}流年{liunian['pillar']}走忌神{ly_wx}——宜守不宜攻，謹慎防守"
                )

    # ── 流年運勢（年度動態）──
    annual_fortune = {}
    if struct:
        annual_fortune['bazi_structure'] = struct
    if liunian:
        annual_fortune['liunian'] = liunian
        if liunian.get('desc'):
            insight_lines.append(f"🌀 {liunian['year']}流年{liunian['pillar']}：{liunian['desc']}")
        if liunian.get('zhi_interactions'):
            for iact in liunian['zhi_interactions']:
                insight_lines.append(f"   ↳ 地支互動：{iact}")
    if shengci:
        annual_fortune['shengci'] = shengci
        if shengci.get('active'):
            insight_lines.append(f"✨ 命中神煞：{shengci['desc']}")
    if xiaoxian:
        annual_fortune['xiaoxian'] = xiaoxian
        insight_lines.append(f"⭐ 紫微小限：{xiaoxian['desc']}")
    if liunian_sihua:
        annual_fortune['liunian_sihua'] = liunian_sihua
        for hua_type in ('祿', '權', '科', '忌'):
            item = liunian_sihua.get(hua_type)
            if item and item.get('palace') not in ('未入盤', None):
                insight_lines.append(f"☯ 紫微流年四化：{item['desc']}")
    if incarnation_cross:
        annual_fortune['incarnation_cross'] = incarnation_cross
        insight_lines.append(f"🔯 業力十字：{incarnation_cross['cross_type']}——{incarnation_cross['cross_desc']}")
    if channel_themes:
        annual_fortune['channel_themes'] = channel_themes
        if channel_themes:
            ch = channel_themes[0]
            insight_lines.append(f"⚡ 主要通道：{ch['name']}（閘門{ch['gates'][0]}-{ch['gates'][1]}）——{ch['desc']}")

    # ── 占星相位（只取容差 ≤ 3° 的強相位）──
    if aspects:
        annual_fortune['aspects'] = aspects
        tight = [a for a in aspects if a['orb'] <= 3.0]
        for a in tight[:3]:
            icon = '✅' if a['polarity'] == 'positive' else '⚠️'
            insight_lines.append(f"{icon} 占星相位：{a['desc']}（{a['aspect']},{a['orb']}°）")

    # ── 大限四化（這10年的重點宮位）──
    if daxian_sihua and daxian_sihua.get('sihua'):
        annual_fortune['daxian_sihua'] = daxian_sihua
        for hua_type in ('祿', '忌'):
            item = daxian_sihua['sihua'].get(hua_type)
            if item and item.get('palace') != '未入盤':
                icon = '💰' if hua_type == '祿' else '⚠️'
                insight_lines.append(f"{icon} 大限四化：{item['desc']}")

    # ── 流月分析 ──
    if liuyue and liuyue.get('desc'):
        annual_fortune['liuyue'] = liuyue
        insight_lines.append(f"📅 流月{liuyue['pillar']}（{liuyue['month']}月）：{liuyue['desc']}")

    # ── 空亡（旬空）──
    if kongwang:
        annual_fortune['kongwang'] = kongwang
        if kongwang.get('pillars_in_kong'):
            affected = '、'.join(f"{l}（{v['zhi']}）" for l, v in kongwang['pillars_in_kong'].items())
            insight_lines.append(f"🕳 空亡落柱：{affected}——相關領域能量虛化，需後天刻意經營方能補足。")

    return {
        'integrated_cards': [
            {'title': '外在表現', 'text': outer_text,    'bad': f'注意：{weakness}'},
            {'title': '內在需求', 'text': inner_text,    'bad': '情緒波動時需要「安靜的獨處空間」而非熱鬧的外部刺激。'},
            {'title': '行動策略', 'text': action_text,   'bad': f'非自己主題：{humandesign.get("not_self", "挫敗")}——這是你偏離本性的信號。'},
            {'title': '思維模式', 'text': think_text,    'bad': '容易陷入過度分析，或在情緒高峰做出衝動決定。'},
            {'title': '關係模式', 'text': relation_text, 'bad': '需警惕過度依賴或邊界模糊，健康關係的前提是先愛自己。'},
        ],
        'prescriptions':       prescriptions,
        'cross_insights':      insight_lines,
        'life_topic':          life_topic,
        'current_phase':       current_phase,
        'annual_fortune':      annual_fortune,
        'day_master_strength': {'level': strength, 'note': strength_label},
    }
