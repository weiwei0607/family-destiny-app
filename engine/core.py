"""Family Destiny Engine - Core Module"""
from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, date
from functools import lru_cache

# Lazy loading: 只在第一次使用時載入 16MB 星曆檔，避免反覆 I/O
_load = None
_eph = None
_ts = None

def _ensure_loaded():
    global _load, _eph, _ts
    if _eph is None:
        _load = Loader('.')
        _eph = _load('de421.bsp')
        _ts = _load.timescale()

def get_eph():
    _ensure_loaded()
    return _eph

def get_ts():
    _ensure_loaded()
    return _ts

def get_observer(lat=25.0330, lon=121.5654):
    eph = get_eph()
    return eph['earth'] + wgs84.latlon(lat, lon)

gan = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
zhi = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

_WX_MAP = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
_SHENG  = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
_KE     = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

# 月柱地支對應的節氣起點黃經（節，不是氣）
# 寅月起立春315°，卯月起驚蟄345°，辰月起清明15°...
MONTH_TERM_DEG = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
MONTH_ZHI = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑']

# 節氣名稱對照
TERM_NAMES = {
    315: '立春', 330: '雨水', 345: '驚蟄', 0: '春分', 15: '清明', 30: '穀雨',
    45: '立夏', 60: '小滿', 75: '芒種', 90: '夏至', 105: '小暑', 120: '大暑',
    135: '立秋', 150: '處暑', 165: '白露', 180: '秋分', 195: '寒露', 210: '霜降',
    225: '立冬', 240: '小雪', 255: '大雪', 270: '冬至', 285: '小寒', 300: '大寒'
}


@lru_cache(maxsize=32)
def _solar_terms(year):
    """計算某年24節氣的精確時刻（UTC），返回 [(datetime, 黃經), ...]"""
    ts = get_ts()
    eph = get_eph()
    earth = eph['earth']
    sun = eph['sun']

    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year + 1, 1, 1)
    n = 1000
    times = ts.linspace(t0, t1, n)

    lats, lons, dists = earth.at(times).observe(sun).apparent().ecliptic_latlon(epoch=None)
    lons_deg = lons.degrees % 360

    terms = []
    for target in range(0, 360, 15):
        for i in range(n - 1):
            l0 = float(lons_deg[i])
            l1 = float(lons_deg[i + 1])
            # 處理 360/0 跨越
            if l0 > l1 and l0 > 300 and l1 < 60:
                l1 += 360
            t_adj = target if target >= l0 else target + 360
            if l0 <= t_adj <= l1:
                frac = (t_adj - l0) / (l1 - l0)
                t_term = times[i].tt + frac * (times[i + 1].tt - times[i].tt)
                dt_term = ts.tt_jd(t_term).utc_datetime().replace(tzinfo=None)
                terms.append((dt_term, target))
                break
    terms.sort()
    return terms


def bazi_pillars(dt):
    """計算八字四柱（精確節氣版）"""
    # Strip timezone so naive solar-term datetimes (UTC) can be compared directly
    dt = dt.replace(tzinfo=None) if dt.tzinfo else dt
    year = dt.year

    # --- 年柱：以當年立春為界 ---
    terms_this_year = _solar_terms(year)
    lichen = next((t for t, d in terms_this_year if d == 315), None)  # 當年立春

    if lichen and dt < lichen:
        y = year - 1
    else:
        y = year

    year_g = gan[(y - 4) % 10]
    year_z = zhi[(y - 4) % 12]

    # --- 月柱：精確節氣 ---
    # 需要前後兩年的節氣來確保邊界正確
    all_terms = _solar_terms(year - 1) + terms_this_year + _solar_terms(year + 1)
    month_terms = [(t, d) for t, d in all_terms if d in MONTH_TERM_DEG]
    month_terms.sort()

    month_idx = 11  # 默認丑月
    for i in range(len(month_terms) - 1):
        if month_terms[i][0] <= dt < month_terms[i + 1][0]:
            deg = month_terms[i][1]
            month_idx = MONTH_TERM_DEG.index(deg)
            break

    month_z = MONTH_ZHI[month_idx]

    # 五虎遁
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_idx = gan.index(tg_start[year_g])
    month_g = gan[(start_idx + month_idx) % 10]

    # --- 日柱 ---
    ref = date(1999, 6, 7)
    ref_idx = 26
    delta = (dt.date() - ref).days
    idx = (ref_idx + delta) % 60
    day_g = gan[idx % 10]
    day_z = zhi[idx % 12]

    # --- 時柱 ---
    hi = ((dt.hour + 1) // 2) % 12
    hour_z = zhi[hi]
    tg_hstart = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    hstart_idx = gan.index(tg_hstart[day_g])
    hour_g = gan[(hstart_idx + hi) % 10]

    return {
        'year': f"{year_g}{year_z}", 'month': f"{month_g}{month_z}",
        'day': f"{day_g}{day_z}", 'hour': f"{hour_g}{hour_z}",
        'day_master': day_g, 'day_master_zhi': day_z
    }


def bazi_dayun(dt, gender, current_year=2026):
    """
    計算八字大運（10年週期）

    規則：
    - 陽年干男命 / 陰年干女命 → 順行（往後的節計算）
    - 陰年干男命 / 陽年干女命 → 逆行（往前的節計算）
    - 每3天≈1歲（起運年齡 = 出生到最近節的天數 / 3）
    - 大運天干地支從月柱往後/往前順延

    回傳：
      qiyun_age  起運年齡
      forward    True=順行
      sequence   [{pillar, age_range, start_year, end_year}, ...]  8個大運
      current    當前所在大運（依 current_year 計算）
    """
    dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
    bz = bazi_pillars(dt_naive)
    year_g  = bz['year'][0]
    month_g = bz['month'][0]
    month_z = bz['month'][1]

    is_yang_gan = year_g in '甲丙戊庚壬'
    is_male     = (gender == '男')
    forward     = (is_yang_gan == is_male)   # 陽男陰女 順行

    year = dt_naive.year
    all_terms = _solar_terms(year - 1) + _solar_terms(year) + _solar_terms(year + 1)
    month_terms = sorted(t for t, d in all_terms if d in MONTH_TERM_DEG)

    if forward:
        upcoming = [t for t in month_terms if t > dt_naive]
        ref_dt   = upcoming[0] if upcoming else dt_naive
        days     = (ref_dt - dt_naive).total_seconds() / 86400
    else:
        past     = [t for t in month_terms if t < dt_naive]
        ref_dt   = past[-1] if past else dt_naive
        days     = (dt_naive - ref_dt).total_seconds() / 86400

    qiyun_age = max(1, round(days / 3))

    mg_idx = gan.index(month_g)
    mz_idx = zhi.index(month_z)

    sequence = []
    for i in range(1, 9):
        if forward:
            g = gan[(mg_idx + i) % 10]
            z = zhi[(mz_idx + i) % 12]
        else:
            g = gan[(mg_idx - i) % 10]
            z = zhi[(mz_idx - i) % 12]
        start_age  = qiyun_age + (i - 1) * 10
        start_year = dt_naive.year + start_age
        sequence.append({
            'pillar':     f"{g}{z}",
            'age_range':  f"{start_age}~{start_age + 9}歲",
            'start_year': start_year,
            'end_year':   start_year + 9,
        })

    current_age = current_year - dt_naive.year
    current_dayun = None
    for d in sequence:
        lo = int(d['age_range'].split('~')[0])
        hi = int(d['age_range'].split('~')[1].rstrip('歲'))
        if lo <= current_age <= hi:
            current_dayun = d
            break

    return {
        'qiyun_age': qiyun_age,
        'forward':   forward,
        'sequence':  sequence,
        'current':   current_dayun,
    }


# 月令主氣（月支正氣）
_MONTH_MAIN_QI = {
    '子':'癸','丑':'己','寅':'甲','卯':'乙','辰':'戊','巳':'丙',
    '午':'丁','未':'己','申':'庚','酉':'辛','戌':'戊','亥':'壬',
}

# 地支六合 / 六沖 / 三刑
_ZHI_LIUHE   = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯',
                 '辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
_ZHI_LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
                  '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
_ZHI_XING    = {'寅':{'巳','申'},'巳':{'寅','申'},'申':{'寅','巳'},
                 '丑':{'戌','未'},'戌':{'丑','未'},'未':{'丑','戌'},
                 '子':{'卯'},'卯':{'子'}}

# 地支三合、半合（名稱, 成員集合, 合化五行）
_SANHE_GROUPS = [
    ('申子辰', {'申','子','辰'}, '水'),
    ('亥卯未', {'亥','卯','未'}, '木'),
    ('寅午戌', {'寅','午','戌'}, '火'),
    ('巳酉丑', {'巳','酉','丑'}, '金'),
]
_BANHE_PAIRS = [
    ('申子', {'申','子'}, '水'), ('子辰', {'子','辰'}, '水'), ('申辰', {'申','辰'}, '水'),
    ('亥卯', {'亥','卯'}, '木'), ('卯未', {'卯','未'}, '木'), ('亥未', {'亥','未'}, '木'),
    ('寅午', {'寅','午'}, '火'), ('午戌', {'午','戌'}, '火'), ('寅戌', {'寅','戌'}, '火'),
    ('巳酉', {'巳','酉'}, '金'), ('酉丑', {'酉','丑'}, '金'), ('巳丑', {'巳','丑'}, '金'),
]

# 旬空（空亡）對照：依日柱旬首（甲X），列出旬中空亡的兩個地支
_XUN_KONG = {
    '甲子': ('戌', '亥'),
    '甲戌': ('申', '酉'),
    '甲申': ('午', '未'),
    '甲午': ('辰', '巳'),
    '甲辰': ('寅', '卯'),
    '甲寅': ('子', '丑'),
}
# 每個地支的五行與象意（用於空亡解讀）
_ZHI_MEANING = {
    '子': '水/事業根基', '丑': '土/財庫',  '寅': '木/進取心',  '卯': '木/感情緣分',
    '辰': '土/貴人',     '巳': '火/文書',  '午': '火/名聲',    '未': '土/田宅',
    '申': '金/行動力',   '酉': '金/財運',  '戌': '土/驛馬',    '亥': '水/祖德',
}

def bazi_kongwang(bazi):
    """
    計算八字空亡（旬空）。
    回傳: {xun_head, kong_zhi, pillars_in_kong, desc}
    """
    day = bazi.get('day', '')
    if len(day) < 2:
        return {'xun_head': '', 'kong_zhi': [], 'pillars_in_kong': {}, 'desc': '無法計算空亡'}

    day_gan_ch = day[0]
    day_zhi_ch = day[1]
    if day_gan_ch not in gan or day_zhi_ch not in zhi:
        return {'xun_head': '', 'kong_zhi': [], 'pillars_in_kong': {}, 'desc': ''}

    g_idx = gan.index(day_gan_ch)
    z_idx = zhi.index(day_zhi_ch)
    # 找日柱在六十甲子中的序號
    jiazi_pos = next((n for n in range(60) if n % 10 == g_idx and n % 12 == z_idx), 0)
    xun_idx = jiazi_pos // 10   # 0..5
    # 旬首天干固定是甲，旬首地支 = 旬首的地支
    xun_zhi_idx = (xun_idx * 10) % 12
    xun_head = '甲' + zhi[xun_zhi_idx]
    kong_zhi = list(_XUN_KONG.get(xun_head, ()))

    # 偵測四柱哪些地支空亡
    pillar_keys = {'year': '年柱', 'month': '月柱', 'day': '日柱', 'hour': '時柱'}
    pillars_in_kong = {}
    for k, label in pillar_keys.items():
        z = bazi.get(k, '')[-1:]
        if z in kong_zhi:
            meaning = _ZHI_MEANING.get(z, '')
            pillars_in_kong[label] = {'zhi': z, 'meaning': meaning}

    if pillars_in_kong:
        affected = '、'.join(f"{l}（{v['zhi']}空）" for l, v in pillars_in_kong.items())
        desc = f"日柱{day}入{xun_head}旬，空亡{'/'.join(kong_zhi)}。受影響柱：{affected}。空亡之地支能量虛化，相關生命領域需後天努力彌補。"
    else:
        desc = f"日柱{day}入{xun_head}旬，空亡{'/'.join(kong_zhi)}。四柱均未落空亡，命局較為圓滿。"

    return {
        'xun_head':       xun_head,
        'kong_zhi':       kong_zhi,
        'pillars_in_kong': pillars_in_kong,
        'desc':           desc,
    }


def bazi_structure_analysis(bazi):
    """格局判斷 + 喜用神分析"""
    dm = bazi.get('day_master', '')
    dm_wx = _WX_MAP.get(dm, '')
    if not dm_wx:
        return {'ju': '未知', 'xiyong': [], 'jishen': [], 'xi_roles': [], 'desc': ''}

    month_z  = bazi.get('month', '')[-1:]
    mq_gan   = _MONTH_MAIN_QI.get(month_z, '')
    mq_wx    = _WX_MAP.get(mq_gan, '')

    # ── 格局 ──
    if not mq_wx:
        ju = '雜格'
    elif mq_wx == dm_wx:
        ju = '羊刃格' if dm in '甲丙戊庚壬' else '建祿格'
    elif _SHENG.get(mq_wx) == dm_wx:
        diff = (mq_gan in '甲丙戊庚壬') != (dm in '甲丙戊庚壬')
        ju = '正印格' if diff else '偏印格'
    elif _SHENG.get(dm_wx) == mq_wx:
        same = (mq_gan in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        ju = '食神格' if same else '傷官格'
    elif _KE.get(dm_wx) == mq_wx:
        diff = (mq_gan in '甲丙戊庚壬') != (dm in '甲丙戊庚壬')
        ju = '正財格' if diff else '偏財格'
    elif _KE.get(mq_wx) == dm_wx:
        diff = (mq_gan in '甲丙戊庚壬') != (dm in '甲丙戊庚壬')
        ju = '正官格' if diff else '七殺格'
    else:
        ju = '外格/雜格'

    # ── 簡化旺弱（與 integrator 一致邏輯）──
    _zhx = {'寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土',
            '申':'金','酉':'金','戌':'土','亥':'水','子':'水','丑':'土'}
    hs, hut = 0.0, 0.0
    for k in ('year', 'month', 'hour'):
        g = bazi.get(k, '')[:1]
        wx = _WX_MAP.get(g, '')
        if wx == dm_wx:               hs += 1.0
        elif _SHENG.get(wx) == dm_wx: hs += 1.5
        elif _SHENG.get(dm_wx) == wx: hut += 0.8
        elif _KE.get(wx) == dm_wx:    hut += 1.2
        elif _KE.get(dm_wx) == wx:    hut += 0.4
    for k in ('year', 'month', 'day', 'hour'):
        z = bazi.get(k, '')[-1:]
        wx = _zhx.get(z, '')
        if wx == dm_wx:               hs += 0.8
        elif _SHENG.get(wx) == dm_wx: hs += 1.0
        elif _SHENG.get(dm_wx) == wx: hut += 0.6
        elif _KE.get(wx) == dm_wx:    hut += 0.8
        elif _KE.get(dm_wx) == wx:    hut += 0.3

    # ── 地支三合半合加成 ──
    pillars_zhi = {bazi.get(k, '')[-1:] for k in ('year', 'month', 'day', 'hour')} - {''}
    sanhe_found, banhe_found = [], []

    sanhe_members = set()
    for name, members, wx_result in _SANHE_GROUPS:
        if members.issubset(pillars_zhi):
            if wx_result == dm_wx:               hs += 2.0
            elif _SHENG.get(wx_result) == dm_wx: hs += 1.5
            elif _SHENG.get(dm_wx) == wx_result: hut += 0.8
            elif _KE.get(wx_result) == dm_wx:    hut += 1.5
            sanhe_found.append(f"{name}三合{wx_result}局")
            sanhe_members.update(members)

    for name, members, wx_result in _BANHE_PAIRS:
        if members.issubset(pillars_zhi) and not members.issubset(sanhe_members):
            if wx_result == dm_wx:               hs += 0.8
            elif _SHENG.get(wx_result) == dm_wx: hs += 0.5
            elif _SHENG.get(dm_wx) == wx_result: hut += 0.4
            elif _KE.get(wx_result) == dm_wx:    hut += 0.5
            banhe_found.append(f"{name}半合{wx_result}局")

    diff_score = hs - hut
    if diff_score >= 2.0:    strength = 'strong'
    elif diff_score >= 0.5:  strength = 'slightly_strong'
    elif diff_score <= -2.0: strength = 'weak'
    elif diff_score <= -0.5: strength = 'slightly_weak'
    else:                    strength = 'neutral'

    # ── 喜用神（依旺弱定喜忌角色）──
    all_wx = ['木', '火', '土', '金', '水']
    def _role(wx):
        if wx == dm_wx:               return 'same'   # 比劫
        if _SHENG.get(wx) == dm_wx:   return 'yin'    # 印
        if _SHENG.get(dm_wx) == wx:   return 'shi'    # 食傷
        if _KE.get(dm_wx) == wx:      return 'cai'    # 財
        if _KE.get(wx) == dm_wx:      return 'guan'   # 官殺
        return ''

    if strength in ('strong', 'slightly_strong'):
        xi_roles = {'shi', 'cai', 'guan'}
        ji_roles = {'yin', 'same'}
    elif strength in ('weak', 'slightly_weak'):
        xi_roles = {'yin', 'same'}
        ji_roles = {'shi', 'cai', 'guan'}
    else:
        xi_roles = {'shi', 'cai'}
        ji_roles = set()

    role_label = {'yin':'印','shi':'食傷','cai':'財','guan':'官殺','same':'比劫'}
    xiyong = [wx for wx in all_wx if _role(wx) in xi_roles]
    jishen = [wx for wx in all_wx if _role(wx) in ji_roles]
    xi_roles_display = sorted({role_label[r] for r in xi_roles if r in role_label})

    # ── 調候用神（季節需求優先於旺弱）──
    _SEASON_NEED = {
        '巳': '水', '午': '水', '未': '水',   # 夏月萬物炎熱，首需水調候
        '亥': '火', '子': '火', '丑': '火',   # 冬月天寒地凍，首需火調候
    }
    tiaohou = _SEASON_NEED.get(month_z, '')
    tiaohou_desc = ''
    if tiaohou:
        season = '夏' if month_z in ('巳', '午', '未') else '冬'
        tiaohou_desc = f"{season}月生人，調候首需{tiaohou}行"
        # 若調候用神不在喜用神中，加入（調候優先）
        if tiaohou not in xiyong:
            xiyong = [tiaohou] + xiyong

    _str_label = {'strong':'強','slightly_strong':'偏旺','neutral':'中和','slightly_weak':'偏弱','weak':'弱'}
    combo_notes = sanhe_found + banhe_found
    combo_part  = ('｜合局：' + '、'.join(combo_notes)) if combo_notes else ''
    desc = (f"格局：{ju}｜身{_str_label.get(strength,'')}"
            + combo_part
            + (f"｜調候：{tiaohou_desc}" if tiaohou_desc else "")
            + f"｜喜：{'、'.join(dict.fromkeys(xiyong)) or '無'}行（{'/'.join(xi_roles_display)}）"
            + f"｜忌：{'、'.join(jishen) or '無'}行")

    return {
        'ju':           ju,
        'strength':     strength,
        'xiyong':       list(dict.fromkeys(xiyong)),
        'jishen':       jishen,
        'xi_roles':     xi_roles_display,
        'tiaohou':      tiaohou,
        'tiaohou_desc': tiaohou_desc,
        'sanhe':        sanhe_found,
        'banhe':        banhe_found,
        'desc':         desc,
    }


def bazi_liunian(dt, current_year=2026):
    """流年干支、十神分析 + 地支刑沖合"""
    dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
    bz = bazi_pillars(dt_naive)
    dm = bz['day_master']

    ly_g = gan[(current_year - 4) % 10]
    ly_z = zhi[(current_year - 4) % 12]
    wx_dm = _WX_MAP.get(dm, '')
    wx_ly = _WX_MAP.get(ly_g, '')

    if wx_ly == wx_dm:
        same_yin = (ly_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '比肩' if same_yin else '劫財'
        desc = f"流年{ly_g}({wx_ly})與日主{dm}同氣，{shishen}年：自我意識旺，適合主動出擊"
    elif _SHENG.get(wx_ly) == wx_dm:
        same_yin = (ly_g in '甲丙戊庚壬') != (dm in '甲丙戊庚壬')
        shishen = '正印' if same_yin else '偏印'
        desc = f"流年{ly_g}生日主{dm}，{shishen}年：學習運、貴人運旺，適合進修考證"
    elif _SHENG.get(wx_dm) == wx_ly:
        same_yin = (ly_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '食神' if same_yin else '傷官'
        desc = f"流年{ly_g}被日主{dm}生，{shishen}年：創意輸出與才藝展現高峰"
    elif _KE.get(wx_dm) == wx_ly:
        same_yin = (ly_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '偏財' if same_yin else '正財'
        desc = f"流年{ly_g}被日主{dm}克，{shishen}年：財運機遇佳，適合理財投資"
    elif _KE.get(wx_ly) == wx_dm:
        same_yin = (ly_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '七殺' if same_yin else '正官'
        desc = f"流年{ly_g}克日主{dm}，{shishen}年：壓力與機遇並存，適合求職升職"
    else:
        shishen, desc = '', ''

    # ── 流年地支與本命四柱的刑沖合 ──
    bazi_zhis = [bz.get(k, '')[-1:] for k in ('year', 'month', 'day', 'hour')]
    zhi_interactions = []
    for bz_z in bazi_zhis:
        if not bz_z:
            continue
        if _ZHI_LIUHE.get(ly_z) == bz_z:
            zhi_interactions.append(f"午合{bz_z}（六合，吉：助力相生）" if ly_z == '午'
                                    else f"{ly_z}合{bz_z}（六合，助力相生）")
        if _ZHI_LIUCHONG.get(ly_z) == bz_z:
            zhi_interactions.append(f"{ly_z}沖{bz_z}（六沖，動：帶來變動與轉機）")
        if bz_z in _ZHI_XING.get(ly_z, set()):
            zhi_interactions.append(f"{ly_z}刑{bz_z}（刑：壓力考驗，破後立）")

    return {
        'year':             current_year,
        'pillar':           f"{ly_g}{ly_z}",
        'gan':              ly_g,
        'zhi':              ly_z,
        'wx_gan':           wx_ly,
        'shishen':          shishen,
        'desc':             desc,
        'zhi_interactions': zhi_interactions,
    }


def bazi_liuyue(dt, current_year=2026, current_month=5):
    """流月干支與十神分析（計算當前月柱對日主的十神關係）"""
    dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
    bz = bazi_pillars(dt_naive)
    dm = bz['day_master']

    # 以當月中旬計算月柱（避免節氣邊界誤判）
    lym_bz = bazi_pillars(datetime(current_year, current_month, 15))
    lym_g = lym_bz['month'][0]
    lym_z = lym_bz['month'][1]
    wx_dm  = _WX_MAP.get(dm, '')
    wx_lym = _WX_MAP.get(lym_g, '')

    if wx_lym == wx_dm:
        same_yin = (lym_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '比肩' if same_yin else '劫財'
        desc = f"流月{lym_g}({wx_lym})與日主{dm}同氣，{shishen}月：自信心強，主動時機佳"
    elif _SHENG.get(wx_lym) == wx_dm:
        same_yin = (lym_g in '甲丙戊庚壬') != (dm in '甲丙戊庚壬')
        shishen = '正印' if same_yin else '偏印'
        desc = f"流月{lym_g}生日主{dm}，{shishen}月：思維清晰，學習與考試月"
    elif _SHENG.get(wx_dm) == wx_lym:
        same_yin = (lym_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '食神' if same_yin else '傷官'
        desc = f"流月{lym_g}被日主{dm}生，{shishen}月：創意旺盛，表達力強"
    elif _KE.get(wx_dm) == wx_lym:
        same_yin = (lym_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '偏財' if same_yin else '正財'
        desc = f"流月{lym_g}被日主{dm}克，{shishen}月：財運活躍，適合推進業務"
    elif _KE.get(wx_lym) == wx_dm:
        same_yin = (lym_g in '甲丙戊庚壬') == (dm in '甲丙戊庚壬')
        shishen = '七殺' if same_yin else '正官'
        desc = f"流月{lym_g}克日主{dm}，{shishen}月：壓力月，宜專注手頭任務"
    else:
        shishen, desc = '', ''

    return {
        'month':   current_month,
        'pillar':  f"{lym_g}{lym_z}",
        'gan':     lym_g,
        'zhi':     lym_z,
        'wx_gan':  wx_lym,
        'shishen': shishen,
        'desc':    desc,
    }


def calc_aspects(ast_data):
    """計算行星相位（合相/六分/四分/三分/對分）"""
    ASPECT_DEFS = [
        ('合相',   0,   8.0, 'positive'),
        ('六分相', 60,  6.0, 'positive'),
        ('四分相', 90,  8.0, 'negative'),
        ('三分相', 120, 8.0, 'positive'),
        ('對分相', 180, 8.0, 'negative'),
    ]
    ASPECT_MEANING = {
        '合相':   '{b1}與{b2}能量融合，主題緊密交織',
        '六分相': '{b1}與{b2}輕鬆共鳴，天然助益',
        '四分相': '{b1}與{b2}形成張力，是成長的驅動力',
        '三分相': '{b1}與{b2}自然和諧，天生優勢',
        '對分相': '{b1}與{b2}形成對立，需整合兩種能量',
    }
    bodies = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '上升點']
    lons = {b: ast_data[b]['longitude'] for b in bodies if b in ast_data}
    body_list = list(lons.keys())

    aspects = []
    for i in range(len(body_list)):
        for j in range(i + 1, len(body_list)):
            b1, b2 = body_list[i], body_list[j]
            diff = abs(lons[b1] - lons[b2]) % 360
            if diff > 180:
                diff = 360 - diff
            for name, angle, orb, polarity in ASPECT_DEFS:
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    aspects.append({
                        'body1':    b1,
                        'body2':    b2,
                        'aspect':   name,
                        'orb':      round(actual_orb, 1),
                        'polarity': polarity,
                        'desc':     ASPECT_MEANING[name].format(b1=b1, b2=b2),
                    })
                    break

    aspects.sort(key=lambda x: x['orb'])
    return aspects


def bazi_shengci(bazi):
    """神煞計算：天乙貴人、桃花、驛馬、文昌"""
    dm     = bazi.get('day_master', '')
    year_z = bazi.get('year', '')[-1:]

    # 天乙貴人（依日主天干）
    tianyigui_map = {
        '甲': ('丑','未'), '戊': ('丑','未'), '庚': ('丑','未'),
        '乙': ('子','申'), '己': ('子','申'),
        '丙': ('亥','酉'), '丁': ('亥','酉'),
        '辛': ('午','寅'),
        '壬': ('卯','巳'), '癸': ('卯','巳'),
    }
    tianyigui_zhi = tianyigui_map.get(dm, ())
    tianyigui_present = any(
        bazi.get(k, '')[-1:] in tianyigui_zhi
        for k in ('year', 'month', 'day', 'hour')
    )

    # 桃花（依年支）
    taohua_map = {
        '申':'酉','子':'酉','辰':'酉',
        '寅':'卯','午':'卯','戌':'卯',
        '亥':'子','卯':'子','未':'子',
        '巳':'午','酉':'午','丑':'午',
    }
    taohua_zhi = taohua_map.get(year_z, '')
    taohua_present = bool(taohua_zhi) and any(
        bazi.get(k, '')[-1:] == taohua_zhi
        for k in ('year', 'month', 'day', 'hour')
    )

    # 驛馬（依年支）
    yima_map = {
        '申':'寅','子':'寅','辰':'寅',
        '寅':'申','午':'申','戌':'申',
        '亥':'巳','卯':'巳','未':'巳',
        '巳':'亥','酉':'亥','丑':'亥',
    }
    yima_zhi = yima_map.get(year_z, '')
    yima_present = bool(yima_zhi) and any(
        bazi.get(k, '')[-1:] == yima_zhi
        for k in ('year', 'month', 'day', 'hour')
    )

    # 文昌（依日主天干）
    wenchang_map = {
        '甲':'巳','乙':'午','丙':'申','丁':'酉',
        '戊':'申','己':'酉','庚':'亥','辛':'子',
        '壬':'寅','癸':'卯',
    }
    wenchang_zhi = wenchang_map.get(dm, '')
    wenchang_present = bool(wenchang_zhi) and any(
        bazi.get(k, '')[-1:] == wenchang_zhi
        for k in ('year', 'month', 'day', 'hour')
    )

    result = {
        '天乙貴人': {'zhi': list(tianyigui_zhi), 'present': tianyigui_present},
        '桃花':     {'zhi': taohua_zhi,          'present': taohua_present},
        '驛馬':     {'zhi': yima_zhi,             'present': yima_present},
        '文昌':     {'zhi': wenchang_zhi,         'present': wenchang_present},
    }
    active = [k for k, v in result.items() if v['present']]
    result['active'] = active
    result['desc'] = (
        f"命帶{'、'.join(active)}，先天神煞加持" if active
        else "四大神煞均不在四柱，逢流年地支激活時仍可顯現"
    )
    return result


def western_astrology(dt, lat=25.0330, lon=121.5654):
    import math
    eph = get_eph()
    ts = get_ts()
    obs_lat, obs_lon = lat, lon
    observer = get_observer(obs_lat, obs_lon)
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    e = observer.at(t)
    bodies = {
        '太陽': eph['sun'], '月亮': eph['moon'], '水星': eph['mercury'],
        '金星': eph['venus'], '火星': eph['mars'], '木星': eph['jupiter barycenter'],
        '土星': eph['saturn barycenter']
    }
    signs = ['牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','摩羯','水瓶','雙魚']
    result = {}
    for name, body in bodies.items():
        _lat, body_lon, dist = e.observe(body).apparent().ecliptic_latlon(epoch=None)
        deg = body_lon.degrees % 360
        sign = signs[int(deg // 30) % 12]
        result[name] = {'sign': sign, 'degree': round(deg % 30, 1), 'longitude': deg}

    # ── 上升點 (ASC) ──
    try:
        OBLIQUITY = 23.4397
        gmst     = t.gmst                          # Greenwich Mean Sidereal Time (hours)
        lst_deg  = (gmst * 15 + obs_lon) % 360     # Local Sidereal Time in degrees
        obl_r    = math.radians(OBLIQUITY)
        lat_r    = math.radians(obs_lat)
        lst_r    = math.radians(lst_deg)
        A   = math.cos(lst_r)
        B   = -(math.sin(lst_r) * math.cos(obl_r) + math.tan(lat_r) * math.sin(obl_r))
        asc_deg  = math.degrees(math.atan2(A, B)) % 360
        asc_sign = signs[int(asc_deg // 30) % 12]
        result['上升點'] = {'sign': asc_sign, 'degree': round(asc_deg % 30, 1), 'longitude': asc_deg}
    except Exception:
        pass

    return result
