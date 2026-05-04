def generate_portrait(lunar, bazi, astrology, ziwei, humandesign, xingxiu):
    """
    五系統整合畫像引擎
    將分散的命理數據交叉翻譯成易懂的人格畫像與建議。
    """
    
    # 1. 提取核心特徵
    dm = bazi.get('day_master', '')
    sun_sign = astrology.get('太陽', {}).get('sign', '')
    moon_sign = astrology.get('月亮', {}).get('sign', '')
    hd_type = humandesign.get('energy_type', '')
    zw_ming = ziwei.get('命宮', '')
    
    # 2. 生成五大維度
    
    # 維度一：外在表現 (Bazi + Sun)
    outer_map = {
        '甲': '參天大樹，正直且有向上心',
        '乙': '柔美藤蔓，靈活且具適應力',
        '丙': '燦爛陽光，熱情且具感染力',
        '丁': '溫暖燭火，細膩且有服務心',
        '戊': '厚重高山，穩重且值得信賴',
        '己': '濕潤田園，包容且具孕育力',
        '庚': '剛硬金屬，果斷且有義氣',
        '辛': '閃耀珠寶，精緻且自尊心強',
        '壬': '奔騰江河，大氣且有洞察力',
        '癸': '靈動雨露，溫柔且有創意'
    }
    outer_text = f"{outer_map.get(dm, '獨特的')}{sun_sign}座性格"
    outer_bad = f"缺點：有時過於{ '剛硬' if dm in '庚甲' else '發散' if dm in '丙壬' else '被動' if dm in '己戊' else '敏感' }，容易產生溝通落差。"

    # 維度二：內在需求 (Moon + Ziwei)
    inner_text = f"月亮{moon_sign}座帶來的安全感，結合紫微{zw_ming}的格局"
    inner_bad = "內在情緒較為波動，需要學會與自己的恐懼共處。"

    # 維度三：行動策略 (HD + Ziwei Stars)
    action_text = f"{hd_type}的運作模式，適合以「{'等待回應' if '生產' in hd_type else '發起' if '顯示' in hd_type else '觀察' if '反映' in hd_type else '受邀'}」作為行動核心。"
    action_bad = "如果不遵循內在權威，容易感到「憤怒」或「挫敗」。"

    # 3. 生成處方籤 (動態邏輯)
    prescriptions = []
    
    # 根據五行日主給建議
    if dm in '甲乙':
        prescriptions.append({'icon': '🌲', 'title': '多接觸森林', 'desc': '你的能量來源於木，每週去山林走走，或在室內擺放真植。'})
    elif dm in '丙丁':
        prescriptions.append({'icon': '🔥', 'title': '保持溫暖與光亮', 'desc': '多曬太陽，適度運動排汗，能讓你的思維更清晰。'})
    elif dm in '戊己':
        prescriptions.append({'icon': '⛰️', 'title': '接地氣 (Earthing)', 'desc': '多赤腳走在草地或沙灘上，幫助你排泄壓力，感受大地的穩定。'})
    elif dm in '庚辛':
        prescriptions.append({'icon': '💎', 'title': '保持極簡空間', 'desc': '金屬能量需要純淨。定期斷捨離，保持辦公桌空無一物。'})
    elif dm in '壬癸':
        prescriptions.append({'icon': '💧', 'title': '流動的水療癒', 'desc': '多泡澡或聽流水聲。水是你的靈魂元素，流動才能帶來財富。'})

    # 根據人類圖權威給建議
    authority = humandesign.get('authority', '')
    if '情緒' in authority:
        prescriptions.append({'icon': '😴', 'title': '重大決定睡一覺', 'desc': '你的情緒波需要時間沉澱。晚上 11 點後不回重要郵件。'})
    elif '薦骨' in authority:
        prescriptions.append({'icon': '🤔', 'title': '聽聽腹部的聲音', 'desc': '不需要思考理由，當下薦骨的「嗯」或「唔」就是答案。'})

    # 根據星宿給建議
    prescriptions.append({'icon': '✨', 'title': f'善用{xingxiu}宿能量', 'desc': f'你是{xingxiu}宿，天生帶有某種使命。在夜深人靜時冥想，能接通宇宙訊息。'})

    return {
        'integrated_cards': [
            {'title': '外在表現', 'text': outer_text, 'bad': outer_bad},
            {'title': '內在需求', 'text': inner_text, 'bad': inner_bad},
            {'title': '行動策略', 'text': action_text, 'bad': action_bad},
            {'title': '思維模式', 'text': f"水星{astrology.get('水星', {}).get('sign', '')}座與紫微輔星的交織", 'bad': '容易陷入細節或想太多。'},
            {'title': '關係模式', 'text': f"金星{astrology.get('金星', {}).get('sign', '')}座帶來的審美與喜好", 'bad': '需要警惕過度的依賴或控制欲望。'}
        ],
        'prescriptions': prescriptions,
        'life_topic': f"你的課題在於如何在{sun_sign}的理想與{dm}的現實之間找到平衡。"
    }
