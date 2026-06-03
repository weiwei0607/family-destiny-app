"""Chart computation service - wraps the destiny engines"""
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, Optional
from app.engine import core, ziwei, humandesign, xingxiu, lunar_lookup, interpretations

LOCATION_COORDS = {
    'taipei': (25.0330, 121.5654),
    'taichung': (24.1477, 120.6736),
    'kaohsiung': (22.6273, 120.3014),
}

def _location_coords(loc_key: str):
    return LOCATION_COORDS.get(loc_key, (25.0330, 121.5654))

def _hour_idx(dt: datetime) -> int:
    return ((dt.hour + 1) // 2) % 12

def _gender_code(g: str) -> str:
    return '男' if g in ('男', 'male', 'M', 'm') else '女'

@lru_cache(maxsize=512)
def _compute_chart_cached(date: str, time: str, location: str, gender_code: str, lang: str) -> Dict[str, Any]:
    """Pure astronomical computation, cached by birth data. Name excluded — it doesn't affect results."""
    dt = datetime.fromisoformat(f"{date}T{time}")
    lat, lon = _location_coords(location)

    bz = core.bazi_pillars(dt)
    ast = core.western_astrology(dt, lat, lon)
    planets_longitudes = {k: v['longitude'] for k, v in ast.items()}

    lunar = lunar_lookup.get_lunar_date(dt.year, dt.month, dt.day)
    if lunar is None:
        lunar = {
            'lunar_year': dt.year, 'lunar_month': dt.month,
            'lunar_day': dt.day, 'lunar_year_gz': bz['year'], 'is_leap_month': False
        }

    try:
        zw = ziwei.ziwei_chart(
            year_gan=bz['year'][0],
            lunar_month=lunar['lunar_month'],
            lunar_day=lunar['lunar_day'],
            hour_idx=_hour_idx(dt),
            gender=gender_code
        )
    except Exception:
        zw = {'命宮': '未知', '身宮': '未知', '五行局': '未知', '紫微': '未知', '天府': '未知', '主星': {}, '輔星': {}, '四化': {}}

    try:
        hd = humandesign.calculate(planets_longitudes)
    except Exception:
        hd = {'energy_type': '未知', 'profile': '未知', 'authority': '未知', 'defined_gates': [], 'active_channels': [], 'defined_centers': [], 'gate_details': {}}

    try:
        xx = xingxiu.get_xingxiu(lunar['lunar_month'], lunar['lunar_day'])
    except Exception:
        xx = '未知'

    defined_centers = hd.get('defined_centers') or []
    main_stars = zw.get('主星') or {}
    energy_score = min(100, 60 + len(defined_centers) * 5 + len([v for v in main_stars.values() if v]) * 2)

    summary = ' · '.join([
        f"{bz['day_master']}日主",
        f"{zw.get('命宮', '未知')}命宮",
        f"{hd.get('energy_type', '未知')}{hd.get('profile', '')}",
        f"{xx}宿"
    ])

    chart_data = {
        "gender": gender_code,
        "bazi": bz,
        "astrology": {k: {"sign": v["sign"], "degree": v["degree"]} for k, v in ast.items()},
        "ziwei": zw,
        "humandesign": hd,
        "xingxiu": xx,
        "lunar": lunar,
        "energy_score": energy_score,
        "summary": summary,
    }
    chart_data["interpretations"] = interpretations.build_free_interpretations(chart_data, lang)
    return chart_data


def compute_basic_chart(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute basic chart data (free tier) - pure code, no AI. Results are cached."""
    cached = _compute_chart_cached(
        date=data['date'],
        time=data.get('time', '12:00'),
        location=data.get('location', 'taipei'),
        gender_code=_gender_code(data.get('gender', '女')),
        lang=data.get('lang', 'zh-TW'),
    )
    # Name is injected after cache lookup — it doesn't affect computation
    return {**cached, "name": data.get('name', '')}


def compute_compatibility_basic(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
    """Compute basic compatibility (free tier) - pure code, no AI"""
    p1 = compute_basic_chart(data1)
    p2 = compute_basic_chart(data2)
    
    # Bazi wuxing analysis
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
    
    # Astro
    sun1 = p1['astrology'].get('太陽', {}).get('sign', '')
    sun2 = p2['astrology'].get('太陽', {}).get('sign', '')
    if sun1 == sun2:
        astro_note = f"同{sun1} · 節奏同步"
        astro_score = 5
    else:
        astro_note = f"{sun1}與{sun2} · 互補視角"
        astro_score = 3
    
    # Ziwei
    zw1 = p1['ziwei'].get('命宮', '未知')
    zw2 = p2['ziwei'].get('命宮', '未知')
    ziwei_note = f"{zw1}與{zw2} · 雙紫府格"
    ziwei_score = 4
    
    # HD
    hd1 = p1['humandesign'].get('energy_type', '')
    hd2 = p2['humandesign'].get('energy_type', '')
    if hd1 == hd2:
        hd_note = f"雙{hd1} · 容易共振"
        hd_score = 3
    else:
        hd_note = f"{hd1}與{hd2} · 互補能量"
        hd_score = 4
    
    # Xingxiu
    xx_rel = xingxiu.relation(p1['xingxiu'], p2['xingxiu'])
    xingxiu_note = f"{p1['xingxiu']}與{p2['xingxiu']} · {xx_rel}"
    xingxiu_score = 4 if xx_rel in ['命之星','榮親','友衰'] else 3
    
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
    
    return {
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
    }
