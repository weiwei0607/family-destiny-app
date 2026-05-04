"""農曆查詢模組 - 快速查表

使用方法:
    from engine.lunar_lookup import get_lunar_date
    result = get_lunar_date(1999, 6, 7)
    # {'lunar_year': 1999, 'lunar_month': 4, 'lunar_day': 24, ...}
"""
import json
from pathlib import Path

_LUNAR_TABLE = None

def _ensure_loaded():
    global _LUNAR_TABLE
    if _LUNAR_TABLE is None:
        _table_path = Path(__file__).parent.parent.parent.parent / 'lunar_table.json'
        with open(_table_path, 'r') as f:
            _LUNAR_TABLE = json.load(f)

def get_lunar_date(year, month, day):
    """查詢公曆日期對應的農曆日期 (1901-2099)
    
    返回: {
        'lunar_year': int, 'lunar_month': int, 'lunar_day': int,
        'lunar_year_gz': str, 'is_leap_month': bool
    }
    """
    _ensure_loaded()
    try:
        return _LUNAR_TABLE[str(year)][str(month)][str(day)]
    except (KeyError, TypeError):
        return None
