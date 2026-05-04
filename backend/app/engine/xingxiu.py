"""二十八星宿計算模組"""

XINGXIU = [
    '角','亢','氐','房','心','尾','箕',      # 東方青龍
    '斗','牛','女','虛','危','室','壁',      # 北方玄武
    '奎','婁','胃','昴','畢','觜','參',      # 西方白虎
    '井','鬼','柳','星','張','翼','軫'       # 南方朱雀
]

# 農曆月起始星宿
MONTH_START = {
    1: 0,   # 正月起角
    2: 14,  # 二月起奎
    3: 16,  # 三月起胃
    4: 18,  # 四月起畢
    5: 20,  # 五月起參
    6: 22,  # 六月起鬼
    7: 25,  # 七月起張
    8: 2,   # 八月起氐
    9: 6,   # 九月起箕
    10: 7,  # 十月起斗
    11: 10, # 十一月起虛
    12: 12, # 十二月起室
}

def get_xingxiu(lunar_month, lunar_day):
    """根據農曆月日查星宿"""
    start = MONTH_START.get(lunar_month, 0)
    idx = (start + lunar_day - 1) % 28
    return XINGXIU[idx]

def relation(x1, x2):
    """星宿關係"""
    idx1 = XINGXIU.index(x1)
    idx2 = XINGXIU.index(x2)
    d = (idx2 - idx1) % 28
    
    if d in [0, 14]:
        return "命之星"
    elif d in [1, 27, 13, 15]:
        return "業胎"
    elif d in [2, 26, 12, 16]:
        return "安壞"
    elif d in [3, 25, 11, 17]:
        return "榮親"
    elif d in [4, 24, 10, 18]:
        return "友衰"
    elif d in [5, 23, 9, 19]:
        return "危成"
    else:
        return "鄰近"
