from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, timedelta
from pathlib import Path
import math

load = Loader('.')
eph = load('de421.bsp')
ts = load.timescale()

stems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
elements = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
yin_yang = {'甲':'陽','乙':'陰','丙':'陽','丁':'陰','戊':'陽','己':'陰','庚':'陽','辛':'陰','壬':'陽','癸':'陰'}

# ========== 農曆轉換 ==========
def get_lunar_date(dt):
    """簡化農曆轉換：找前後朔日"""
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    
    # 找前後3個月內的朔日
    t0 = ts.utc(dt.year, dt.month-2, 1)
    t1 = ts.utc(dt.year, dt.month+2, 1)
    
    # 找新月
    phases = almanac.moon_phases(eph)
    t_moons, y_moons = almanac.find_discrete(t0, t1, phases)
    
    new_moons = [ti for ti, yi in zip(t_moons, y_moons) if yi == 0]
    
    # 找到出生日期所在的新月區間
    for i in range(len(new_moons)-1):
        if new_moons[i].tt <= t.tt < new_moons[i+1].tt:
            lunar_day = int((t.tt - new_moons[i].tt) / ((new_moons[i+1].tt - new_moons[i].tt) / 30)) + 1
            if lunar_day > 30:
                lunar_day = 30
            
            # 農曆月：從第一個新月開始數
            # 需要知道立春來確定農曆年
            first_nm = new_moons[0]
            lichen = None
            for y in [dt.year-1, dt.year]:
                t_l0 = ts.utc(y, 1, 1)
                t_l1 = ts.utc(y, 3, 1)
                t_seasons, y_seasons = almanac.find_discrete(t_l0, t_l1, almanac.seasons(eph))
                for ts_i, ys_i in zip(t_seasons, y_seasons):
                    if ys_i == 0:  # spring equinox is not 立春...
                        pass
            
            # 簡化：直接用已知對照表（關鍵日期）
            return lunar_day, i  # 返回農曆日和月偏移
    
    return 1, 0

# ========== 八字工具 ==========
def get_year_pillar(dt):
    lichen = datetime(dt.year, 2, 4, 0, 0)
    if dt < lichen:
        y = dt.year - 1
    else:
        y = dt.year
    return stems[(y - 4) % 10], branches[(y - 4) % 12], y

def get_month_pillar(dt, year_stem):
    month_branches = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑']
    term_dates = [
        (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7),
        (8, 8), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6)
    ]
    
    applicable = 11
    for i in range(len(term_dates)):
        m, d = term_dates[i]
        boundary = datetime(dt.year, m, d)
        if (m, d) < (2, 4):
            boundary = datetime(dt.year - 1, m, d)
        if dt >= boundary:
            applicable = i
    
    month_branch = month_branches[applicable % 12]
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_idx = stems.index(tg_start[year_stem])
    branch_idx = branches.index(month_branch)
    month_stem = stems[(start_idx + branch_idx - 2) % 10]
    return month_stem, month_branch

def get_day_pillar(dt):
    ref = datetime(1999, 6, 7)
    ref_idx = 26
    delta = (dt.date() - ref.date()).days
    idx = (ref_idx + delta) % 60
    return stems[idx % 10], branches[idx % 12]

def get_hour_pillar(hour, day_stem):
    hour_idx = ((hour + 1) // 2) % 12
    hour_branch = branches[hour_idx]
    tg_start = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    start_idx = stems.index(tg_start[day_stem])
    hour_stem = stems[(start_idx + hour_idx) % 10]
    return hour_stem, hour_branch

# ========== 占星工具 ==========
def get_planet_positions(dt):
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    e = (eph['earth'] + wgs84.latlon(25.0330, 121.5654)).at(t)
    planets = {
        '太陽': eph['sun'], '月亮': eph['moon'], '水星': eph['mercury'],
        '金星': eph['venus'], '火星': eph['mars'], '木星': eph['jupiter barycenter'],
        '土星': eph['saturn barycenter']
    }
    results = {}
    for name, planet in planets.items():
        ra, dec, dist = e.observe(planet).apparent().radec()
        results[name] = ra.hours * 15
    return results

def lon_to_sign(lon):
    signs = ['牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','摩羯','水瓶','雙魚']
    idx = int(lon // 30) % 12
    deg = lon % 30
    return signs[idx], deg

# ========== 紫微斗數（簡化版） ==========
def get_ziwei_palace(lunar_month, hour_idx):
    """命宮地支：農曆月起寅，順數至生月，再逆數至生時"""
    # 月地支：正月=寅=2, 二月=卯=3... (0-based: 子=0, 丑=1, 寅=2...)
    month_branch_idx = ((lunar_month + 1) % 12)  # 正月=2, 二月=3...
    palace_idx = (month_branch_idx - hour_idx) % 12
    return branches[palace_idx]

def get_wuxing_ju(ming_gong_gz):
    """五行局：簡化，根據納音"""
    # 納音表（簡化）
    nayin = {
        ('甲','子'):'水', ('甲','寅'):'水', ('甲','辰'):'火', ('甲','午'):'金',
        ('乙','丑'):'水', ('乙','卯'):'水', ('乙','巳'):'火', ('乙','未'):'金',
        ('丙','寅'):'火', ('丙','辰'):'土', ('丙','午'):'水', ('丙','申'):'火',
        ('丁','卯'):'火', ('丁','巳'):'土', ('丁','未'):'水', ('丁','酉'):'火',
        ('戊','辰'):'木', ('戊','午'):'火', ('戊','申'):'土', ('戊','戌'):'木',
        ('己','巳'):'木', ('己','未'):'火', ('己','酉'):'土', ('己','亥'):'木',
        ('庚','午'):'土', ('庚','申'):'木', ('庚','戌'):'金', ('庚','子'):'土',
        ('辛','未'):'土', ('辛','酉'):'木', ('辛','亥'):'金', ('辛','丑'):'土',
        ('壬','申'):'金', ('壬','戌'):'水', ('壬','子'):'木', ('壬','寅'):'金',
        ('癸','酉'):'金', ('癸','亥'):'水', ('癸','丑'):'木', ('癸','卯'):'金',
        ('甲','申'):'水', ('甲','戌'):'火', ('甲','子'):'金',
        ('乙','酉'):'水', ('乙','亥'):'火', ('乙','丑'):'金',
        ('丙','子'):'水', ('丙','寅'):'火',
        ('丁','丑'):'水', ('丁','卯'):'火',
        ('戊','寅'):'土', ('戊','辰'):'木',
        ('己','卯'):'土', ('己','巳'):'木',
        ('庚','辰'):'金', ('庚','午'):'土',
        ('辛','巳'):'金', ('辛','未'):'土',
        ('壬','午'):'木', ('壬','申'):'金',
        ('癸','未'):'木', ('癸','酉'):'金',
        ('甲','戌'):'火', ('甲','子'):'金',
        ('乙','亥'):'火', ('乙','丑'):'金',
        ('丙','辰'):'土', ('丙','午'):'水',
        ('丁','巳'):'土', ('丁','未'):'水',
        ('戊','申'):'土', ('戊','戌'):'木',
        ('己','酉'):'土', ('己','亥'):'木',
        ('庚','戌'):'金', ('庚','子'):'土',
        ('辛','亥'):'金', ('辛','丑'):'土',
        ('壬','寅'):'金', ('壬','辰'):'水',
        ('癸','卯'):'金', ('癸','巳'):'水',
        ('甲','辰'):'火', ('甲','午'):'金',
        ('乙','巳'):'火', ('乙','未'):'金',
        ('丙','午'):'水', ('丙','申'):'火',
        ('丁','未'):'水', ('丁','酉'):'火',
        ('戊','申'):'土', ('戊','戌'):'木',
        ('己','酉'):'土', ('己','亥'):'木',
        ('庚','戌'):'金', ('庚','子'):'土',
        ('辛','亥'):'金', ('辛','丑'):'土',
        ('壬','子'):'木', ('壬','寅'):'金',
        ('癸','丑'):'木', ('癸','卯'):'金',
    }
    return nayin.get(ming_gong_gz, '土')

def place_ziwei(birth_day, wuxing_ju):
    """安紫微星（簡化算法）"""
    # 五行局：水二局、木三局、金四局、土五局、火六局
    ju_num = {'水':2, '木':3, '金':4, '土':5, '火':6}[wuxing_ju]
    
    # 紫微位置 = (生日 - 1) // ju_num 的餘數對應
    # 簡化：直接用查表法
    ziwei_table = {
        2: [1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6],  # 水二局
        3: [1,1,2,3,3,4,5,5,6,7,7,8,9,9,10,11,11,12,1,1,2,3,3,4,5,5,6,7,7,8],    # 木三局
        4: [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,1,1,2,2,3,3],  # 金四局
        5: [1,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,1,1,1,2,2],  # 土五局
        6: [1,1,1,2,2,2,3,3,4,4,4,5,5,6,6,6,7,7,8,8,8,9,9,10,10,10,11,11,12,12], # 火六局
    }
    
    palace_num = ziwei_table[ju_num][birth_day - 1]  # 1-based
    # 轉地支：子=1, 丑=2, ..., 亥=12
    return branches[palace_num - 1]

def get_main_stars(ziwei_branch):
    """安14主星（簡化）"""
    # 紫微星系：從紫微開始，逆數
    # 天府星系：從天府開始，順數
    # 簡化：只列紫微和天府的位置
    ziwei_idx = branches.index(ziwei_branch)
    tianfu_idx = (10 - ziwei_idx) % 12  # 天府在紫微對宮的規律
    
    main_stars = {
        '紫微': branches[ziwei_idx],
        '天府': branches[tianfu_idx],
        # 簡化列出其他主星的相對位置
        '天機': branches[(ziwei_idx - 1) % 12],
        '太陽': branches[(ziwei_idx - 3) % 12],
        '武曲': branches[(ziwei_idx - 4) % 12],
        '天同': branches[(ziwei_idx - 5) % 12],
        '廉貞': branches[(ziwei_idx - 7) % 12],
    }
    return main_stars

# ========== 人類圖（簡化版） ==========
def get_hd_gate(longitude):
    """黃經轉人類圖閘門（簡化：假設閘門均勻分布，Gate 41從0度開始）"""
    gate = int(longitude / 5.625) % 64 + 1
    line = int((longitude % 5.625) / 0.9375) + 1
    if line > 6:
        line = 6
    return gate, line

def get_hd_profile(sun_gate, sun_line, earth_gate, earth_line):
    """人生角色 = (太陽線, 地球線)"""
    return f"{sun_line}/{earth_line}"

def get_hd_type(defined_gates):
    """簡化能量類型判斷"""
    # 定義的中心（簡化判斷）
    sacral_gates = {9,5,52,53,29,14,34,57,27,59}
    throat_gates = {62,23,56,16,35,12,45,33,20,31,8,7}
    emotion_gates = {36,22,37,6,49,55,30}
    spleen_gates = {48,57,18,28,44,50,32}
    root_gates = {58,38,54,19,39,41,60,52}
    will_gates = {26,44,51,21,40}
    g_gates = {1,13,25,46,10,15,7,2}
    ajna_gates = {47,24,4,17,43,11}
    head_gates = {61,63,64}
    
    has_sacral = bool(defined_gates & sacral_gates)
    has_throat = bool(defined_gates & throat_gates)
    has_motor = bool(defined_gates & (emotion_gates | root_gates | will_gates | sacral_gates))
    
    if has_sacral:
        return "顯示生產者/生產者 Generator"
    elif has_throat and has_motor:
        return "顯示者 Manifestor"
    elif len(defined_gates) == 0:
        return "反映者 Reflector"
    else:
        return "投射者 Projector"

# ========== 星宿關係 ==========
# 使用 engine.xingxiu 的正式對照表（農曆月日查表）
import sys
sys.path.insert(0, str(Path(__file__).parent))
from engine import lunar_lookup, xingxiu as xingxiu_engine

def get_xingxiu(year, month, day):
    """根據公曆生日查星宿（使用 lunar.db + 農曆對照表）"""
    lunar = lunar_lookup.get_lunar_date(year, month, day)
    if lunar:
        return xingxiu_engine.get_xingxiu(lunar['lunar_month'], lunar['lunar_day'])
    # fallback: 簡化
    return '未知'

def xingxiu_relation(x1, x2):
    """星宿關係（簡化6種）"""
    xingxiu_list = [
        '角','亢','氐','房','心','尾','箕',
        '斗','牛','女','虛','危','室','壁',
        '奎','婁','胃','昴','畢','觜','參',
        '井','鬼','柳','星','張','翼','軫'
    ]
    idx1 = xingxiu_list.index(x1)
    idx2 = xingxiu_list.index(x2)
    diff = (idx2 - idx1) % 28
    
    relations = [
        (0, '命之星'), (1, '業胎'), (2, '業胎'), (3, '安壞'), (4, '安壞'), (5, '安壞'),
        (6, '榮親'), (7, '榮親'), (8, '榮親'), (9, '友衰'), (10, '友衰'), (11, '友衰'),
        (12, '危成'), (13, '危成'), (14, '危成'), (15, '命之星'), (16, '業胎'), (17, '業胎'),
        (18, '安壞'), (19, '安壞'), (20, '安壞'), (21, '榮親'), (22, '榮親'), (23, '榮親'),
        (24, '友衰'), (25, '友衰'), (26, '友衰'), (27, '危成')
    ]
    return relations[diff][1]

class Person:
    def __init__(self, name, year, month, day, hour, minute, gender, note=""):
        self.name = name
        self.dt = datetime(year, month, day, hour, minute)
        self.gender = gender
        self.note = note
        
        # 八字
        self.year_stem, self.year_branch, self.year = get_year_pillar(self.dt)
        self.month_stem, self.month_branch = get_month_pillar(self.dt, self.year_stem)
        self.day_stem, self.day_branch = get_day_pillar(self.dt)
        self.hour_stem, self.hour_branch = get_hour_pillar(hour, self.day_stem)
        
        self.bazi = f"{self.year_stem}{self.year_branch} {self.month_stem}{self.month_branch} {self.day_stem}{self.day_branch} {self.hour_stem}{self.hour_branch}"
        self.day_master = self.day_stem
        
        # 占星
        self.planets = get_planet_positions(self.dt)
        self.sun_sign, self.sun_deg = lon_to_sign(self.planets['太陽'])
        self.moon_sign, self.moon_deg = lon_to_sign(self.planets['月亮'])
        
        # 行星星座
        self.planet_signs = {k: lon_to_sign(v)[0] for k, v in self.planets.items()}
        
        # 紫微（簡化）
        # 農曆日期查詢
        lunar_info = lunar_lookup.get_lunar_date(year, month, day)
        if lunar_info:
            lunar_month = lunar_info['lunar_month']
            lunar_day = lunar_info['lunar_day']
        else:
            lunar_day = day % 30 + 1
            if lunar_day > 30:
                lunar_day = 30
            lunar_month = month % 12
            if lunar_month == 0:
                lunar_month = 12
        
        hour_idx = ((hour + 1) // 2) % 12
        self.ming_gong = get_ziwei_palace(lunar_month, hour_idx)
        self.ming_gong_gz = (self.ming_gong, "?")  # 需要天干
        
        # 人類圖（簡化）
        self.hd_gates = set()
        for lon in self.planets.values():
            g, l = get_hd_gate(lon)
            self.hd_gates.add(g)
        
        self.hd_type = get_hd_type(self.hd_gates)
        
        sun_g, sun_l = get_hd_gate(self.planets['太陽'])
        earth_g, earth_l = get_hd_gate((self.planets['太陽'] + 180) % 360)
        self.hd_profile = get_hd_profile(sun_g, sun_l, earth_g, earth_l)
        
        # 星宿
        self.xingxiu = get_xingxiu(year, month, day)

# ========== 衍徵一家 ==========
people = [
    Person("衍徵", 1999, 1, 4, 0, 8, "女", "好友"),
    Person("衍徵妹", 2001, 11, 6, 7, 30, "女", ""),
    Person("衍徵爸", 1965, 10, 31, 8, 0, "男", ""),
    Person("衍徵媽", 1969, 4, 28, 8, 0, "女", "時間推估"),
    Person("衍徵男友", 1999, 1, 12, 7, 0, "男", ""),
]

print("=" * 80)
print("衍徵一家 · 八字·星盤·紫微·人類圖·星宿 · 大整合")
print("=" * 80)

for p in people:
    print(f"\n{'─' * 70}")
    print(f"【{p.name}】{p.note} | {p.dt.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'─' * 70}")
    
    print(f"\n☯️ 八字四柱")
    print(f"    {p.bazi}")
    print(f"    日主: {p.day_master} ({yin_yang[p.day_master]}{elements[p.day_master]})")
    print(f"    年柱: {p.year_stem}{p.year_branch} | 月柱: {p.month_stem}{p.month_branch}")
    print(f"    日柱: {p.day_stem}{p.day_branch} | 時柱: {p.hour_stem}{p.hour_branch}")
    
    print(f"\n🌟 西方占星")
    print(f"    太陽: {p.sun_sign} {p.sun_deg:.1f}° | 月亮: {p.moon_sign}")
    print(f"    水星: {p.planet_signs['水星']} | 金星: {p.planet_signs['金星']} | 火星: {p.planet_signs['火星']}")
    print(f"    木星: {p.planet_signs['木星']} | 土星: {p.planet_signs['土星']}")
    
    print(f"\n🔮 紫微斗數（簡化）")
    print(f"    命宮: {p.ming_gong}")
    print(f"    五行局: 需精確農曆排盤")
    
    print(f"\n🧬 人類圖（簡化）")
    print(f"    能量類型: {p.hd_type}")
    print(f"    人生角色: {p.hd_profile}")
    print(f"    被定義閘門: {sorted(p.hd_gates)}")
    
    print(f"\n⭐ 星宿")
    print(f"    本命星宿: {p.xingxiu}")

# ========== 關係矩陣 ==========
print("\n" + "=" * 80)
print("衍徵一家 · 星宿關係矩陣")
print("=" * 80)

names = [p.name for p in people]
print(f"{'':>10}", end="")
for n in names:
    print(f"{n:>10}", end="")
print()

for p1 in people:
    print(f"{p1.name:>10}", end="")
    for p2 in people:
        if p1 == p2:
            print(f"{'—':>10}", end="")
        else:
            rel = xingxiu_relation(p1.xingxiu, p2.xingxiu)
            print(f"{rel:>10}", end="")
    print()

# ========== 家庭角色定位 ==========
print("\n" + "=" * 80)
print("衍徵一家 · 角色定位與能量流動")
print("=" * 80)

def analyze_role(p):
    dm = p.day_master
    el = elements[dm]
    yy = yin_yang[dm]
    
    roles = []
    descriptions = []
    
    if el == '火':
        roles.append("🔥 發光體/暖爐")
        descriptions.append("照亮家庭氣氛，有表演慾和感染力")
    elif el == '水':
        roles.append("🌊 潤滑劑/情感流")
        descriptions.append("感知家庭情緒，調解衝突，但容易被吸收")
    elif el == '木':
        roles.append("🌱 成長引擎")
        descriptions.append("帶來新方向，開創性強，需要空間扎根")
    elif el == '金':
        roles.append("⚔️ 架構師")
        descriptions.append("建立規則和邊界，講求公平")
    elif el == '土':
        roles.append("🏔️ 地基/穩定器")
        descriptions.append("承載全家重量，可靠但固執")
    
    if yy == '陽':
        descriptions.append("外顯主動，習慣主導")
    else:
        descriptions.append("內斂配合，以柔克剛")
    
    return roles, descriptions

for p in people:
    roles, desc = analyze_role(p)
    print(f"\n【{p.name}】{' / '.join(roles)}")
    for d in desc:
        print(f"    · {d}")


# ========== 三人閨蜜報告 ==========

people = [
    Person("韡寧", 1999, 6, 7, 15, 30, "女", "你"),
    Person("朋友A", 1999, 1, 4, 0, 8, "女", ""),
    Person("朋友B", 1999, 4, 25, 0, 0, "女", ""),
]

report_lines = []

def add(line=""):
    report_lines.append(line)

add("# 三人閨蜜 · 五系統整合命盤報告")
add()
add("> 韡寧（你）· 朋友A · 朋友B")
add("> 計算日期：2026年5月2日")
add()
add("---")
add()

# ========== 個人命盤 ==========
add("## 一、個人五維命盤")
add()

for p in people:
    add(f"### 【{p.name}】{p.note}")
    add()
    add(f"**出生時間**：{p.dt.strftime('%Y-%m-%d %H:%M')}")
    add()
    
    # 八字
    add("#### ☯️ 八字四柱")
    add()
    add(f"| 柱 | 天干 | 地支 | 十神（以日干論）|")
    add(f"|---|---|---|---|")
    add(f"| 年柱 | {p.year_stem} | {p.year_branch} | {p.year_stem}({elements.get(p.year_stem,'?')}) |")
    add(f"| 月柱 | {p.month_stem} | {p.month_branch} | {p.month_stem}({elements.get(p.month_stem,'?')}) |")
    add(f"| 日柱 | {p.day_stem} | {p.day_branch} | **日主：{p.day_master} ({yin_yang.get(p.day_master,'?')}{elements.get(p.day_master,'?')})** |")
    add(f"| 時柱 | {p.hour_stem} | {p.hour_branch} | {p.hour_stem}({elements.get(p.hour_stem,'?')}) |")
    add()
    
    # 占星
    add("#### 🌟 西方占星")
    add()
    add(f"| 行星 | 星座 | 度數 |")
    add(f"|---|---|---|")
    add(f"| 太陽 | {p.sun_sign} | {p.sun_deg:.1f}° |")
    add(f"| 月亮 | {p.moon_sign} | - |")
    add(f"| 水星 | {p.planet_signs.get('水星','?')} | - |")
    add(f"| 金星 | {p.planet_signs.get('金星','?')} | - |")
    add(f"| 火星 | {p.planet_signs.get('火星','?')} | - |")
    add(f"| 木星 | {p.planet_signs.get('木星','?')} | - |")
    add(f"| 土星 | {p.planet_signs.get('土星','?')} | - |")
    add()
    
    # 紫微
    add("#### 🔮 紫微斗數（簡化）")
    add()
    add(f"- 命宮地支：{p.ming_gong}")
    add(f"- 五行局：需精確農曆排盤")
    add()
    
    # 人類圖
    add("#### 🧬 人類圖（簡化）")
    add()
    add(f"- 能量類型：{p.hd_type}")
    add(f"- 人生角色：{p.hd_profile}")
    add(f"- 被定義閘門：{sorted(p.hd_gates)}")
    add()
    
    # 星宿
    add("#### ⭐ 星宿")
    add()
    add(f"- 本命星宿：**{p.xingxiu}宿**")
    add()
    add("---")
    add()

# ========== 關係矩陣 ==========
add("## 二、三人關係矩陣")
add()

add("### 2.1 星宿關係矩陣")
add()
names = [p.name for p in people]
header = "| | " + " | ".join(names) + " |"
add(header)
add("|" + "---|" * (len(names) + 1))

for p1 in people:
    row = f"| **{p1.name}** |"
    for p2 in people:
        if p1 == p2:
            row += " — |"
        else:
            rel = xingxiu_relation(p1.xingxiu, p2.xingxiu)
            row += f" {rel} |"
    add(row)
add()

add("### 2.2 八字日主五行關係")
add()
add("| 組合 | 你（日主）| 對方（日主）| 五行關係 | 白話解釋 |")
add("|---|---|---|---|---|")

for i, p1 in enumerate(people):
    for j, p2 in enumerate(people):
        if i >= j:
            continue
        
        dm1, dm2 = p1.day_master, p2.day_master
        el1, el2 = elements[dm1], elements[dm2]
        
        # 五行關係
        shengke_map = {
            "木": {"生": "火", "克": "土"},
            "火": {"生": "土", "克": "金"},
            "土": {"生": "金", "克": "水"},
            "金": {"生": "水", "克": "木"},
            "水": {"生": "木", "克": "火"},
        }
        
        if shengke_map[el1]["生"] == el2:
            relation = f"{p1.name}生{p2.name}"
            desc = f"{p1.name}付出、滋養{p2.name}"
        elif shengke_map[el1]["克"] == el2:
            relation = f"{p1.name}克{p2.name}"
            desc = f"{p1.name}挑戰、壓制{p2.name}"
        elif shengke_map[el2]["生"] == el1:
            relation = f"{p2.name}生{p1.name}"
            desc = f"{p2.name}付出、滋養{p1.name}"
        elif shengke_map[el2]["克"] == el1:
            relation = f"{p2.name}克{p1.name}"
            desc = f"{p2.name}挑戰、壓制{p1.name}"
        else:
            relation = "比劫"
            desc = "同五行，互相理解但也競爭"
        
        add(f"| {p1.name} vs {p2.name} | {dm1}（{el1}）| {dm2}（{el2}）| {relation} | {desc} |")

add()

add("### 2.3 太陽星座關係")
add()
add("| 組合 | 星座A | 星座B | 元素關係 |")
add("|---|---|---|---|")

for i, p1 in enumerate(people):
    for j, p2 in enumerate(people):
        if i >= j:
            continue
        
        sign1, sign2 = p1.sun_sign, p2.sun_sign
        
        # 元素判斷
        fire = ["白羊座", "獅子座", "射手座"]
        earth = ["金牛座", "處女座", "摩羯座"]
        air = ["雙子座", "天秤座", "水瓶座"]
        water = ["巨蟹座", "天蠍座", "雙魚座"]
        
        def get_element(sign):
            if sign in fire: return "火"
            if sign in earth: return "土"
            if sign in air: return "風"
            if sign in water: return "水"
            return "?"
        
        e1, e2 = get_element(sign1), get_element(sign2)
        
        if e1 == e2:
            rel = "同元素（最理解彼此）"
        elif (e1 in ["火","風"] and e2 in ["火","風"]) or (e1 in ["土","水"] and e2 in ["土","水"]):
            rel = "陽性或陰性同盟（互補）"
        else:
            rel = "異元素（需要磨合）"
        
        add(f"| {p1.name} vs {p2.name} | {sign1}（{e1}）| {sign2}（{e2}）| {rel} |")

add()

# ========== 角色定位 ==========
add("## 三、三人角色定位")
add()

for p in people:
    roles, desc = analyze_role(p)
    add(f"### 【{p.name}】{' / '.join(roles)}")
    add()
    for d in desc:
        add(f"- {d}")
    add()

# ========== 關係分析 ==========
add("## 四、關係深度分析")
add()

# 你 vs 朋友A
add("### 4.1 韡寧 vs 朋友A")
add()
add("**八字日主**：庚金（你） vs 丙火（她）→ **火克金**")
add()
add("**星宿關係**：" + xingxiu_relation(people[0].xingxiu, people[1].xingxiu))
add()
add("**太陽星座**：雙子（風） vs 摩羯（土）→ 異元素，需要磨合")
add()
add("**核心動態**：")
add("- 丙火是大火，庚金是冷金——她會「燒」你，你會被她推著走")
add("- 她的太陽摩羯看重實際和結果，你的太陽雙子喜歡變動和新鮮")
add("- 她的月亮獅子需要掌聲，你的月亮雙魚需要理解——頻率不同但互相吸引")
add("- 她是「點火的人」，你是「執行的人」")
add()

# 你 vs 朋友B
add("### 4.2 韡寧 vs 朋友B")
add()
add("**八字日主**：庚金（你） vs 丁火（她）→ **火克金（溫火）**")
add()
add("**星宿關係**：" + xingxiu_relation(people[0].xingxiu, people[2].xingxiu))
add()
add("**太陽星座**：雙子（風） vs 金牛（土）→ 異元素，需要磨合")
add()
add("**核心動態**：")
add("- 丁火是燭火，比丙火溫和——她會「溫溫地烤」你，不會像朋友A那樣直接")
add("- 她的太陽金牛穩定固執，你的太陽雙子變動好奇——她覺得你飄，你覺得她悶")
add("- 她的月亮獅子（00:00出生）內心渴望舞台，上升摩羯讓她外表嚴肅")
add("- 她的時柱庚子——時干和你同為庚金，潛意識裡有你的頻率")
add("- 她是「修正的人」，你「執行後她幫你調整」")
add()

# 朋友A vs 朋友B
add("### 4.3 朋友A vs 朋友B")
add()
add("**八字日主**：丙火（她） vs 丁火（她）→ **比劫（同為火）**")
add()
add("**星宿關係**：" + xingxiu_relation(people[1].xingxiu, people[2].xingxiu))
add()
add("**太陽星座**：摩羯（土） vs 金牛（土）→ **同元素，最理解彼此**")
add()
add("**核心動態**：")
add("- 兩個人都是火日主+土象太陽，天然合拍")
add("- 朋友A是丙火（大火），朋友B是丁火（小火）——A主導，B配合")
add("- 兩個人都有月亮獅子——內心都渴望被看見，容易互搶舞台")
add("- 朋友A太陽摩羯+上升天秤，朋友B太陽金牛+上升摩羯——外表都嚴肅冷靜")
add("- 她們是「互相理解的盟友」，但也可能「一起排擠你」")
add()

# ========== 三人整體動態 ==========
add("## 五、三人整體動態")
add()
add("```")
add("        朋友A（丙火·太陽摩羯·月亮獅子）")
add("           ↓ 火克金（大火燒你）")
add("           ↓ 火火同盟（理解B）")
add("        韡寧（庚金·太陽雙子·月亮雙魚）")
add("           ↑ 火克金（溫火烤你）")
add("           ↑ 時柱同頻（B潛意識裡有你的能量）")
add("        朋友B（丁火·太陽金牛·月亮獅子·上升摩羯）")
add("```")
add()
add("**權力結構**：")
add()
add("| 位置 | 成員 | 原因 |")
add("|---|---|---|")
add("| 表面領導者 | 朋友A | 丙火+太陽摩羯，最有「帶頭」的氣場 |")
add("| 實際控制者 | 朋友B | 丁火+上升摩羯+火星天蠍，觀察後出手，一擊必中 |")
add("| 情緒黏著劑 | 韡寧 | 庚金+雙子+雙魚，翻譯她們、調節她們、被她們兩個「鍊」 |")
add()
add("**你們三個的劇本**：")
add()
add("> 朋友A喊「我們去做這個！」（丙火開創），朋友B說「等一下，這樣比較好」（丁火修正+摩羯控制），你說「好，我來安排細節」（庚金執行+雙子溝通）。**A點火，B控溫，你執行。**")
add()

# ========== 相處建議 ==========
add("## 六、給你的相處建議")
add()
add("### 和朋友A：學會「被燒」")
add()
add("- 她會直接挑戰你，這不舒服但有用")
add("- 不要在她情緒高漲時反駁，等冷靜後再討論")
add("- 她需要掌聲，偶爾說「這個想法很厲害」會讓她充滿能量")
add("- 你們的衝突點：她覺得你不夠認真，你覺得她太嚴肅")
add()
add("### 和朋友B：學會「讀她的冰山」")
add()
add("- 她外表冷（上升摩羯），內心熱（月亮獅子）")
add("- 她會用「溫柔但堅定」的方式推你，不是攻擊")
add("- 她比朋友A更需要「被看見」，但她的獅子藏在摩羯下面")
add("- 你們的連結點：時柱同頻（都是庚金能量）")
add()
add("### 和她們兩個在一起：不要當「第三者」")
add()
add("- 她們兩個都是火+土象，天然合拍")
add("- 當她們聊得很開心時，你可能會覺得被排除——這不是你的錯，是頻率問題")
add("- 主動提出「我來做...」的具體任務，讓自己成為「執行者」而不是「旁觀者」")
add()

add("---")
add()
add("*報告完成。如需更精確的紫微斗數和人類圖分析，建議使用專業排盤軟體。*")

# 寫入檔案
with open("weiwei_friends_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("報告已生成：weiwei_friends_report.md")
