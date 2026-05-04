import sqlite3
from pathlib import Path

def get_lunar_date(year, month, day):
    """查詢公曆日期對應的農曆日期 (1901-2099)
    
    使用 SQLite 資料庫進行快速查詢，避免佔用大量內存。
    """
    db_path = Path(__file__).parent.parent / 'lunar.db'
    solar_date = f"{year}-{month:02d}-{day:02d}"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT lunar_year, lunar_month, lunar_day, lunar_year_gz, is_leap_month 
            FROM lunar_days 
            WHERE solar_date = ?
        ''', (solar_date,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'lunar_year': row[0],
                'lunar_month': row[1],
                'lunar_day': row[2],
                'lunar_year_gz': row[3],
                'is_leap_month': bool(row[4])
            }
    except Exception as e:
        print(f"Lunar DB query error: {e}")
        
    return None
