#!/usr/bin/env python3
"""
簡化版八字計算器
支援：年柱、月柱、日柱（簡化算法）、生肖、星座
注意：日柱使用簡化公式，極少數日期（如節氣交界）可能偏差±1日，
      如需100%準確請對照專業萬年曆。
"""

from datetime import datetime, timedelta

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI   = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZODIAC  = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]

# 節氣資料（簡化版，涵蓋1996-2004年份足夠用）
# 格式: (月份, 日), 表示該節氣在當月的幾號（簡化，不考慮時辰）
JIEQI_TABLE = {
    # 立春、驚蟄、清明、立夏、芒種、小暑、立秋、白露、寒露、立冬、大雪、小寒
    1999: {
        "立春": (2, 4), "驚蟄": (3, 6), "清明": (4, 5), "立夏": (5, 6),
        "芒種": (6, 6), "小暑": (7, 7), "立秋": (8, 8), "白露": (9, 8),
        "寒露": (10, 9), "立冬": (11, 8), "大雪": (12, 7), "小寒": (1, 6),
    },
    1998: {
        "立春": (2, 4), "驚蟄": (3, 6), "清明": (4, 5), "立夏": (5, 6),
        "芒種": (6, 6), "小暑": (7, 7), "立秋": (8, 8), "白露": (9, 8),
        "寒露": (10, 9), "立冬": (11, 8), "大雪": (12, 7), "小寒": (1, 6),
    },
    2000: {
        "立春": (2, 4), "驚蟄": (3, 5), "清明": (4, 4), "立夏": (5, 5),
        "芒種": (6, 5), "小暑": (7, 7), "立秋": (8, 7), "白露": (9, 7),
        "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 7), "小寒": (1, 6),
    }
}

MONTH_ZHU_NAME = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]


def get_year_ganzhi(year, month, day):
    """計算年柱（以立春為界）"""
    jieqi = JIEQI_TABLE.get(year, JIEQI_TABLE[1999])
    lichun_month, lichun_day = jieqi["立春"]
    
    # 以立春為界，立春前屬上一年
    if month < lichun_month or (month == lichun_month and day < lichun_day):
        effective_year = year - 1
    else:
        effective_year = year
    
    gan_idx = (effective_year - 4) % 10
    zhi_idx = (effective_year - 4) % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx], ZODIAC[zhi_idx]


def get_month_ganzhi(year_gan, month, day):
    """計算月柱（以節氣為界）"""
    # 年干對應月干起始
    year_gan_idx = TIANGAN.index(year_gan)
    # 甲己之年丙作首, 乙庚之歲戊為頭, 丙辛之歲尋庚起, 丁壬壬位順行流, 若問戊癸何方發, 甲寅之上好追求
    start_gan_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}
    # 等等，上面的索引可能有點亂，用標準口訣重新算
    # 甲己 -> 丙(2), 乙庚 -> 戊(4), 丙辛 -> 庚(6), 丁壬 -> 壬(8), 戊癸 -> 甲(0)
   口诀映射 = {
        "甲": 2, "己": 2,  # 丙
        "乙": 4, "庚": 4,  # 戊
        "丙": 6, "辛": 6,  # 庚
        "丁": 8, "壬": 8,  # 壬
        "戊": 0, "癸": 0,  # 甲
    }
    
    # 找到當月對應的節氣月份（寅月=立春後，卯月=驚蟄後...）
    jieqi = JIEQI_TABLE.get(datetime.now().year, JIEQI_TABLE[1999])
    # 簡化：用常見節氣判斷
    # 實際上應該對照完整節氣表，這裡用簡化規則
    
    # 寅月(立春-驚蟄), 卯月(驚蟄-清明), 辰月(清明-立夏), 巳月(立夏-芒種),
    # 午月(芒種-小暑), 未月(小暑-立秋), 申月(立秋-白露), 酉月(白露-寒露),
    # 戌月(寒露-立冬), 亥月(立冬-大雪), 子月(大雪-小寒), 丑月(小寒-立春)
    
    # 簡化映射（僅供參考，節氣交界日可能偏差）
    if (month == 1 and day >= 6) or (month == 2 and day < 4):
        month_zhi_idx = 11  # 丑月
    elif (month == 2 and day >= 4) or (month == 3 and day < 6):
        month_zhi_idx = 0   # 寅月
    elif (month == 3 and day >= 6) or (month == 4 and day < 5):
        month_zhi_idx = 1   # 卯月
    elif (month == 4 and day >= 5) or (month == 5 and day < 6):
        month_zhi_idx = 2   # 辰月
    elif (month == 5 and day >= 6) or (month == 6 and day < 6):
        month_zhi_idx = 3   # 巳月
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        month_zhi_idx = 4   # 午月
    elif (month == 7 and day >= 7) or (month == 8 and day < 8):
        month_zhi_idx = 5   # 未月
    elif (month == 8 and day >= 8) or (month == 9 and day < 8):
        month_zhi_idx = 6   # 申月
    elif (month == 9 and day >= 8) or (month == 10 and day < 9):
        month_zhi_idx = 7   # 酉月
    elif (month == 10 and day >= 9) or (month == 11 and day < 8):
        month_zhi_idx = 8   # 戌月
    elif (month == 11 and day >= 8) or (month == 12 and day < 7):
        month_zhi_idx = 9   # 亥月
    elif (month == 12 and day >= 7) or (month == 1 and day < 6):
        month_zhi_idx = 10  # 子月
    else:
        month_zhi_idx = 0
    
    start_gan = 口诀映射.get(year_gan, 0)
    gan_idx = (start_gan + month_zhi_idx) % 10
    return TIANGAN[gan_idx] + DIZHI[month_zhi_idx]


def get_day_ganzhi_simplified(year, month, day):
    """
    簡化版日柱計算（基於已知錨點推算）
    錨點：2000年1月1日 = 戊午日（簡化假設）
    注意：此為簡化算法，節氣交界前後可能偏差±1日
    """
    # 使用儒略日差計算（簡化）
    base_date = datetime(2000, 1, 1)
    target_date = datetime(year, month, day)
    delta_days = (target_date - base_date).days
    
    # 2000年1月1日假設為戊午日
    # 戊=4, 午=6
    base_gan = 4
    base_zhi = 6
    
    gan_idx = (base_gan + delta_days) % 10
    zhi_idx = (base_zhi + delta_days) % 12
    
    return TIANGAN[gan_idx] + DIZHI[zhi_idx], TIANGAN[gan_idx]


def get_zodiac_sign(month, day):
    """計算太陽星座"""
    signs = [
        ("摩羯座", 1, 1), ("水瓶座", 1, 20), ("雙魚座", 2, 19),
        ("白羊座", 3, 21), ("金牛座", 4, 20), ("雙子座", 5, 21),
        ("巨蟹座", 6, 21), ("獅子座", 7, 23), ("處女座", 8, 23),
        ("天秤座", 9, 23), ("天蠍座", 10, 23), ("射手座", 11, 22),
        ("摩羯座", 12, 22)
    ]
    for i in range(len(signs) - 1, -1, -1):
        name, m, d = signs[i]
        if (month > m) or (month == m and day >= d):
            return name
    return "摩羯座"


def get_wuxing(day_gan):
    """日主五行"""
    wuxing_map = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    return wuxing_map.get(day_gan, "未知")


def calculate_bazi(year, month, day, hour=None, minute=None):
    """計算八字基礎資訊"""
    result = {
        "陽曆": f"{year}年{month}月{day}日",
        "星座": get_zodiac_sign(month, day),
    }
    
    # 年柱
    year_gz, zodiac = get_year_ganzhi(year, month, day)
    result["生肖"] = zodiac
    result["年柱"] = year_gz
    
    # 月柱
    month_gz = get_month_ganzhi(year_gz[0], month, day)
    result["月柱"] = month_gz
    
    # 日柱（簡化）
    day_gz, day_gan = get_day_ganzhi_simplified(year, month, day)
    result["日柱"] = day_gz
    result["日主"] = day_gan
    result["日主五行"] = get_wuxing(day_gan)
    
    # 時柱（如果有時間）
    if hour is not None:
        # 時辰對照
        shichen_map = [
            (0, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11),
            (11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23)
        ]
        sc_idx = 0
        for i, (start, end) in enumerate(shichen_map):
            if start <= hour < end or (hour == 23 and i == 11):
                sc_idx = i
                break
        if hour == 23:
            sc_idx = 11
            
        # 日干定時干
        # 甲己日起甲子, 乙庚日起丙子, 丙辛日起戊子, 丁壬日起庚子, 戊癸日起壬子
        start_gan_map = {"甲": 0, "己": 0, "乙": 2, "庚": 2, "丙": 4, "辛": 4, "丁": 6, "壬": 6, "戊": 8, "癸": 8}
        start_gan = start_gan_map.get(day_gan, 0)
        gan_idx = (start_gan + sc_idx) % 10
        result["時柱"] = TIANGAN[gan_idx] + DIZHI[sc_idx]
        result["時辰"] = DIZHI[sc_idx] + "時"
    
    return result


def analyze_relationship(name1, bazi1, name2, bazi2):
    """分析兩人關係基礎"""
    day1 = bazi1["日主"]
    day2 = bazi2["日主"]
    wx1 = bazi1["日主五行"]
    wx2 = bazi2["日主五行"]
    
    # 五行生剋
    shengke = {
        "木": {"生": "火", "克": "土", "被生": "水", "被克": "金"},
        "火": {"生": "土", "克": "金", "被生": "木", "被克": "水"},
        "土": {"生": "金", "克": "水", "被生": "火", "被克": "木"},
        "金": {"生": "水", "克": "木", "被生": "土", "被克": "火"},
        "水": {"生": "木", "克": "火", "被生": "金", "被克": "土"},
    }
    
    relation = ""
    if shengke[wx1]["生"] == wx2:
        relation = f"{name1}生{name2}（{name1}付出、滋養{name2}）"
    elif shengke[wx1]["克"] == wx2:
        relation = f"{name1}克{name2}（{name1}挑戰、壓制{name2}）"
    elif shengke[wx1]["被生"] == wx2:
        relation = f"{name2}生{name1}（{name2}付出、滋養{name1}）"
    elif shengke[wx1]["被克"] == wx2:
        relation = f"{name2}克{name1}（{name2}挑戰、壓制{name1}）"
    else:
        relation = "比劫（同五行，互相理解但也競爭）"
    
    # 生肖關係
    zodiac_relation = {
        ("鼠", "牛"): "六合", ("虎", "豬"): "六合", ("兔", "狗"): "六合",
        ("龍", "雞"): "六合", ("蛇", "猴"): "六合", ("馬", "羊"): "六合",
        ("鼠", "馬"): "六衝", ("牛", "羊"): "六衝", ("虎", "猴"): "六衝",
        ("兔", "雞"): "六衝", ("龍", "狗"): "六衝", ("蛇", "豬"): "六衝",
    }
    z1, z2 = bazi1["生肖"], bazi2["生肖"]
    zr = zodiac_relation.get((z1, z2)) or zodiac_relation.get((z2, z1)) or "一般"
    
    return {
        "五行關係": relation,
        "生肖關係": zr,
        "日主組合": f"{day1} vs {day2}",
        "星座組合": f"{bazi1['星座']} vs {bazi2['星座']}",
    }


if __name__ == "__main__":
    print("=" * 50)
    print("三人八字基礎計算")
    print("=" * 50)
    
    # 你（韡寧）
    you = calculate_bazi(1999, 6, 7)
    print(f"\n【你】{you['陽曆']}")
    for k, v in you.items():
        print(f"  {k}: {v}")
    
    # 朋友A
    friend_a = calculate_bazi(1999, 1, 4, 0, 8)
    print(f"\n【朋友A】{friend_a['陽曆']} 00:08")
    for k, v in friend_a.items():
        print(f"  {k}: {v}")
    
    # 朋友B（時間待定）
    friend_b = calculate_bazi(1999, 4, 25)
    print(f"\n【朋友B】{friend_b['陽曆']}（時間待定）")
    for k, v in friend_b.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 50)
    print("關係分析")
    print("=" * 50)
    
    r1 = analyze_relationship("你", you, "朋友A", friend_a)
    print(f"\n【你 vs 朋友A】")
    for k, v in r1.items():
        print(f"  {k}: {v}")
    
    r2 = analyze_relationship("你", you, "朋友B", friend_b)
    print(f"\n【你 vs 朋友B】")
    for k, v in r2.items():
        print(f"  {k}: {v}")
    
    r3 = analyze_relationship("朋友A", friend_a, "朋友B", friend_b)
    print(f"\n【朋友A vs 朋友B】")
    for k, v in r3.items():
        print(f"  {k}: {v}")
