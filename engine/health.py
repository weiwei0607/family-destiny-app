# engine/health.py — 五行健康體質分析引擎
# 根據日主、喜忌神、五行缺失，對應中醫臟腑、運動、飲食建議

# ── 五行 → 臟腑 ─────────────────────────────────────────────
_WX_ORGAN = {
    '木': {
        'zangfu':  '肝・膽',
        'system':  '神經系統・眼睛・筋腱',
        'weak_symptoms': ['容易眼睛乾澀疲勞', '情緒壓抑或易怒', '指甲脆弱', '筋骨緊繃・抽筋', '睡眠淺容易多夢'],
        'over_symptoms': ['頭脹頭痛', '口苦', '情緒波動大', '兩肋脹痛'],
    },
    '火': {
        'zangfu':  '心・小腸',
        'system':  '循環系統・舌・血脈',
        'weak_symptoms': ['心悸氣短', '記憶力下降', '容易失眠多夢', '臉色蒼白', '手腳冰冷'],
        'over_symptoms': ['心煩口渴', '失眠難入睡', '舌尖紅痛', '小便短赤'],
    },
    '土': {
        'zangfu':  '脾・胃',
        'system':  '消化系統・肌肉・口唇',
        'weak_symptoms': ['消化不良・脹氣', '容易疲倦四肢無力', '食慾不振', '大便稀溏', '皮膚暗沉'],
        'over_symptoms': ['口甜・口臭', '腸胃悶脹', '濕氣重・水腫', '思慮過多失眠'],
    },
    '金': {
        'zangfu':  '肺・大腸',
        'system':  '呼吸系統・皮膚・鼻腔',
        'weak_symptoms': ['容易感冒咳嗽', '皮膚乾燥・過敏', '氣短・聲音無力', '大便乾燥・便秘', '鼻子過敏'],
        'over_symptoms': ['咳嗽・哮喘', '皮膚發炎紅腫', '大腸燥熱・痔瘡'],
    },
    '水': {
        'zangfu':  '腎・膀胱',
        'system':  '泌尿系統・骨骼・耳・生殖',
        'weak_symptoms': ['腰膝痠軟無力', '頻尿・夜尿多', '耳鳴・聽力下降', '髮質乾枯易落', '怕冷・手腳涼'],
        'over_symptoms': ['水腫', '尿道不適', '下背痛', '性功能下降'],
    },
}

# ── 五行 → 適合運動 ─────────────────────────────────────────
_WX_EXERCISE = {
    '木': {
        'good':  ['瑜珈・伸展', '太極拳', '森林步道健行', '攀岩（活化筋腱）', '舞蹈'],
        'avoid': ['過度競爭性運動（易傷肝氣）', '高強度間歇訓練（過燥）'],
        'note':  '重視伸展與柔韌度，戶外綠意環境最補',
    },
    '火': {
        'good':  ['有氧運動・慢跑', '游泳（涼爽調節心火）', '跳繩', '球類運動', '有節奏的舞蹈'],
        'avoid': ['過熱環境劇烈運動（耗心氣）', '長時間高強度不休息'],
        'note':  '保持心跳提升的有氧最佳，但要避免過熱過勞',
    },
    '土': {
        'good':  ['步行・散步', '健身房重訓（強化肌肉）', '農事・園藝', '土地感強的活動', '瑜珈'],
        'avoid': ['空腹劇烈運動（傷脾胃）', '運動後立刻吃東西'],
        'note':  '規律穩定的運動比衝刺型有效，飯後散步最補脾',
    },
    '金': {
        'good':  ['呼吸訓練・冥想', '游泳（強肺活量）', '跑步', '登山', '武術'],
        'avoid': ['霧霾或室內空氣差的環境運動', '過度壓抑呼吸的運動'],
        'note':  '重視呼吸品質，清晨戶外新鮮空氣最補肺',
    },
    '水': {
        'good':  ['游泳・水中運動', '太極・氣功', '瑜珈（強化腰腎）', '騎單車', '冬泳（謹慎）'],
        'avoid': ['過度消耗腎氣的高強度重訓', '長期熬夜後運動'],
        'note':  '腰腎保養最重要，避免劇烈消耗，溫和持續勝過爆發',
    },
}

# ── 五行 → 飲食建議 ─────────────────────────────────────────
_WX_DIET = {
    '木': {
        'good_foods':  ['深綠色蔬菜（菠菜・花椰菜・韭菜）', '酸味食物（檸檬・醋・梅子）', '枸杞・菊花茶', '堅果'],
        'avoid_foods': ['油炸・燒烤（傷肝）', '酒精（肝最忌）', '辛辣過度'],
        'good_taste':  '酸',
        'avoid_taste': '過辣・過鹹',
        'tip': '春天多吃嫩葉芽菜，護肝排毒；睡前不吃太飽',
    },
    '火': {
        'good_foods':  ['苦味食物（苦瓜・蓮子・綠茶）', '紅色食物（番茄・紅椒・草莓）', '蓮藕・百合・麥冬'],
        'avoid_foods': ['辛辣刺激（助火）', '咖啡因過多', '燒烤油炸'],
        'good_taste':  '苦（清心火）',
        'avoid_taste': '過辣・過甜',
        'tip': '夏天多補水，午休養心，少熬夜（子時傷心）',
    },
    '土': {
        'good_foods':  ['黃色食物（南瓜・玉米・地瓜）', '甘甜食物（蓮藕・山藥・紅棗）', '粥・易消化食物'],
        'avoid_foods': ['生冷食物（傷脾胃）', '過甜・過油', '暴飲暴食'],
        'good_taste':  '甘（適量）',
        'avoid_taste': '過酸・生冷',
        'tip': '規律三餐最重要，細嚼慢嚥，少喝冰飲',
    },
    '金': {
        'good_foods':  ['白色食物（白木耳・梨子・白蘿蔔・豆腐）', '辛味食物（蔥薑蒜適量）', '蜂蜜・川貝'],
        'avoid_foods': ['煙・油炸食物（傷肺）', '過鹹（傷腎連帶影響肺）', '辛辣過度'],
        'good_taste':  '辛（適量）',
        'avoid_taste': '過鹹・過苦',
        'tip': '秋天補肺潤燥，多喝水，蒸梨川貝是好選擇',
    },
    '水': {
        'good_foods':  ['黑色食物（黑芝麻・黑豆・黑木耳・海藻）', '鹹味食物（適量）', '核桃・枸杞・山藥'],
        'avoid_foods': ['過鹹（腎負擔）', '生冷寒涼（傷腎陽）', '過多咖啡因'],
        'good_taste':  '鹹（少量）',
        'avoid_taste': '過甜・過冷',
        'tip': '冬天補腎最佳，早睡護腎（子時腎藏精），腰部保暖',
    },
}

# ── 日主五行 → 體質傾向 ──────────────────────────────────────
_DM_CONSTITUTION = {
    '甲': {'type': '陽木體質', 'desc': '體質偏燥，筋骨強健但易緊繃，神經系統敏感，壓力容易積累在肝'},
    '乙': {'type': '陰木體質', 'desc': '體質柔和，免疫力中等，情緒影響身體明顯，需要規律作息'},
    '丙': {'type': '陽火體質', 'desc': '體質燥熱，精力充沛但易上火，心血管需要關注，夏天要特別降溫'},
    '丁': {'type': '陰火體質', 'desc': '體質偏熱但較溫和，心思細膩容易焦慮，心神不寧影響睡眠'},
    '戊': {'type': '陽土體質', 'desc': '體質偏濕重，消化系統是關鍵，容易水腫，肌肉力量好但需動起來'},
    '己': {'type': '陰土體質', 'desc': '體質容易濕阻，腸胃敏感，思慮過多影響脾，飲食規律是核心'},
    '庚': {'type': '陽金體質', 'desc': '體質偏燥，呼吸系統敏感，皮膚容易乾，秋冬要特別保濕潤肺'},
    '辛': {'type': '陰金體質', 'desc': '體質精緻但脆弱，皮膚敏感，過敏體質，環境品質對健康影響大'},
    '壬': {'type': '陽水體質', 'desc': '體質偏寒，腎氣充沛但怕過度消耗，熬夜是最大的敵人'},
    '癸': {'type': '陰水體質', 'desc': '體質偏寒濕，腎陰易虛，情緒起伏影響身體明顯，需要充足睡眠'},
}


def get_health_profile(bazi_struct: dict, bazi_wuxing: dict, day_master: str = '') -> dict:
    """
    根據日主 + 喜忌神 + 五行缺失 → 健康體質完整建議

    bazi_struct : core.bazi_structure_analysis() 的輸出
    bazi_wuxing : _analyze_person() 裡的 bazi_wuxing（含 missing/present）
    day_master  : 日主天干（如 '庚'）
    """
    xiyong   = bazi_struct.get('xiyong', [])
    jishen   = bazi_struct.get('jishen', [])
    missing  = bazi_wuxing.get('missing', [])
    present  = bazi_wuxing.get('present', [])
    strength = bazi_struct.get('strength', 'neutral')
    tiaohou  = bazi_struct.get('tiaohou', '')

    WX_MAP = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
              '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    dm_wx = WX_MAP.get(day_master, '')

    # 日主體質
    dm_constitution = _DM_CONSTITUTION.get(day_master, {
        'type': '均衡體質', 'desc': '五行均衡，體質適應力強'
    })

    # 命缺五行 → 對應臟腑偏弱，需要補養
    weak_organs = []
    for wx in missing:
        info = _WX_ORGAN.get(wx, {})
        if info:
            weak_organs.append({
                'wx': wx,
                'zangfu': info['zangfu'],
                'system': info['system'],
                'symptoms': info['weak_symptoms'][:3],
            })

    # 忌神對應臟腑 → 不可過勞（過旺已是負擔）
    overload_organs = []
    for wx in jishen:
        if wx in present:   # 命裡有且是忌神 → 已經偏旺
            info = _WX_ORGAN.get(wx, {})
            if info:
                overload_organs.append({
                    'wx': wx,
                    'zangfu': info['zangfu'],
                    'symptoms': info['over_symptoms'][:2],
                })

    # 主要保養重點（依喜用神 + 缺失）
    primary_wx = tiaohou if tiaohou else (xiyong[0] if xiyong else dm_wx)
    focus_wxs  = list(dict.fromkeys(missing + [primary_wx]))[:3]

    # 運動建議（主要喜用神）
    exercise = _WX_EXERCISE.get(primary_wx, {
        'good': ['有氧運動', '伸展運動'],
        'avoid': [],
        'note': '依身體狀態調整',
    })

    # 飲食建議（缺失五行補養 + 日主體質）
    diet_primary = _WX_DIET.get(primary_wx, {})
    diet_dm      = _WX_DIET.get(dm_wx, {}) if dm_wx != primary_wx else {}

    # 補缺飲食（缺什麼五行就補什麼）
    supplement_foods = []
    for wx in missing[:2]:
        d = _WX_DIET.get(wx, {})
        if d:
            supplement_foods.append({
                'wx': wx,
                'zangfu': _WX_ORGAN.get(wx, {}).get('zangfu', ''),
                'foods': d.get('good_foods', [])[:3],
                'tip': d.get('tip', ''),
            })

    # 整體健康警示
    warnings = _build_warnings(strength, dm_wx, missing, jishen, present)

    return {
        'dm_constitution':   dm_constitution,
        'weak_organs':       weak_organs,
        'overload_organs':   overload_organs,
        'exercise':          exercise,
        'diet_primary':      diet_primary,
        'diet_dm':           diet_dm,
        'supplement_foods':  supplement_foods,
        'focus_wxs':         focus_wxs,
        'warnings':          warnings,
        'strength':          strength,
    }


def _build_warnings(strength, dm_wx, missing, jishen, present):
    warnings = []

    if strength in ('weak', 'slightly_weak'):
        warnings.append('身弱型：體力消耗後恢復較慢，需要充足睡眠，少熬夜')
    elif strength in ('strong', 'slightly_strong'):
        warnings.append('身強型：精力充沛但容易輕忽身體訊號，定期健檢不可少')

    if '水' in missing:
        warnings.append('命缺水：腎氣較薄，注意腰膝保養，避免過度熬夜（子時傷腎）')
    if '火' in missing:
        warnings.append('命缺火：循環偏弱，手腳容易冰冷，冬天要特別保暖心臟')
    if '木' in missing:
        warnings.append('命缺木：肝膽代謝較弱，注意情緒管理，避免過度飲酒')
    if '金' in missing:
        warnings.append('命缺金：肺與皮膚較敏感，注意空氣品質，秋冬潤肺為重')
    if '土' in missing:
        warnings.append('命缺土：脾胃消化較弱，三餐要規律，少吃生冷')

    if dm_wx == '火' and '水' in jishen:
        warnings.append('火旺忌水：情緒起伏大時心臟壓力上升，學會緩壓最重要')
    if dm_wx == '金' and '火' in jishen:
        warnings.append('金旺忌火：呼吸系統敏感，避免高溫悶熱環境，秋冬護肺')
    if dm_wx == '水' and '土' in jishen:
        warnings.append('水旺忌土：腎與泌尿系統需要關注，多喝水但避免過度寒涼')

    return warnings[:4]  # 最多顯示4條
