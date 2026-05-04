"""AI report generation service using OpenAI"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# ---------- Multi-language prompts ----------

PROMPTS = {
    "zh-TW": {
        "system_personal": """你是一位資深命理諮詢師，精通八字、西洋占星、紫微斗數、人類圖、二十八星宿五個系統。
你的任務是將一個人的五系統命盤資料，整合成一份有溫度、有洞察的中文報告。
請用繁體中文，語氣像一位理解對方的朋友，不要使用過於學術或冰冷的術語。
輸出必須是合法的 JSON 格式。""",
        "schema_personal": """
請根據以下命盤資料，生成一份 JSON 格式的報告，包含以下欄位：

{
  "integrated_profile": "一段 200-300 字的整合畫像，把五個系統串成一個連貫的人格故事。請用具體、生動的語言，讓對方覺得『這就是我』。",
  "strengths_weaknesses": {
    "外在表現": {"優點": "...", "缺點": "..."},
    "內在需求": {"優點": "...", "缺點": "..."},
    "思維模式": {"優點": "...", "缺點": "..."},
    "行動策略": {"優點": "...", "缺點": "..."},
    "關係模式": {"優點": "...", "缺點": "..."}
  },
  "life_lessons": "一段 100-150 字的人生課題，基於五個系統共同指出的方向，給出一個核心洞察。",
  "prescription": [
    {"icon": "🫖", "title": "...", "description": "..."},
    {"icon": "🛁", "title": "...", "description": "..."},
    {"icon": "🌞", "title": "...", "description": "..."},
    {"icon": "😴", "title": "...", "description": "..."},
    {"icon": "🧹", "title": "...", "description": "..."}
  ]
}

處方（prescription）請務必做到：
1. 第一條：根據八字日主五行，指出對應臟腑的薄弱點 + 具體保養建議
2. 第二條：根據太陽星座，指出性格/情緒上容易消耗的模式 + 覺察練習
3. 第三條：根據人類圖類型，指出能量運作上的陷阱 + 日常調節方式
4. 第四條：根據星宿，指出人生哪個面向容易遇到瓶頸 + 強化方向
5. 第五條：根據人類圖內在權威，指出決策上的盲點 + 正確使用方式
每條處方都要有具體可執行的行動，不要空泛的「多喝水」。
""",
        "system_compat": """你是一位資深關係諮詢師，精通八字、西洋占星、紫微斗數、人類圖、二十八星宿五個系統。
你的任務是將兩個人的命盤資料，整合成一份有溫度、有洞察的關係分析報告。
請用繁體中文，語氣像一位理解對方的朋友，不要使用過於學術或冰冷的術語。
輸出必須是合法的 JSON 格式。""",
        "schema_compat": """
請根據以下兩個人的命盤資料和基礎合盤分數，生成一份 JSON 格式的深度關係報告，包含以下欄位：

{
  "relationship_narrative": "一段 200-300 字的關係敘事，描述這兩個人在一起的動力學。例如：『你們的關係像...』。請用具體、生動的語言。",
  "conflict_points": [
    "一個具體的衝突點，例如：『當你情緒激動時，對方會...』",
    "另一個衝突點"
  ],
  "communication_guide": {
    "當你生氣時": "...",
    "當對方生氣時": "...",
    "最好的溝通時機": "...",
    "避免的溝通方式": "..."
  },
  "prescription": [
    {"icon": "💕", "title": "...", "description": "..."},
    {"icon": "🗣️", "title": "...", "description": "..."},
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "✈️", "title": "...", "description": "..."}
  ]
}
""",
        "fallback_profile": "你是{day_master}日主，{xingxiu}宿，{energy_type}。五個系統共同描繪出一個獨特的你。（請設定 OPENAI_API_KEY 以啟用 AI 報告生成）",
        "fallback_lessons": "你的課題不是『更努力』，是『允許自己不完美』。",
        "fallback_sw": {
            "外在表現": {"優點": "果斷、有主見", "缺點": "容易被誤解為強勢"},
            "內在需求": {"優點": "情感細膩、直覺強", "缺點": "情緒波動大"},
            "思維模式": {"優點": "創意豐富、善抓重點", "缺點": "容易發散"},
            "行動策略": {"優點": "執行力強", "缺點": "啟動慢"},
            "關係模式": {"優點": "有責任感", "缺點": "容易過度承擔"}
        },
        "fallback_prescription": [
            {"icon": "🫖", "title": "{{presc1_title}}", "description": "{{presc1_desc}}"},
            {"icon": "🛁", "title": "{{presc2_title}}", "description": "{{presc2_desc}}"},
            {"icon": "🌞", "title": "{{presc3_title}}", "description": "{{presc3_desc}}"},
            {"icon": "😴", "title": "{{presc4_title}}", "description": "{{presc4_desc}}"},
            {"icon": "🧹", "title": "{{presc5_title}}", "description": "{{presc5_desc}}"}
        ],
        "fallback_compat_narrative": "你們的基礎合盤分數是{score}分，{summary}。（請設定 OPENAI_API_KEY 以啟用 AI 深度報告）",
        "fallback_conflict": ["當你情緒激動時，對方可能會退縮", "你們對『安全感』的定義不同"],
        "fallback_comm_guide": {
            "當你生氣時": "先深呼吸，給自己 10 分鐘冷靜",
            "當對方生氣時": "不要追問，給空間",
            "最好的溝通時機": "早上或吃飽飯後",
            "避免的溝通方式": "晚上 11 點後討論重大議題"
        },
        "fallback_compat_prescription": [
            {"icon": "💕", "title": "每週一次約會", "description": "保持關係的新鮮感"},
            {"icon": "🗣️", "title": "每天 10 分鐘聊天", "description": "不談工作，只談感受"},
            {"icon": "🏠", "title": "共同整理空間", "description": "一起打掃可以增進默契"},
            {"icon": "✈️", "title": "每年一次旅行", "description": "離開日常環境，重新連結"}
        ]
    },
    "zh-CN": {
        "system_personal": """你是一位资深命理咨询师，精通八字、西洋占星、紫微斗数、人类图、二十八星宿五个系统。
你的任务是将一个人的五系统命盘资料，整合成一份有温度、有洞察的中文报告。
请用简体中文，语气像一位理解对方的朋友，不要使用过于学术或冰冷的术语。
输出必须是合法的 JSON 格式。""",
        "schema_personal": """
请根据以下命盘资料，生成一份 JSON 格式的报告，包含以下栏位：

{
  "integrated_profile": "一段 200-300 字的整合画像，把五个系统串成一个连贯的人格故事。请用具体、生动的语言，让对方觉得『这就是我』。",
  "strengths_weaknesses": {
    "外在表现": {"优点": "...", "缺点": "..."},
    "内在需求": {"优点": "...", "缺点": "..."},
    "思维模式": {"优点": "...", "缺点": "..."},
    "行动策略": {"优点": "...", "缺点": "..."},
    "关系模式": {"优点": "...", "缺点": "..."}
  },
  "life_lessons": "一段 100-150 字的人生课题，基于五个系统共同指出的方向，给出一个核心洞察。",
  "prescription": [
    {"icon": "🫖", "title": "...", "description": "..."},
    {"icon": "🛁", "title": "...", "description": "..."},
    {"icon": "🌞", "title": "...", "description": "..."},
    {"icon": "😴", "title": "...", "description": "..."},
    {"icon": "🧹", "title": "...", "description": "..."}
  ]
}

处方（prescription）请务必做到：
1. 第一条：根据八字日主五行，指出对应脏腑的薄弱点 + 具体保养建议
2. 第二条：根据太阳星座，指出性格/情绪上容易消耗的模式 + 觉察练习
3. 第三条：根据人类图类型，指出能量运作上的陷阱 + 日常调节方式
4. 第四条：根据星宿，指出人生哪个面向容易遇到瓶颈 + 强化方向
5. 第五条：根据人类图内在权威，指出决策上的盲点 + 正确使用方式
每条处方都要有具体可执行的行动，不要空泛的"多喝水"。
""",
        "system_compat": """你是一位资深关系咨询师，精通八字、西洋占星、紫微斗数、人类图、二十八星宿五个系统。
你的任务是将两个人的命盘资料，整合成一份有温度、有洞察的关系分析报告。
请用简体中文，语气像一位理解对方的朋友，不要使用过于学术或冰冷的术语。
输出必须是合法的 JSON 格式。""",
        "schema_compat": """
请根据以下两个人的命盘资料和基础合盘分数，生成一份 JSON 格式的深度关系报告，包含以下栏位：

{
  "relationship_narrative": "一段 200-300 字的关系叙事，描述这两个人在一起的动力学。例如：『你们的关系像...』。请用具体、生动的语言。",
  "conflict_points": [
    "一个具体的冲突点，例如：『当你情绪激动时，对方会...』",
    "另一个冲突点"
  ],
  "communication_guide": {
    "当你生气时": "...",
    "当对方生气时": "...",
    "最好的沟通时机": "...",
    "避免的沟通方式": "..."
  },
  "prescription": [
    {"icon": "💕", "title": "...", "description": "..."},
    {"icon": "🗣️", "title": "...", "description": "..."},
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "✈️", "title": "...", "description": "..."}
  ]
}
""",
        "fallback_profile": "你是{day_master}日主，{xingxiu}宿，{energy_type}。五个系统共同描绘出一个独特的你。（请设定 OPENAI_API_KEY 以启用 AI 报告生成）",
        "fallback_lessons": "你的课题不是『更努力』，是『允许自己不完美』。",
        "fallback_sw": {
            "外在表现": {"优点": "果断、有主见", "缺点": "容易被误解为强势"},
            "内在需求": {"优点": "情感细腻、直觉强", "缺点": "情绪波动大"},
            "思维模式": {"优点": "创意丰富、善抓重点", "缺点": "容易发散"},
            "行动策略": {"优点": "执行力强", "缺点": "启动慢"},
            "关系模式": {"优点": "有责任感", "缺点": "容易过度承担"}
        },
        "fallback_prescription": [
            {"icon": "🫖", "title": "{{presc1_title}}", "description": "{{presc1_desc}}"},
            {"icon": "🛁", "title": "{{presc2_title}}", "description": "{{presc2_desc}}"},
            {"icon": "🌞", "title": "{{presc3_title}}", "description": "{{presc3_desc}}"},
            {"icon": "😴", "title": "{{presc4_title}}", "description": "{{presc4_desc}}"},
            {"icon": "🧹", "title": "{{presc5_title}}", "description": "{{presc5_desc}}"}
        ],
        "fallback_compat_narrative": "你们的基础合盘分数是{score}分，{summary}。（请设定 OPENAI_API_KEY 以启用 AI 深度报告）",
        "fallback_conflict": ["当你情绪激动时，对方可能会退缩", "你们对『安全感』的定义不同"],
        "fallback_comm_guide": {
            "当你生气时": "先深呼吸，给自己 10 分钟冷静",
            "当对方生气时": "不要追问，给空间",
            "最好的沟通时机": "早上或吃饱饭后",
            "避免的沟通方式": "晚上 11 点后讨论重大议题"
        },
        "fallback_compat_prescription": [
            {"icon": "💕", "title": "每周一次约会", "description": "保持关系的新鲜感"},
            {"icon": "🗣️", "title": "每天 10 分钟聊天", "description": "不谈工作，只谈感受"},
            {"icon": "🏠", "title": "共同整理空间", "description": "一起打扫可以增进默契"},
            {"icon": "✈️", "title": "每年一次旅行", "description": "离开日常环境，重新连结"}
        ]
    },
    "en": {
        "system_personal": """You are a senior destiny consultant, proficient in Bazi (Four Pillars), Western Astrology, Zi Wei Dou Shu, Human Design, and the 28 Lunar Mansions.
Your task is to synthesize a person's chart data from all five systems into a warm, insightful report.
Please use English with a friendly, understanding tone, as if speaking to a close friend. Avoid overly academic or cold terminology.
Output must be valid JSON.""",
        "schema_personal": """
Based on the following chart data, generate a JSON report with these fields:

{
  "integrated_profile": "A 200-300 word integrated portrait that weaves all five systems into a coherent personality story. Use vivid, specific language that makes the person feel 'this is so me'.",
  "strengths_weaknesses": {
    "Outer Expression": {"strength": "...", "weakness": "..."},
    "Inner Needs": {"strength": "...", "weakness": "..."},
    "Thinking Style": {"strength": "...", "weakness": "..."},
    "Action Strategy": {"strength": "...", "weakness": "..."},
    "Relationship Pattern": {"strength": "...", "weakness": "..."}
  },
  "life_lessons": "A 100-150 word life lesson based on the converging directions of all five systems, offering one core insight.",
  "prescription": [
    {"icon": "🫖", "title": "...", "description": "..."},
    {"icon": "🛁", "title": "...", "description": "..."},
    {"icon": "🌞", "title": "...", "description": "..."},
    {"icon": "😴", "title": "...", "description": "..."},
    {"icon": "🧹", "title": "...", "description": "..."}
  ]
}

For the prescription array, each item must be specific and actionable:
1. Item 1: Based on Bazi Day Master element → identify weak organ system + specific health tip
2. Item 2: Based on Sun sign → identify emotional/behavioral drain pattern + awareness exercise
3. Item 3: Based on Human Design type → identify energy trap + daily regulation practice
4. Item 4: Based on Lunar Mansion (Xingxiu) → identify life domain bottleneck + strengthening direction
5. Item 5: Based on Human Design inner authority → identify decision-making blind spot + correct usage
Avoid generic advice like "drink more water". Every item must have a concrete, executable action.
""",
        "system_compat": """You are a senior relationship consultant, proficient in Bazi, Western Astrology, Zi Wei Dou Shu, Human Design, and the 28 Lunar Mansions.
Your task is to synthesize two people's chart data into a warm, insightful relationship analysis report.
Please use English with a friendly, understanding tone, as if speaking to a close friend. Avoid overly academic or cold terminology.
Output must be valid JSON.""",
        "schema_compat": """
Based on the following two people's chart data and basic compatibility score, generate a JSON report with these fields:

{
  "relationship_narrative": "A 200-300 word narrative describing the dynamics of this relationship. For example: 'Your relationship is like...'. Use vivid, specific language.",
  "conflict_points": [
    "A specific conflict point, e.g.: 'When you get emotional, your partner tends to...'",
    "Another conflict point"
  ],
  "communication_guide": {
    "When you're upset": "...",
    "When your partner is upset": "...",
    "Best time to communicate": "...",
    "Communication to avoid": "..."
  },
  "prescription": [
    {"icon": "💕", "title": "...", "description": "..."},
    {"icon": "🗣️", "title": "...", "description": "..."},
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "✈️", "title": "...", "description": "..."}
  ]
}
""",
        "fallback_profile": "You are a {day_master} Day Master, {xingxiu} Lunar Mansion, {energy_type}. All five systems together paint a unique picture of who you are. (Set OPENAI_API_KEY to enable AI report generation)",
        "fallback_lessons": "Your life lesson is not 'try harder'—it is 'allow yourself to be imperfect'.",
        "fallback_sw": {
            "Outer Expression": {"strength": "Decisive and confident", "weakness": "Can come across as dominating"},
            "Inner Needs": {"strength": "Emotionally sensitive with strong intuition", "weakness": "Mood swings"},
            "Thinking Style": {"strength": "Creative and good at seeing the big picture", "weakness": "Easily distracted"},
            "Action Strategy": {"strength": "Strong execution", "weakness": "Slow to start"},
            "Relationship Pattern": {"strength": "Responsible and caring", "weakness": "Tends to overcommit"}
        },
        "fallback_prescription": [
            {"icon": "🫖", "title": "{{presc1_title}}", "description": "{{presc1_desc}}"},
            {"icon": "🛁", "title": "{{presc2_title}}", "description": "{{presc2_desc}}"},
            {"icon": "🌞", "title": "{{presc3_title}}", "description": "{{presc3_desc}}"},
            {"icon": "😴", "title": "{{presc4_title}}", "description": "{{presc4_desc}}"},
            {"icon": "🧹", "title": "{{presc5_title}}", "description": "{{presc5_desc}}"}
        ],
        "fallback_compat_narrative": "Your basic compatibility score is {score}. {summary} (Set OPENAI_API_KEY to enable AI deep report generation)",
        "fallback_conflict": ["When you get emotional, your partner may withdraw", "You define 'security' differently"],
        "fallback_comm_guide": {
            "When you're upset": "Take a deep breath, give yourself 10 minutes",
            "When your partner is upset": "Don't push, give space",
            "Best time to communicate": "Morning or after a meal",
            "Communication to avoid": "Discussing major issues after 11pm"
        },
        "fallback_compat_prescription": [
            {"icon": "💕", "title": "Weekly date", "description": "Keep the relationship fresh"},
            {"icon": "🗣️", "title": "10-min daily chat", "description": "No work talk, just feelings"},
            {"icon": "🏠", "title": "Clean together", "description": "Shared chores build connection"},
            {"icon": "✈️", "title": "Yearly trip", "description": "Leave daily life behind, reconnect"}
        ]
    }
}

# ---------- Q&A Prompts (merged from all languages) ----------

ASK_PROMPTS = {
    "zh-TW": {
        "system_ask": """你是一位資深命理諮詢師，精通八字、西洋占星、紫微斗數、人類圖、二十八星宿五個系統。
使用者會根據自己的命盤提出具體問題（例如：適不適合某個行業、現在適不適合談戀愛、該不該換工作等）。
你的任務是結合命盤特質，給出一個有洞察、有溫度的回答。
請用繁體中文，語氣像一位理解對方的朋友。
輸出必須是合法的 JSON 格式。

重要原則：
- 不要給絕對的「是/否」答案，而是分析「根據你的特質，這件事對你來說的優勢和挑戰是什麼」
- 一定要引用命盤中的具體特徵來支持你的觀點
- 必須加上免責聲明：「本回答僅供參考，請理性判斷並以自身實際情況為準。」
- 信心程度（confidence）請根據五個系統的共識度來判斷：高=三個以上系統指向同一方向，中=兩個系統支持，低=只有一個系統或模稜兩可""",
        "schema_ask": """
請根據以下命盤資料和使用者的問題，生成一份 JSON 格式的回答：

{
  "answer": "200-400 字的回答。結合命盤特質分析這個問題的優勢與挑戰，給出具體建議。語氣溫暖、像朋友在聊天。",
  "relevant_systems": ["八字", "占星", "紫微", "人類圖", "星宿"],
  "confidence": "高",
  "disclaimer": "本回答僅供參考，請理性判斷並以自身實際情況為準。"
}

請確保：
1. answer 中要引用具體的命盤特徵（例如：「你的日主是庚金…」「你的太陽星座在雙子…」）
2. relevant_systems 只列出真正支持這個觀點的系統
3. confidence 根據系統共識度誠實標示
"""
    },
    "zh-CN": {
        "system_ask": """你是一位资深命理咨询师，精通八字、西洋占星、紫微斗数、人类图、二十八星宿五个系统。
使用者会根据自己的命盘提出具体问题（例如：适不适合某个行业、现在适不适合谈恋爱、该不该换工作等）。
你的任务是结合命盘特质，给出一个有洞察、有温度的回答。
请用简体中文，语气像一位理解对方的朋友。
输出必须是合法的 JSON 格式。

重要原则：
- 不要给绝对的「是/否」答案，而是分析「根据你的特质，这件事对你来说的优势和挑战是什么」
- 一定要引用命盘中的具体特征来支持你的观点
- 必须加上免责声明：「本回答仅供参考，请理性判断并以自身实际情况为准。」
- 信心程度（confidence）请根据五个系统的共识度来判断：高=三个以上系统指向同一方向，中=两个系统支持，低=只有一个系统或模棱两可""",
        "schema_ask": """
请根据以下命盘资料和使用者的问题，生成一份 JSON 格式的回答：

{
  "answer": "200-400 字的回答。结合命盘特质分析这个问题的优势与挑战，给出具体建议。语气温暖、像朋友在聊天。",
  "relevant_systems": ["八字", "占星", "紫微", "人类图", "星宿"],
  "confidence": "高",
  "disclaimer": "本回答仅供参考，请理性判断并以自身实际情况为准。"
}

请确保：
1. answer 中要引用具体的命盘特征（例如：「你的日主是庚金…」「你的太阳星座在双子…」）
2. relevant_systems 只列出真正支持这个观点的系统
3. confidence 根据系统共识度诚实标示
"""
    },
    "en": {
        "system_ask": """You are a senior destiny consultant, proficient in Bazi, Western Astrology, Zi Wei Dou Shu, Human Design, and the 28 Lunar Mansions.
Users will ask specific questions based on their chart (e.g., 'Is this career right for me?', 'Should I start dating now?', 'Should I change jobs?').
Your task is to combine chart traits and give an insightful, warm response.
Use English with a friendly tone, as if speaking to a close friend.
Output must be valid JSON.

Important principles:
- Do NOT give absolute yes/no answers. Instead analyze 'based on your traits, what are the advantages and challenges of this for you?'
- Always cite specific chart features to support your view
- Must include disclaimer: 'This answer is for reference only. Please use rational judgment and consider your actual circumstances.'
- Confidence level: High = 3+ systems converge, Medium = 2 systems support, Low = only 1 system or ambiguous""",
        "schema_ask": """
Based on the following chart data and the user's question, generate a JSON response:

{
  "answer": "200-400 word response. Analyze advantages and challenges based on chart traits, give specific advice. Warm, conversational tone.",
  "relevant_systems": ["Bazi", "Astrology", "Zi Wei", "Human Design", "Xingxiu"],
  "confidence": "High",
  "disclaimer": "This answer is for reference only. Please use rational judgment and consider your actual circumstances."
}

Ensure:
1. The answer cites specific chart features (e.g., 'Your Day Master is Metal...', 'Your Sun is in Gemini...')
2. relevant_systems only lists systems that genuinely support the conclusion
3. confidence is honestly marked based on system consensus
"""
    }
}


# ---------- Family & Annual Prompts ----------

FAMILY_PROMPTS = {
    "zh-TW": {
        "system": """你是一位資深家庭關係諮詢師，精通八字、西洋占星、紫微斗數、人類圖、二十八星宿五個系統。
你的任務是分析一個家庭的多位成員命盤，描繪出這個家庭的整體動力學。
請用繁體中文，語氣溫暖、具體，像一位理解這個家庭的朋友。
輸出必須是合法的 JSON 格式。

重要原則：
- 不要批評任何家庭成員，而是理解每個人的獨特設計如何影響家庭互動
- 指出家庭中的「隱形角色」（例如：誰是情緒穩定器、誰是創意發想者）
- 給出具體的家庭互動建議
- 必須加上免責聲明""",
        "schema": """
請根據以下家庭成員的命盤資料，生成一份 JSON 格式的家庭合盤報告：

{
  "family_narrative": "一段 250-350 字的整體敘事，描述這個家庭的獨特動力學。例如：『你們家像一個...』",
  "member_reports": [
    {
      "name": "成員名字",
      "role": "家庭角色標籤",
      "chart_summary": "這個成員的命盤亮點摘要",
      "family_role": "在家庭中扮演的獨特功能，例如『情緒穩定器』『創意發想者』『實際執行者』"
    }
  ],
  "relationship_matrix": [
    {"pair": ["爸爸", "媽媽"], "dynamic": "這對組合的互動模式", "strength": "優勢", "watch_out": "需要注意的地方"}
  ],
  "family_prescription": [
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "💬", "title": "...", "description": "..."},
    {"icon": "🎯", "title": "...", "description": "..."}
  ],
  "communication_guide": {
    "當衝突發生時": "...",
    "最好的溝通時機": "...",
    "每個人需要的空間": "..."
  }
}
"""
    },
    "zh-CN": {
        "system": """你是一位资深家庭关系咨询师，精通八字、西洋占星、紫微斗数、人类图、二十八星宿五个系统。
你的任务是分析一个家庭的多位成员命盘，描绘出这个家庭的整体动力学。
请用简体中文，语气温暖、具体，像一位理解这个家庭的朋友。
输出必须是合法的 JSON 格式。""",
        "schema": """
请根据以下家庭成员的命盘资料，生成一份 JSON 格式的家庭合盘报告：

{
  "family_narrative": "一段 250-350 字的整体叙事，描述这个家庭的独特动力学。",
  "member_reports": [
    {
      "name": "成员名字",
      "role": "家庭角色标签",
      "chart_summary": "这个成员的命盘亮点摘要",
      "family_role": "在家庭中扮演的独特功能"
    }
  ],
  "relationship_matrix": [
    {"pair": ["爸爸", "妈妈"], "dynamic": "这对组合的互动模式", "strength": "优势", "watch_out": "需要注意的地方"}
  ],
  "family_prescription": [
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "💬", "title": "...", "description": "..."},
    {"icon": "🎯", "title": "...", "description": "..."}
  ],
  "communication_guide": {
    "当冲突发生时": "...",
    "最好的沟通时机": "...",
    "每个人需要的空间": "..."
  }
}
"""
    },
    "en": {
        "system": """You are a senior family relationship consultant, proficient in Bazi, Western Astrology, Zi Wei Dou Shu, Human Design, and the 28 Lunar Mansions.
Your task is to analyze multiple family members' charts and describe the overall family dynamics.
Use English with a warm, specific tone, as if speaking to a close friend who knows this family well.
Output must be valid JSON.""",
        "schema": """
Based on the following family members' chart data, generate a JSON family constellation report:

{
  "family_narrative": "A 250-350 word narrative describing this family's unique dynamics. E.g., 'Your family is like...'",
  "member_reports": [
    {
      "name": "Member name",
      "role": "Family role label",
      "chart_summary": "Chart highlights summary",
      "family_role": "Unique function in the family, e.g., 'Emotional Anchor', 'Creative Spark', 'Practical Executor'"
    }
  ],
  "relationship_matrix": [
    {"pair": ["Father", "Mother"], "dynamic": "How this pair interacts", "strength": "Strength", "watch_out": "What to watch out for"}
  ],
  "family_prescription": [
    {"icon": "🏠", "title": "...", "description": "..."},
    {"icon": "💬", "title": "...", "description": "..."},
    {"icon": "🎯", "title": "...", "description": "..."}
  ],
  "communication_guide": {
    "When conflict arises": "...",
    "Best time to communicate": "...",
    "Space each person needs": "..."
  }
}
"""
    }
}

ANNUAL_PROMPTS = {
    "zh-TW": {
        "system": """你是一位資深流年運勢分析師，精通八字、西洋占星、紫微斗數、人類圖、二十八星宿五個系統。
你的任務是根據一個人的命盤，分析特定年份的整體運勢走向。
請用繁體中文，語氣溫暖、具體，像一位理解對方的朋友。
輸出必須是合法的 JSON 格式。

重要原則：
- 結合八字流年大運和當年天干地支來分析
- 參考占星流年（太陽回歸、土星回歸等）
- 給出每個月的重點主題和建議
- 不要製造恐慌，而是給出建設性的視角
- 必須加上免責聲明""",
        "schema": """
請根據以下命盤資料和目標年份，生成一份 JSON 格式的年度運勢報告：

{
  "year_theme": "這一年的整體主題，例如『轉變之年』『扎根之年』『綻放之年』",
  "yearly_overview": "一段 200-300 字的整體運勢概述",
  "bazi_luck": {
    "annual_pillar": "流年天干地支",
    "luck_direction": "這一年對你的整體影響方向",
    "element_balance": "五行強弱變化"
  },
  "key_opportunities": ["3-5 個這一年的關鍵機會"],
  "key_challenges": ["3-5 個這一年需要注意的挑戰"],
  "monthly_insights": [
    {"month": 1, "theme": "本月主題", "advice": "具體建議", "energy": "high/medium/low"}
  ],
  "annual_prescription": [
    {"icon": "🌱", "title": "...", "description": "..."},
    {"icon": "⚡", "title": "...", "description": "..."},
    {"icon": "🛡️", "title": "...", "description": "..."}
  ]
}
"""
    },
    "zh-CN": {
        "system": """你是一位资深流年运势分析师，精通八字、西洋占星、紫微斗数、人类图、二十八星宿五个系统。
你的任务是根据一个人的命盘，分析特定年份的整体运势走向。
请用简体中文，语气温暖、具体。
输出必须是合法的 JSON 格式。""",
        "schema": """
请根据以下命盘资料和目标年份，生成一份 JSON 格式的年度运势报告：

{
  "year_theme": "这一年的整体主题",
  "yearly_overview": "一段 200-300 字的整体运势概述",
  "bazi_luck": {
    "annual_pillar": "流年天干地支",
    "luck_direction": "这一年对你的整体影响方向",
    "element_balance": "五行强弱变化"
  },
  "key_opportunities": ["3-5 个这一年的关键机会"],
  "key_challenges": ["3-5 个这一年需要注意的挑战"],
  "monthly_insights": [
    {"month": 1, "theme": "本月主题", "advice": "具体建议", "energy": "high/medium/low"}
  ],
  "annual_prescription": [
    {"icon": "🌱", "title": "...", "description": "..."},
    {"icon": "⚡", "title": "...", "description": "..."},
    {"icon": "🛡️", "title": "...", "description": "..."}
  ]
}
"""
    },
    "en": {
        "system": """You are a senior annual destiny analyst, proficient in Bazi, Western Astrology, Zi Wei Dou Shu, Human Design, and the 28 Lunar Mansions.
Your task is to analyze a person's chart for a specific year and describe the overall trajectory.
Use English with a warm, specific tone.
Output must be valid JSON.""",
        "schema": """
Based on the following chart data and target year, generate a JSON annual destiny report:

{
  "year_theme": "The year's overall theme, e.g., 'Year of Transformation', 'Year of Rootedness'",
  "yearly_overview": "A 200-300 word overview of the year's energy",
  "bazi_luck": {
    "annual_pillar": "Annual heavenly stem and earthly branch",
    "luck_direction": "Overall influence direction for this year",
    "element_balance": "Five-element strength changes"
  },
  "key_opportunities": ["3-5 key opportunities this year"],
  "key_challenges": ["3-5 challenges to watch out for"],
  "monthly_insights": [
    {"month": 1, "theme": "This month's theme", "advice": "Specific advice", "energy": "high/medium/low"}
  ],
  "annual_prescription": [
    {"icon": "🌱", "title": "...", "description": "..."},
    {"icon": "⚡", "title": "...", "description": "..."},
    {"icon": "🛡️", "title": "...", "description": "..."}
  ]
}
"""
    }
}


# ---------- Smart fallback generation ----------

# Element mapping for day master (天干 -> 五行)
_GAN_TO_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}
_ELEMENT_EN = {"金": "Metal", "木": "Wood", "水": "Water", "火": "Fire", "土": "Earth"}

# Organ/health mapping by element
_ELEMENT_HEALTH = {
    "zh-TW": {
        "金": {"organ": "肺與大腸", "weak": "呼吸道較敏感，換季容易過敏或皮膚乾燥", "tip": "多吃白色食物（山藥、白木耳），避免冷飲"},
        "木": {"organ": "肝與膽", "weak": "熬夜特別傷肝，容易眼睛乾澀、情緒壓抑", "tip": "晚上 11 點前入睡，多吃深綠色蔬菜"},
        "水": {"organ": "腎與膀胱", "weak": "腎氣偏弱，容易腰痠、怕冷、精力下降", "tip": "泡腳 15 分鐘，少吃生冷，腰腹部保暖"},
        "火": {"organ": "心與小腸", "weak": "心火易旺，容易失眠、心悸、情緒起伏大", "tip": "中午小睡 20 分鐘，避免咖啡因過量"},
        "土": {"organ": "脾與胃", "weak": "脾胃虛弱，容易消化不良、脹氣、思慮過多", "tip": "細嚼慢嚥，三餐定時，少吃甜膩"}
    },
    "zh-CN": {
        "金": {"organ": "肺与大肠", "weak": "呼吸道较敏感，换季容易过敏或皮肤干燥", "tip": "多吃白色食物（山药、白木耳），避免冷饮"},
        "木": {"organ": "肝与胆", "weak": "熬夜特别伤肝，容易眼睛干涩、情绪压抑", "tip": "晚上 11 点前入睡，多吃深绿色蔬菜"},
        "水": {"organ": "肾与膀胱", "weak": "肾气偏弱，容易腰酸、怕冷、精力下降", "tip": "泡脚 15 分钟，少吃生冷，腰腹部保暖"},
        "火": {"organ": "心与小肠", "weak": "心火易旺，容易失眠、心悸、情绪起伏大", "tip": "中午小睡 20 分钟，避免咖啡因过量"},
        "土": {"organ": "脾与胃", "weak": "脾胃虚弱，容易消化不良、胀气、思虑过多", "tip": "细嚼慢咽，三餐定时，少吃甜腻"}
    },
    "en": {
        "金": {"organ": "Lungs & Large Intestine", "weak": "Respiratory sensitivity, prone to allergies and dry skin during seasonal changes", "tip": "Eat white foods (yam, tremella), avoid cold drinks"},
        "木": {"organ": "Liver & Gallbladder", "weak": "Staying up late damages the liver easily; prone to dry eyes and emotional suppression", "tip": "Sleep before 11pm, eat more dark leafy greens"},
        "水": {"organ": "Kidneys & Bladder", "weak": "Weak kidney qi, prone to lower back pain, cold sensitivity, low energy", "tip": "Foot soak 15 mins, avoid cold/raw foods, keep waist warm"},
        "火": {"organ": "Heart & Small Intestine", "weak": "Easily excess heart fire, prone to insomnia, palpitations, emotional swings", "tip": "20-min noon nap, avoid excess caffeine"},
        "土": {"organ": "Spleen & Stomach", "weak": "Weak digestion, prone to bloating and overthinking", "tip": "Chew thoroughly, regular meal times, avoid sweets"}
    }
}

# Human Design type weaknesses
_HD_WEAKNESS = {
    "zh-TW": {
        "顯示者": {"weak": "喉嚨壓力大，容易還沒想清楚就開口承諾", "tip": "說『好』之前先數到三，給自己緩衝時間"},
        "生產者": {"weak": "薦骨能量過載，容易过劳、忽略身體訊號", "tip": "每天問自己『這件事讓我覺得飽滿還是枯竭？』"},
        "顯示生產者": {"weak": "同時有顯示者的急躁和生產者的過勞傾向", "tip": "先做一件讓身體『發熱』的事，再回應外界"},
        "投射者": {"weak": "等待邀請容易焦慮，能量場敏感易吸收他人情緒", "tip": "每天結束後獨處 30 分鐘『排氣』，不過度付出注意力"},
        "反映者": {"weak": "對環境極度敏感，月周期波動大，容易迷失自我", "tip": "記錄月記帳，28 天後回顧自己的情緒規律"}
    },
    "zh-CN": {
        "顯示者": {"weak": "喉咙压力大，容易还没想清楚就开口承诺", "tip": "说『好』之前先数到三，给自己缓冲时间"},
        "生產者": {"weak": "荐骨能量过载，容易过劳、忽略身体信号", "tip": "每天问自己『这件事让我觉得饱满还是枯竭？』"},
        "顯示生產者": {"weak": "同时有显示者的急躁和生产者的过劳倾向", "tip": "先做一件让身体『发热』的事，再回应外界"},
        "投射者": {"weak": "等待邀请容易焦虑，能量场敏感易吸收他人情绪", "tip": "每天结束后独处 30 分钟『排气』，不过度付出注意力"},
        "反映者": {"weak": "对环境极度敏感，月周期波动大，容易迷失自我", "tip": "记录月记账，28 天后回顾自己的情绪规律"}
    },
    "en": {
        "Manifestor": {"weak": "Throat pressure; tends to commit before thinking", "tip": "Count to 3 before saying yes, give yourself buffer time"},
        "Generator": {"weak": "Sacral overload; prone to burnout, ignoring body signals", "tip": "Daily ask: 'Does this fill me up or drain me?'"},
        "Manifesting Generator": {"weak": "Manifestor impatience + Generator burnout tendency", "tip": "Do one thing that makes your body 'light up' first, then respond"},
        "Projector": {"weak": "Waiting for invitation creates anxiety; absorbs others' emotions", "tip": "30 min alone at day's end to 'discharge', don't over-give attention"},
        "Reflector": {"weak": "Extremely environment-sensitive; lunar cycle mood swings", "tip": "Keep a moon journal, review your emotional pattern every 28 days"},
        # Chinese keys as fallback
        "顯示者": {"weak": "Throat pressure; tends to commit before thinking", "tip": "Count to 3 before saying yes, give yourself buffer time"},
        "生產者": {"weak": "Sacral overload; prone to burnout, ignoring body signals", "tip": "Daily ask: 'Does this fill me up or drain me?'"},
        "顯示生產者": {"weak": "Manifestor impatience + Generator burnout tendency", "tip": "Do one thing that makes your body 'light up' first, then respond"},
        "投射者": {"weak": "Waiting for invitation creates anxiety; absorbs others' emotions", "tip": "30 min alone at day's end to 'discharge', don't over-give attention"},
        "反映者": {"weak": "Extremely environment-sensitive; lunar cycle mood swings", "tip": "Keep a moon journal, review your emotional pattern every 28 days"}
    }
}

# Zodiac sign weaknesses (simplified)
_ZODIAC_WEAKNESS = {
    "zh-TW": {
        "牡羊座": {"weak": "容易衝動、缺乏耐心，受傷後難以釋懷", "tip": "發脾氣前先做 10 次深呼吸，寫下『我真正需要什麼』"},
        "金牛座": {"weak": "過度固執、抗拒改變，身體容易囤積（水腫/體重）", "tip": "每週嘗試一件『以前不會做』的小事，給身體輕斷食"},
        "雙子座": {"weak": "思緒過度發散，淺嚐輒止，神經系統緊繃", "tip": "每天只追蹤一件最重要的事，睡前做簡單伸展"},
        "巨蟹座": {"weak": "情緒容易內化，過度保護自己或他人，胃敏感", "tip": "情緒來時先問『這是我的感受還是我承接的？』"},
        "獅子座": {"weak": "自尊心過強，忽視身體疲勞訊號，心臟負擔", "tip": "允許自己『不漂亮』一天，早睡比熬夜奮鬥更榮耀"},
        "處女座": {"weak": "過度批判（自己/他人），腸胃敏感，容易焦慮", "tip": "每天寫下三件『已經夠好』的事，放下完美清單"},
        "天秤座": {"weak": "過度在意他人看法，決策疲勞，腎上腺耗弱", "tip": "先做決定再詢問意見，練習說『我需要想一下』"},
        "天蠍座": {"weak": "情緒埋藏過深，容易鑽牛角尖，生殖/泌尿系統", "tip": "找一個安全對象每週釋放一次真實感受，不評判"},
        "射手座": {"weak": "過度樂觀忽略細節，肝臟負擔大，承諾恐懼", "tip": "把大夢想切成可執行的 30 天小目標"},
        "摩羯座": {"weak": "壓抑情緒、過度工作，骨骼/關節/皮膚乾燥", "tip": "設定『無用時間』，什麼都不做也是成就"},
        "水瓶座": {"weak": "疏離感、腦過度運轉，循環系統/小腿痠痛", "tip": "每天與身體對話 5 分鐘（摸脈搏、感受呼吸）"},
        "雙魚座": {"weak": "邊界模糊、過度吸收他人情緒，免疫系統/腳部", "tip": "進入公共場合前先想像自己被金光包圍（結界）"},
        # Backend returns signs without "座"
        "牡羊": {"weak": "容易衝動、缺乏耐心，受傷後難以釋懷", "tip": "發脾氣前先做 10 次深呼吸，寫下『我真正需要什麼』"},
        "金牛": {"weak": "過度固執、抗拒改變，身體容易囤積（水腫/體重）", "tip": "每週嘗試一件『以前不會做』的小事，給身體輕斷食"},
        "雙子": {"weak": "思緒過度發散，淺嚐輒止，神經系統緊繃", "tip": "每天只追蹤一件最重要的事，睡前做簡單伸展"},
        "巨蟹": {"weak": "情緒容易內化，過度保護自己或他人，胃敏感", "tip": "情緒來時先問『這是我的感受還是我承接的？』"},
        "獅子": {"weak": "自尊心過強，忽視身體疲勞訊號，心臟負擔", "tip": "允許自己『不漂亮』一天，早睡比熬夜奮鬥更榮耀"},
        "處女": {"weak": "過度批判（自己/他人），腸胃敏感，容易焦慮", "tip": "每天寫下三件『已經夠好』的事，放下完美清單"},
        "天秤": {"weak": "過度在意他人看法，決策疲勞，腎上腺耗弱", "tip": "先做決定再詢問意見，練習說『我需要想一下』"},
        "天蠍": {"weak": "情緒埋藏過深，容易鑽牛角尖，生殖/泌尿系統", "tip": "找一個安全對象每週釋放一次真實感受，不評判"},
        "射手": {"weak": "過度樂觀忽略細節，肝臟負擔大，承諾恐懼", "tip": "把大夢想切成可執行的 30 天小目標"},
        "摩羯": {"weak": "壓抑情緒、過度工作，骨骼/關節/皮膚乾燥", "tip": "設定『無用時間』，什麼都不做也是成就"},
        "水瓶": {"weak": "疏離感、腦過度運轉，循環系統/小腿痠痛", "tip": "每天與身體對話 5 分鐘（摸脈搏、感受呼吸）"},
        "雙魚": {"weak": "邊界模糊、過度吸收他人情緒，免疫系統/腳部", "tip": "進入公共場合前先想像自己被金光包圍（結界）"}
    },
    "zh-CN": {
        "牡羊座": {"weak": "容易冲动、缺乏耐心，受伤后难以释怀", "tip": "发脾气前先做 10 次深呼吸，写下『我真正需要什么』"},
        "金牛座": {"weak": "过度固执、抗拒改变，身体容易囤积（水肿/体重）", "tip": "每周尝试一件『以前不会做』的小事，给身体轻断食"},
        "雙子座": {"weak": "思绪过度发散，浅尝辄止，神经系统紧绷", "tip": "每天只追踪一件最重要的事，睡前做简单伸展"},
        "巨蟹座": {"weak": "情绪容易内化，过度保护自己或他人，胃敏感", "tip": "情绪来时先问『这是我的感受还是我承接的？』"},
        "獅子座": {"weak": "自尊心过强，忽视身体疲劳信号，心脏负担", "tip": "允许自己『不漂亮』一天，早睡比熬夜奋斗更荣耀"},
        "處女座": {"weak": "过度批判（自己/他人），肠胃敏感，容易焦虑", "tip": "每天写下三件『已经够好』的事，放下完美清单"},
        "天秤座": {"weak": "过度在意他人看法，决策疲劳，肾上腺耗弱", "tip": "先做决定再询问意见，练习说『我需要想一下』"},
        "天蠍座": {"weak": "情绪埋藏过深，容易钻牛角尖，生殖/泌尿系统", "tip": "找一个安全对象每周释放一次真实感受，不评判"},
        "射手座": {"weak": "过度乐观忽略细节，肝脏负担大，承诺恐惧", "tip": "把大梦想切成可执行的 30 天小目标"},
        "摩羯座": {"weak": "压抑情绪、过度工作，骨骼/关节/皮肤干燥", "tip": "设定『无用时间』，什么都不做也是成就"},
        "水瓶座": {"weak": "疏离感、脑过度运转，循环系统/小腿酸痛", "tip": "每天与身体对话 5 分钟（摸脉搏、感受呼吸）"},
        "雙魚座": {"weak": "边界模糊、过度吸收他人情绪，免疫系统/脚部", "tip": "进入公共场合前先想象自己被金光包围（结界）"},
        # Backend returns signs without "座"
        "牡羊": {"weak": "容易冲动、缺乏耐心，受伤后难以释怀", "tip": "发脾气前先做 10 次深呼吸，写下『我真正需要什么』"},
        "金牛": {"weak": "过度固执、抗拒改变，身体容易囤积（水肿/体重）", "tip": "每周尝试一件『以前不会做』的小事，给身体轻断食"},
        "雙子": {"weak": "思绪过度发散，浅尝辄止，神经系统紧绷", "tip": "每天只追踪一件最重要的事，睡前做简单伸展"},
        "巨蟹": {"weak": "情绪容易内化，过度保护自己或他人，胃敏感", "tip": "情绪来时先问『这是我的感受还是我承接的？』"},
        "獅子": {"weak": "自尊心过强，忽视身体疲劳信号，心脏负担", "tip": "允许自己『不漂亮』一天，早睡比熬夜奋斗更荣耀"},
        "處女": {"weak": "过度批判（自己/他人），肠胃敏感，容易焦虑", "tip": "每天写下三件『已经够好』的事，放下完美清单"},
        "天秤": {"weak": "过度在意他人看法，决策疲劳，肾上腺耗弱", "tip": "先做决定再询问意见，练习说『我需要想一下』"},
        "天蠍": {"weak": "情绪埋藏过深，容易钻牛角尖，生殖/泌尿系统", "tip": "找一个安全对象每周释放一次真实感受，不评判"},
        "射手": {"weak": "过度乐观忽略细节，肝脏负担大，承诺恐惧", "tip": "把大梦想切成可执行的 30 天小目标"},
        "摩羯": {"weak": "压抑情绪、过度工作，骨骼/关节/皮肤干燥", "tip": "设定『无用时间』，什么都不做也是成就"},
        "水瓶": {"weak": "疏离感、脑过度运转，循环系统/小腿酸痛", "tip": "每天与身体对话 5 分钟（摸脉搏、感受呼吸）"},
        "雙魚": {"weak": "边界模糊、过度吸收他人情绪，免疫系统/脚部", "tip": "进入公共场合前先想象自己被金光包围（结界）"}
    },
    "en": {
        "Aries": {"weak": "Impulsive, impatient, holds grudges", "tip": "10 deep breaths before reacting, write 'What do I really need?'"},
        "Taurus": {"weak": "Overly stubborn, resistant to change, prone to water retention", "tip": "Try one 'I wouldn't do this' thing weekly, give your body a light fast"},
        "Gemini": {"weak": "Scattered thinking, superficial, nervous system tension", "tip": "Track only ONE priority daily, simple stretches before bed"},
        "Cancer": {"weak": "Internalizes emotions, overprotective, sensitive stomach", "tip": "Ask: 'Is this my feeling or one I absorbed from others?'"},
        "Leo": {"weak": "Prideful, ignores body fatigue signals, heart strain", "tip": "Allow yourself one 'not pretty' day; early sleep is more glorious than late hustle"},
        "Virgo": {"weak": "Overly critical, sensitive digestion, anxiety-prone", "tip": "Write three 'good enough' things daily, drop the perfect checklist"},
        "Libra": {"weak": "Overly concerned with others' opinions, decision fatigue", "tip": "Decide first, ask opinions second. Practice saying 'I need to think about it'"},
        "Scorpio": {"weak": "Buries emotions deeply, obsessive, reproductive/urinary sensitivity", "tip": "Find one safe person to release real feelings weekly, no judgment"},
        "Sagittarius": {"weak": "Overly optimistic misses details, liver strain, commitment fear", "tip": "Cut big dreams into actionable 30-day goals"},
        "Capricorn": {"weak": "Suppresses emotions, overworks, bone/joint/dry skin issues", "tip": "Schedule 'useless time'—doing nothing is also an achievement"},
        "Aquarius": {"weak": "Detached, overthinking, circulation/calf pain", "tip": "5-min body dialogue daily (feel pulse, notice breath)"},
        "Pisces": {"weak": "Blurry boundaries, absorbs others' emotions, immune/foot issues", "tip": "Imagine golden light surrounding you before entering public spaces"},
        # Chinese keys as fallback since backend returns Chinese signs (with and without 座)
        "牡羊座": {"weak": "Impulsive, impatient, holds grudges", "tip": "10 deep breaths before reacting, write 'What do I really need?'"},
        "金牛座": {"weak": "Overly stubborn, resistant to change, prone to water retention", "tip": "Try one 'I wouldn't do this' thing weekly, give your body a light fast"},
        "雙子座": {"weak": "Scattered thinking, superficial, nervous system tension", "tip": "Track only ONE priority daily, simple stretches before bed"},
        "巨蟹座": {"weak": "Internalizes emotions, overprotective, sensitive stomach", "tip": "Ask: 'Is this my feeling or one I absorbed from others?'"},
        "獅子座": {"weak": "Prideful, ignores body fatigue signals, heart strain", "tip": "Allow yourself one 'not pretty' day; early sleep is more glorious than late hustle"},
        "處女座": {"weak": "Overly critical, sensitive digestion, anxiety-prone", "tip": "Write three 'good enough' things daily, drop the perfect checklist"},
        "天秤座": {"weak": "Overly concerned with others' opinions, decision fatigue", "tip": "Decide first, ask opinions second. Practice saying 'I need to think about it'"},
        "天蠍座": {"weak": "Buries emotions deeply, obsessive, reproductive/urinary sensitivity", "tip": "Find one safe person to release real feelings weekly, no judgment"},
        "射手座": {"weak": "Overly optimistic misses details, liver strain, commitment fear", "tip": "Cut big dreams into actionable 30-day goals"},
        "摩羯座": {"weak": "Suppresses emotions, overworks, bone/joint/dry skin issues", "tip": "Schedule 'useless time'—doing nothing is also an achievement"},
        "水瓶座": {"weak": "Detached, overthinking, circulation/calf pain", "tip": "5-min body dialogue daily (feel pulse, notice breath)"},
        "雙魚座": {"weak": "Blurry boundaries, absorbs others' emotions, immune/foot issues", "tip": "Imagine golden light surrounding you before entering public spaces"},
        "牡羊": {"weak": "Impulsive, impatient, holds grudges", "tip": "10 deep breaths before reacting, write 'What do I really need?'"},
        "金牛": {"weak": "Overly stubborn, resistant to change, prone to water retention", "tip": "Try one 'I wouldn't do this' thing weekly, give your body a light fast"},
        "雙子": {"weak": "Scattered thinking, superficial, nervous system tension", "tip": "Track only ONE priority daily, simple stretches before bed"},
        "巨蟹": {"weak": "Internalizes emotions, overprotective, sensitive stomach", "tip": "Ask: 'Is this my feeling or one I absorbed from others?'"},
        "獅子": {"weak": "Prideful, ignores body fatigue signals, heart strain", "tip": "Allow yourself one 'not pretty' day; early sleep is more glorious than late hustle"},
        "處女": {"weak": "Overly critical, sensitive digestion, anxiety-prone", "tip": "Write three 'good enough' things daily, drop the perfect checklist"},
        "天秤": {"weak": "Overly concerned with others' opinions, decision fatigue", "tip": "Decide first, ask opinions second. Practice saying 'I need to think about it'"},
        "天蠍": {"weak": "Buries emotions deeply, obsessive, reproductive/urinary sensitivity", "tip": "Find one safe person to release real feelings weekly, no judgment"},
        "射手": {"weak": "Overly optimistic misses details, liver strain, commitment fear", "tip": "Cut big dreams into actionable 30-day goals"},
        "摩羯": {"weak": "Suppresses emotions, overworks, bone/joint/dry skin issues", "tip": "Schedule 'useless time'—doing nothing is also an achievement"},
        "水瓶": {"weak": "Detached, overthinking, circulation/calf pain", "tip": "5-min body dialogue daily (feel pulse, notice breath)"},
        "雙魚": {"weak": "Blurry boundaries, absorbs others' emotions, immune/foot issues", "tip": "Imagine golden light surrounding you before entering public spaces"}
    }
}

# Xingxiu life-domain weaknesses (simplified 28 mansions)
_XINGXIU_DOMAIN = {
    "zh-TW": {
        "角": "職場人際", "亢": "情緒管理", "氐": "家庭關係", "房": "財務規劃",
        "心": "心臟循環", "尾": "溝通表達", "箕": "行動執行", "斗": "自我認同",
        "牛": "物質安全感", "女": "女性能量", "虛": "想像力/腎氣", "危": "風險判斷",
        "室": "居住環境", "壁": "邊界設定", "奎": "學習吸收", "婁": "人際合作",
        "胃": "消化吸收", "昴": "審美/皮膚", "畢": "長期規劃", "觜": "細節執行",
        "参": "冒險/肝膽", "井": "資源整合", "鬼": "直覺/免疫力", "柳": "公眾形象",
        "星": "創意表達", "張": "社交能量", "翼": "資訊篩選", "軫": "出行/溝通"
    },
    "zh-CN": {
        "角": "职场人际", "亢": "情绪管理", "氐": "家庭关系", "房": "财务规划",
        "心": "心脏循环", "尾": "沟通表达", "箕": "行动执行", "斗": "自我认同",
        "牛": "物质安全感", "女": "女性能量", "虚": "想像力/肾气", "危": "风险判断",
        "室": "居住环境", "壁": "边界设定", "奎": "学习吸收", "娄": "人际合作",
        "胃": "消化吸收", "昴": "审美/皮肤", "毕": "长期规划", "觜": "细节执行",
        "参": "冒险/肝胆", "井": "资源整合", "鬼": "直觉/免疫力", "柳": "公众形象",
        "星": "创意表达", "张": "社交能量", "翼": "资讯筛选", "轸": "出行/沟通"
    },
    "en": {
        "角": "Workplace relations", "亢": "Emotional management", "氐": "Family dynamics", "房": "Financial planning",
        "心": "Heart circulation", "尾": "Communication", "箕": "Action execution", "斗": "Self-identity",
        "牛": "Material security", "女": "Feminine energy", "虚": "Imagination/kidney qi", "危": "Risk judgment",
        "室": "Living environment", "壁": "Boundary setting", "奎": "Learning absorption", "娄": "Teamwork",
        "胃": "Digestion", "昴": "Aesthetics/skin", "毕": "Long-term planning", "觜": "Detail execution",
        "参": "Adventure/liver", "井": "Resource integration", "鬼": "Intuition/immunity", "柳": "Public image",
        "星": "Creative expression", "张": "Social energy", "翼": "Information filtering", "轸": "Travel/communication"
    }
}

def _build_smart_prescription(chart: Dict[str, Any], lang: str = "zh-TW") -> List[Dict[str, str]]:
    """Generate personalized fallback prescriptions based on chart analysis."""
    p = PROMPTS.get(lang, PROMPTS["zh-TW"])
    is_en = lang == "en"
    is_cn = lang == "zh-CN"
    
    # Extract data
    bazi = chart.get("bazi", {})
    hd = chart.get("humandesign", {})
    astro = chart.get("astrology", {})
    xingxiu = chart.get("xingxiu", "")
    
    day_master = bazi.get("day_master", "")
    element_zh = _GAN_TO_ELEMENT.get(day_master[0] if day_master else "", "土")
    element = _ELEMENT_EN.get(element_zh, "Earth") if is_en else element_zh
    # Try sun_sign first, fallback to 太陽.sign (chart_service format)
    sun_sign = astro.get("sun_sign", "") or astro.get("太陽", {}).get("sign", "")
    if is_en:
        sun_sign = astro.get("sun_sign_en", "") or astro.get("sun_sign", "") or astro.get("太陽", {}).get("sign", "")
    hd_type = hd.get("energy_type", "")
    authority = hd.get("authority", "")
    
    # Look up localized data (use Chinese key for health since lookup table keys are Chinese)
    health = _ELEMENT_HEALTH.get(lang, _ELEMENT_HEALTH["zh-TW"]).get(element_zh, _ELEMENT_HEALTH["zh-TW"]["土"])
    zodiac = _ZODIAC_WEAKNESS.get(lang, _ZODIAC_WEAKNESS["zh-TW"]).get(sun_sign, None)
    hd_weak = _HD_WEAKNESS.get(lang, _HD_WEAKNESS["zh-TW"]).get(hd_type, None)
    
    # Extract xingxiu first char for domain lookup
    xiu_char = xingxiu[0] if xingxiu else ""
    domain = _XINGXIU_DOMAIN.get(lang, _XINGXIU_DOMAIN["zh-TW"]).get(xiu_char, "")
    
    if is_en:
        # English prescriptions
        p1 = {"icon": "🫁", "title": f"Protect your {health['organ']}", "description": f"Your {element} Day Master indicates: {health['weak']}. {health['tip']}."}
        p2 = {"icon": "🧘", "title": f"Manage {sun_sign} tendencies", "description": zodiac['weak'] + ". " + zodiac['tip'] + "." if zodiac else f"Your Sun sign {sun_sign} has unique emotional patterns worth observing daily."}
        p3 = {"icon": "⚡", "title": f"{hd_type} energy care", "description": hd_weak['weak'] + ". " + hd_weak['tip'] + "." if hd_weak else f"Your {hd_type} design benefits from regular energy check-ins."}
        p4 = {"icon": "🔮", "title": f"Strengthen {domain}" if domain else "Build core stability", "description": f"Your {xingxiu} Lunar Mansion highlights {domain} as an area for conscious development." if domain else "Focus on one life domain each month for steady growth."}
        p5 = {"icon": "🌙", "title": f"Honor your {authority} authority", "description": f"With {authority} as your inner authority, rushing decisions drains you. Create a 24-hour buffer for major choices." if authority else "Give yourself a full day before making important decisions."}
        return [p1, p2, p3, p4, p5]
    
    # Chinese prescriptions (zh-TW or zh-CN)
    cn = "简体" if is_cn else "繁體"
    p1 = {"icon": "🫁", "title": f"保養{health['organ']}", "description": f"你的日主五行屬{element}，對應{health['organ']}較弱。{health['weak']}。→ {health['tip']}"}
    p2 = {"icon": "🧘", "title": f"覺察{sun_sign}模式", "description": zodiac['weak'] + "。→ " + zodiac['tip'] if zodiac else f"你的太陽星座{sun_sign}有獨特的情緒模式，值得每天觀察。"}
    p3 = {"icon": "⚡", "title": f"{hd_type}能量保養", "description": hd_weak['weak'] + "。→ " + hd_weak['tip'] if hd_weak else f"你的{hd_type}設計需要定期檢視能量狀態。"}
    p4 = {"icon": "🔮", "title": f"強化{domain}" if domain else "建立核心穩定", "description": f"你的星宿{xingxiu}顯示「{domain}」是你這一生的發展課題，需要有意識地投入。" if domain else "每個月專注提升一個人生面向，累積穩定成長。"}
    # Avoid "權威權威" duplication if authority already contains "權威"
    auth_title = authority.replace("權威", "") if authority and "權威" in authority else authority
    p5 = {"icon": "🌙", "title": f"尊重{auth_title}權威", "description": f"你的內在權威是{authority}，倉促決定會消耗你。→ 重大決定前給自己 24 小時緩衝。" if authority else "重大決定前給自己完整一天的沉澱時間。"}
    return [p1, p2, p3, p4, p5]


def _get_prompt(lang: str, key: str) -> str:
    """Get prompt for language, fallback to zh-TW"""
    return PROMPTS.get(lang, PROMPTS["zh-TW"]).get(key, "")


def _serialize_chart(chart: Dict[str, Any]) -> str:
    """Serialize chart data for AI prompt"""
    return json.dumps(chart, ensure_ascii=False, indent=2)


def _build_personal_tier_prompt(base_schema: str, tier: str, lang: str) -> str:
    """Adjust prompt based on tier level"""
    is_zh = lang.startswith("zh")
    
    if tier == "lite":
        addon = """
重要：這是 Lite 版本，請精簡輸出：
- integrated_profile: 150-200 字即可
- strengths_weaknesses: 可省略或極簡（每項 1 句話）
- life_lessons: 1 句話核心洞察即可
- prescription: 只需 2 條處方
""" if is_zh else """
Important: This is the Lite version, please keep it concise:
- integrated_profile: 150-200 words max
- strengths_weaknesses: optional or very brief
- life_lessons: one sentence core insight
- prescription: only 2 items
"""
    elif tier == "premium":
        addon = """
重要：這是 Premium 版本，請深度輸出：
- integrated_profile: 300-400 字，更具體、更有畫面感
- strengths_weaknesses: 每項優缺點都要具體到「這個人」的獨特表現
- life_lessons: 200 字深度洞察，包含具體建議
- prescription: 5 條處方，每條都要有具體執行方式
- 額外加入 "relationship_tips": 給不同類型的人（父母/伴侶/朋友）的相處建議
""" if is_zh else """
Important: This is the Premium version, please go deep:
- integrated_profile: 300-400 words, vivid and specific
- strengths_weaknesses: each item specific to this person
- life_lessons: 200 words with actionable advice
- prescription: 5 items with specific execution steps
- Extra field "relationship_tips": advice for parents/partners/friends
"""
    else:
        addon = """
重要：這是 Standard 版本，請平衡深度與長度：
- integrated_profile: 200-300 字
- strengths_weaknesses: 五個維度各給優缺點
- life_lessons: 100-150 字
- prescription: 3-4 條處方
""" if is_zh else """
Important: This is the Standard version, balanced depth:
- integrated_profile: 200-300 words
- strengths_weaknesses: all five dimensions
- life_lessons: 100-150 words
- prescription: 3-4 items
"""
    
    return base_schema + addon


async def generate_personal_report(chart: Dict[str, Any], lang: str = "zh-TW", tier: str = "standard") -> Dict[str, Any]:
    """Generate AI-powered personal full report"""
    p = PROMPTS.get(lang, PROMPTS["zh-TW"])
    
    if not client or not settings.OPENAI_API_KEY:
        # Fallback: return structured placeholders when AI is not configured
        day_master = chart['bazi'].get('day_master', '?')
        xingxiu = chart.get('xingxiu', '?')
        energy_type = chart['humandesign'].get('energy_type', '?')
        authority = chart['humandesign'].get('authority', '?')
        
        smart_prescriptions = _build_smart_prescription(chart, lang)
        result = {
            "integrated_profile": p["fallback_profile"].format(
                day_master=day_master, xingxiu=xingxiu, energy_type=energy_type
            ),
            "strengths_weaknesses": p["fallback_sw"] if tier != "lite" else {},
            "life_lessons": p["fallback_lessons"],
            "prescription": smart_prescriptions[:2 if tier == "lite" else (5 if tier == "premium" else 3)]
        }
        if tier == "premium":
            result["relationship_tips"] = {
                "父母": "多表達感謝，讓他們知道你的保護是雙向的",
                "伴侶": "給對方空間，同時學會說『我需要你』",
                "朋友": "不必總是撐住全場，偶爾示弱也是一種信任"
            }
        return result
    
    chart_text = _serialize_chart(chart)
    schema = _build_personal_tier_prompt(p['schema_personal'], tier, lang)
    prompt = f"Chart data:\n{chart_text}\n\n{schema}"
    
    max_tokens = {"lite": 800, "standard": 1500, "premium": 2500}.get(tier, 1500)
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": p["system_personal"]},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=max_tokens
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    result["_ai_metadata"] = {
        "model": response.model,
        "tier": tier,
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0
    }
    return result


def _build_compat_tier_prompt(base_schema: str, tier: str, lang: str) -> str:
    """Adjust compatibility prompt based on tier level"""
    is_zh = lang.startswith("zh")
    
    if tier == "lite":
        addon = """
重要：這是 Lite 版本，請精簡輸出：
- relationship_narrative: 150-200 字即可
- conflict_points: 可省略或只給 1 條
- communication_guide: 可省略或極簡
- prescription: 只需 2 條
""" if is_zh else """
Important: Lite version, keep concise:
- relationship_narrative: 150-200 words
- conflict_points: optional or 1 item
- communication_guide: optional/brief
- prescription: only 2 items
"""
    elif tier == "premium":
        addon = """
重要：這是 Premium 版本，請深度輸出：
- relationship_narrative: 300-400 字，更具體生動
- conflict_points: 3-4 個具體衝突點，每個都要深入分析
- communication_guide: 6-8 條具體建議，涵蓋不同情境
- prescription: 4-5 條行動建議，含具體執行方式
- 額外加入 "growth_plan": 這段關係的 30 天成長計畫
""" if is_zh else """
Important: Premium version, go deep:
- relationship_narrative: 300-400 words
- conflict_points: 3-4 detailed items
- communication_guide: 6-8 specific scenarios
- prescription: 4-5 actionable items
- Extra field "growth_plan": 30-day relationship growth plan
"""
    else:
        addon = """
重要：這是 Standard 版本，請平衡深度與長度：
- relationship_narrative: 200-300 字
- conflict_points: 2-3 個衝突點
- communication_guide: 4 條建議
- prescription: 3-4 條處方
""" if is_zh else """
Important: Standard version, balanced:
- relationship_narrative: 200-300 words
- conflict_points: 2-3 items
- communication_guide: 4 suggestions
- prescription: 3-4 items
"""
    
    return base_schema + addon


async def generate_compatibility_report(chart1: Dict[str, Any], chart2: Dict[str, Any], basic_compat: Dict[str, Any], lang: str = "zh-TW", tier: str = "standard") -> Dict[str, Any]:
    """Generate AI-powered deep compatibility report"""
    p = PROMPTS.get(lang, PROMPTS["zh-TW"])
    
    if not client or not settings.OPENAI_API_KEY:
        score = basic_compat.get('overall_score', '?')
        summary = basic_compat.get('summary', '')
        result = {
            "relationship_narrative": p["fallback_compat_narrative"].format(score=score, summary=summary),
            "conflict_points": p["fallback_conflict"][:1 if tier == "lite" else (4 if tier == "premium" else 2)],
            "communication_guide": {} if tier == "lite" else p["fallback_comm_guide"],
            "prescription": p["fallback_compat_prescription"][:2 if tier == "lite" else (5 if tier == "premium" else 3)]
        }
        if tier == "premium":
            result["growth_plan"] = {
                "week1": "每天 10 分鐘分享當天感受",
                "week2": "一起做一件對方喜歡的事",
                "week3": "討論一個衝突點，練習新溝通方式",
                "week4": "寫一封信給對方，不發，只是整理感受"
            }
        return result
    
    data_text = f"""
[Person 1]
{_serialize_chart(chart1)}

[Person 2]
{_serialize_chart(chart2)}

[Basic Compatibility Result]
{_serialize_chart(basic_compat)}

{_build_compat_tier_prompt(p['schema_compat'], tier, lang)}
"""
    
    max_tokens = {"lite": 800, "standard": 1500, "premium": 3000}.get(tier, 1500)
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": p["system_compat"]},
            {"role": "user", "content": data_text}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=max_tokens
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    result["_ai_metadata"] = {
        "model": response.model,
        "tier": tier,
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0
    }
    return result


# ---------- Q&A fallback templates ----------

_ASK_KEYWORDS = {
    "zh-TW": {
        "職業": {"kw": ["工作", "職業", "行業", "創業", "事業", "賺錢", "老闆", "上班", "辭職", "轉職", "設計師", "工程師", "老師", "醫生", "律師", "藝術家", "作家", "程式", "行銷", "業務", "管理", "職位", "升遷", "跳槽"], "systems": ["八字", "紫微", "人類圖"]},
        "感情": {"kw": ["戀愛", "感情", "結婚", "桃花", "對象", "分手", "復合", "單身", "追求者", "曖昧"], "systems": ["八字", "占星", "星宿"]},
        "健康": {"kw": ["健康", "身體", "病", "睡眠", "飲食", "運動", "減肥", "疲勞"], "systems": ["八字", "人類圖"]},
        "人際": {"kw": ["朋友", "人際", "同事", "家人", "父母", "相處", "衝突", "社交"], "systems": ["占星", "人類圖", "星宿"]},
        "決策": {"kw": ["決定", "選擇", "該不該", "要不要", "適合", "方向", "迷茫"], "systems": ["八字", "紫微", "人類圖"]},
    },
    "zh-CN": {
        "职业": {"kw": ["工作", "职业", "行业", "创业", "事业", "赚钱", "老板", "上班", "辞职", "转职", "设计师", "工程师", "老师", "医生", "律师", "艺术家", "作家", "程序", "营销", "业务", "管理", "职位", "升迁", "跳槽"], "systems": ["八字", "紫微", "人类图"]},
        "感情": {"kw": ["恋爱", "感情", "结婚", "桃花", "对象", "分手", "复合", "单身", "追求者", "暧昧"], "systems": ["八字", "占星", "星宿"]},
        "健康": {"kw": ["健康", "身体", "病", "睡眠", "饮食", "运动", "减肥", "疲劳"], "systems": ["八字", "人类图"]},
        "人际": {"kw": ["朋友", "人际", "同事", "家人", "父母", "相处", "冲突", "社交"], "systems": ["占星", "人类图", "星宿"]},
        "决策": {"kw": ["决定", "选择", "该不该", "要不要", "适合", "方向", "迷茫"], "systems": ["八字", "紫微", "人类图"]},
    },
    "en": {
        "career": {"kw": ["job", "career", "work", "business", "industry", "money", "boss", "startup", "quit", "promotion", "designer", "engineer", "teacher", "doctor", "lawyer", "artist", "writer", "programmer", "marketing", "sales", "manager", "position", "raise", "jump"], "systems": ["Bazi", "Zi Wei", "Human Design"]},
        "relationship": {"kw": ["love", "relationship", "marriage", "dating", "partner", "breakup", "single", "crush", "romance"], "systems": ["Bazi", "Astrology", "Xingxiu"]},
        "health": {"kw": ["health", "body", "sick", "sleep", "diet", "exercise", "tired", "fatigue"], "systems": ["Bazi", "Human Design"]},
        "social": {"kw": ["friend", "social", "colleague", "family", "parent", "get along", "conflict", "people"], "systems": ["Astrology", "Human Design", "Xingxiu"]},
        "decision": {"kw": ["decide", "choice", "should I", "direction", "confused", "lost", "path"], "systems": ["Bazi", "Zi Wei", "Human Design"]},
    }
}

def _classify_question(question: str, lang: str) -> tuple:
    """Classify question type and return category + relevant systems"""
    q = question.lower()
    kw_dict = _ASK_KEYWORDS.get(lang, _ASK_KEYWORDS["zh-TW"])
    for category, data in kw_dict.items():
        for kw in data["kw"]:
            if kw.lower() in q:
                return category, data["systems"]
    return "general", ["八字", "占星", "紫微", "人類圖", "星宿"] if lang.startswith("zh") else ["Bazi", "Astrology", "Zi Wei", "Human Design", "Xingxiu"]

def _build_fallback_answer(chart: Dict[str, Any], question: str, lang: str) -> Dict[str, Any]:
    """Build a smart fallback answer based on chart traits and question type"""
    category, systems = _classify_question(question, lang)
    
    bazi = chart.get("bazi", {})
    hd = chart.get("humandesign", {})
    astro = chart.get("astrology", {})
    xx = chart.get("xingxiu", "")
    
    day_master = bazi.get("day_master", "")
    element = _GAN_TO_ELEMENT.get(day_master[0] if day_master else "", "土")
    hd_type = hd.get("energy_type", "")
    sun_sign = astro.get("太陽", {}).get("sign", "") if isinstance(astro, dict) else ""
    
    is_en = lang == "en"
    
    if is_en:
        # English fallback answers
        if category == "career":
            answer = f"Your Day Master is {day_master} ({element}), and you're a {hd_type}. {element} energy tends to {'thrive in structured environments' if element in ['金', '土'] else 'excel in creative or fluid environments' if element in ['木', '水'] else 'lead and inspire others'}. As a {hd_type}, your work strategy is unique—{'wait to respond' if hd_type == '生產者' else 'wait for invitation' if hd_type == '投射者' else 'initiate and inform' if hd_type == '顯示者' else 'reflect over time'}. The key is not forcing yourself into a mold that doesn't fit your design."
            confidence = "Medium"
        elif category == "relationship":
            answer = f"With your Sun in {sun_sign} and {xx} Lunar Mansion, you have a unique emotional rhythm. {sun_sign} brings {'spontaneity and curiosity' if sun_sign in ['雙子', '射手', '水瓶'] else 'depth and intensity' if sun_sign in ['天蠍', '巨蟹', '雙魚'] else 'warmth and loyalty' if sun_sign in ['獅子', '金牛', '天秤'] else 'passion and directness'} to relationships. Your Human Design type ({hd_type}) suggests {'waiting for the right invitation' if hd_type == '投射者' else 'responding to what excites you' if hd_type in ['生產者', '顯示生產者'] else 'initiating when you feel the impulse'}. Timing matters more than rushing."
            confidence = "Medium"
        elif category == "health":
            health_info = _ELEMENT_HEALTH["en"].get(element, _ELEMENT_HEALTH["en"]["土"])
            answer = f"From a Bazi perspective, your {element} Day Master connects to the {health_info['organ']}. {health_info['weak']}. Your {hd_type} design also plays a role—{'sacral energy needs rest' if hd_type in ['生產者', '顯示生產者'] else 'your sensitive aura needs decompression' if hd_type == '投射者' else 'environment affects you deeply' if hd_type == '反映者' else 'throat pressure needs release'}. Listen to your body signals."
            confidence = "High"
        elif category == "decision":
            answer = f"Your inner authority is {hd.get('authority', 'unknown')}. With {day_master} Day Master and {sun_sign} Sun, you tend to {'overthink' if sun_sign in ['雙子', '處女', '水瓶'] else 'follow intuition' if sun_sign in ['巨蟹', '雙魚', '天蠍'] else 'act decisively' if sun_sign in ['牡羊', '獅子', '射手'] else 'seek balance'}. The key insight from your chart: don't let external pressure override your inner signal. Give yourself the time your design requires."
            confidence = "Medium"
        else:
            answer = f"Your chart shows a {day_master} Day Master with {sun_sign} Sun and {hd_type} design. Each system offers a different lens on your question. The common thread across all five systems is: trust your unique design rather than forcing conventional paths. Your {xx} Lunar Mansion especially highlights the importance of {'authentic expression' if xx in ['角', '井', '星'] else 'inner stability' if xx in ['亢', '斗', '室'] else 'meaningful connections' if xx in ['尾', '心', '張'] else 'steady growth'} in this area of life."
            confidence = "Low"
        
        return {
            "answer": answer,
            "relevant_systems": systems,
            "confidence": confidence,
            "disclaimer": "This answer is for reference only. Please use rational judgment and consider your actual circumstances."
        }
    
    # Chinese fallback (zh-TW or zh-CN)
    use_cn = lang == "zh-CN"
    
    if category == "職業" or category == "职业":
        answer = f"你的日主是{day_master}（五行屬{element}），人類圖類型是{hd_type}。{element}日主的人通常{'適合有架構、能累積專業的工作' if element in ['金', '土'] else '在變動、創意或需要靈活應變的領域表現較好' if element in ['木', '水'] else '適合能發揮影響力、帶動他人的角色'}。以你的人類圖來說，{hd_type}的你在職場上最好的策略是{'等待對的事物來敲門，再用薦骨回應' if hd_type == '生產者' else '等待被邀請，再發揮你的洞察力' if hd_type == '投射者' else '主動發起，但記得先告知他人' if hd_type == '顯示者' else '給自己完整的28天週期來感受'}。重點不是『選對行業』，是『用你的方式做』。"
        confidence = "中"
    elif category == "感情":
        answer = f"你的太陽星座在{sun_sign}，星宿是{xx}宿。{sun_sign}的你在感情中帶來{'好奇與輕快，但容易三分鐘熱度' if sun_sign in ['雙子', '射手', '水瓶'] else '深刻與敏感，但也容易患得患失' if sun_sign in ['天蠍', '巨蟹', '雙魚'] else '溫暖與忠誠，但偶爾過於依賴或強勢' if sun_sign in ['獅子', '金牛', '天秤'] else '熱情與直率，但需要學會柔軟'}。你的人類圖類型{hd_type}在關係中{'需要被正確邀請，才不會耗竭' if hd_type == '投射者' else '要用薦骨感受對方是否讓你飽滿' if hd_type in ['生產者', '顯示生產者'] else '要學會主動告知，而不是悶著' if hd_type == '顯示者' else '需要長時間觀察對方和環境'}。現在適不適合談戀愛，不如問：『這個人讓我感覺像我自己嗎？』"
        confidence = "中"
    elif category == "健康":
        health_info = _ELEMENT_HEALTH["zh-TW"].get(element, _ELEMENT_HEALTH["zh-TW"]["土"])
        answer = f"從八字來看，你的{element}日主對應{health_info['organ']}。{health_info['weak']}。你的人類圖類型{hd_type}也在提醒你：{'薦骨過載時身體會先知道，別忽略疲勞訊號' if hd_type in ['生產者', '顯示生產者'] else '能量場敏感，每天需要獨處排氣' if hd_type == '投射者' else '環境對你影響極大，居住品質比什麼都重要' if hd_type == '反映者' else '喉嚨壓力大，要學會說不'}。身體是最誠實的命盤。"
        confidence = "高"
    elif category == "人際" or category == "人际":
        answer = f"你的太陽{sun_sign}加上星宿{xx}宿，讓你在人際中{'容易成為焦點，但要注意別搶了所有人的風頭' if sun_sign in ['獅子', '牡羊'] else '擅長傾聽，但容易吸收太多他人情緒' if sun_sign in ['巨蟹', '雙魚', '天蠍'] else '喜歡和諧，但常常為了維持和平而委屈自己' if sun_sign in ['天秤', '金牛'] else '帶來輕快氣氛，但可能讓人覺得不夠深入' if sun_sign in ['雙子', '射手', '水瓶'] else '踏實可靠，但偶爾顯得過於嚴肅'}. {hd_type}的你在人際中最需要的是{'被看見你的價值，而不是你的付出' if hd_type == '投射者' else '被問對問題，才能給出最好的回應' if hd_type == '生產者' else '被允許主動，同時被理解' if hd_type == '顯示者' else '被給予時間和空間來感受'}。"
        confidence = "中"
    elif category == "決策" or category == "决策":
        answer = f"你的內在權威是{hd.get('authority', '未知')}。{day_master}日主加上{sun_sign}太陽，讓你在決策時傾向{'反覆分析、考慮太多選項' if sun_sign in ['雙子', '處女', '水瓶'] else '跟隨直覺、但事後容易懷疑' if sun_sign in ['巨蟹', '雙魚', '天蠍'] else '快速決定、但可能忽略細節' if sun_sign in ['牡羊', '獅子', '射手'] else '尋求共識、但可能拖太久'}. 人類圖給你的建議是：{'不要急，給情緒完整的波動週期' if '情緒' in hd.get('authority', '') else '注意身體的薦骨回應，不是頭腦的聲音' if '薦骨' in hd.get('authority', '') else '相信你的直覺，即使說不出原因' if '直覺' in hd.get('authority', '') else '把你的想法說出來，聽自己怎麼說' if '自我' in hd.get('authority', '') else '重大決定交給時間，28天後再看'}. 五個系統共同的提醒：你的設計不適合被催。"
        confidence = "中"
    else:
        answer = f"你的命盤顯示{day_master}日主、{sun_sign}太陽、{hd_type}設計、{xx}宿。五個系統從不同角度回答了這個問題，共同點是：{'你天生具備將不同面向整合為獨特路徑的能力' if element == '土' else '你需要在變動中找到自己的節奏' if element == '水' else '你的成長來自於敢於突破框架' if element == '木' else '你的核心課題是學會適時收斂與等待' if element == '火' else '你的力量在於精準與堅持'}. 與其問『該不該』，不如問『這件事讓我更像我自己，還是更不像？』"
        confidence = "低"
    
    disclaimer = "本回答僅供參考，請理性判斷並以自身實際情況為準。" if not use_cn else "本回答仅供参考，请理性判断并以自身实际情况为准。"
    
    return {
        "answer": answer,
        "relevant_systems": systems,
        "confidence": confidence,
        "disclaimer": disclaimer
    }


async def generate_answer(chart: Dict[str, Any], question: str, lang: str = "zh-TW", tier: str = "standard") -> Dict[str, Any]:
    """Generate AI answer to a chart-based question"""
    ask_p = ASK_PROMPTS.get(lang, ASK_PROMPTS["zh-TW"])
    
    if not client or not settings.OPENAI_API_KEY:
        return _build_fallback_answer(chart, question, lang)
    
    chart_text = _serialize_chart(chart)
    
    # Tier-based length control
    is_zh = lang.startswith("zh")
    if tier == "lite":
        length_hint = "回答請控制在 150 字以內。" if is_zh else "Keep answer under 150 words."
        max_tokens = 600
    elif tier == "premium":
        length_hint = "回答請寫 300-400 字，深入分析並給出具體例子。" if is_zh else "Write 300-400 words with deep analysis and specific examples."
        max_tokens = 1200
    else:
        length_hint = "回答請寫 200-300 字。" if is_zh else "Write 200-300 words."
        max_tokens = 800
    
    prompt = f"""使用者問題：{question}

命盤資料：
{chart_text}

{ask_p['schema_ask']}

{length_hint}"""
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": ask_p["system_ask"]},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=max_tokens
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    result["_ai_metadata"] = {
        "model": response.model,
        "tier": tier,
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0
    }
    return result


# ---------- Family & Annual Report Generation ----------

def _build_family_fallback(members: List[Dict[str, Any]], lang: str = "zh-TW") -> Dict[str, Any]:
    """Build a fallback family report when AI is not available"""
    is_en = lang == "en"
    
    # Extract key traits for each member
    member_reports = []
    for m in members:
        chart = m.get("chart", {})
        bazi = chart.get("bazi", {})
        hd = chart.get("humandesign", {})
        name = m.get("name", "未知")
        role = m.get("role", "member")
        
        dm = bazi.get("day_master", "")
        hd_type = hd.get("energy_type", "")
        element = _GAN_TO_ELEMENT.get(dm[0] if dm else "", "土")
        
        if is_en:
            role_names = {"father": "Father", "mother": "Mother", "child": "Child", "grandparent": "Grandparent"}
            family_roles = {
                "金": "The Anchor", "木": "The Growth Catalyst", "水": "The Flow Keeper",
                "火": "The Energy Igniter", "土": "The Grounding Force"
            }
            hd_roles = {
                "顯示者": "The Initiator", "生產者": "The Builder", "顯示生產者": "The Dynamic Doer",
                "投射者": "The Guide", "反映者": "The Mirror"
            }
            member_reports.append({
                "name": name,
                "role": role_names.get(role, "Member"),
                "chart_summary": f"{dm} Day Master ({element}), {hd_type} design",
                "family_role": f"{family_roles.get(element, 'Unique Contributor')} + {hd_roles.get(hd_type, 'Valued Member')}"
            })
        else:
            family_roles = {
                "金": "穩定錨點", "木": "成長催化劑", "水": "流動調節者",
                "火": "能量點火者", "土": "扎根力量"
            }
            hd_roles = {
                "顯示者": "發起者", "生產者": "建造者", "顯示生產者": "動態執行者",
                "投射者": "引導者", "反映者": "鏡子"
            }
            member_reports.append({
                "name": name,
                "role": {"father": "爸爸", "mother": "媽媽", "child": "孩子", "grandparent": "祖父母"}.get(role, "成員"),
                "chart_summary": f"{dm}日主（五行{element}），{hd_type}設計",
                "family_role": f"{family_roles.get(element, '獨特貢獻者')} + {hd_roles.get(hd_type, '珍貴成員')}"
            })
    
    # Build relationship matrix (simplified: just parent-child and couple pairs)
    relationship_matrix = []
    parents = [m for m in member_reports if m["role"] in ("Father", "Mother", "爸爸", "媽媽")]
    children = [m for m in member_reports if m["role"] in ("Child", "孩子")]
    
    if len(parents) >= 2:
        if is_en:
            relationship_matrix.append({
                "pair": [parents[0]["name"], parents[1]["name"]],
                "dynamic": "The core partnership that sets the family tone",
                "strength": "Shared commitment to family",
                "watch_out": "Don't lose individual identities in parenting roles"
            })
        else:
            relationship_matrix.append({
                "pair": [parents[0]["name"], parents[1]["name"]],
                "dynamic": "家庭的核心夥伴關係，決定整個家的氛圍",
                "strength": "對家庭的共同承諾",
                "watch_out": "不要只在父母角色中失去個人身份"
            })
    
    for p in parents[:1]:
        for c in children[:2]:
            if is_en:
                relationship_matrix.append({
                    "pair": [p["name"], c["name"]],
                    "dynamic": f"{p['family_role']} guiding {c['family_role']}",
                    "strength": "Natural complement of experience and fresh energy",
                    "watch_out": "Allow the child to develop their own path"
                })
            else:
                relationship_matrix.append({
                    "pair": [p["name"], c["name"]],
                    "dynamic": f"{p['family_role']} 引導 {c['family_role']}",
                    "strength": "經驗與新鮮能量的自然互補",
                    "watch_out": "允許孩子發展自己的路"
                })
    
    if is_en:
        return {
            "family_narrative": f"Your family of {len(members)} members is a unique constellation. Each person brings a distinct energy that creates a dynamic greater than the sum of its parts. The key to harmony is not making everyone the same, but honoring each person's unique design while finding the common thread that binds you together. (Set OPENAI_API_KEY for deeper AI analysis)",
            "member_reports": member_reports,
            "relationship_matrix": relationship_matrix,
            "family_prescription": [
                {"icon": "🏠", "title": "Weekly Family Check-in", "description": "Set aside 30 minutes each week for everyone to share one high and one low"},
                {"icon": "💬", "title": "Speak Each Person's Language", "description": "Notice how each family member prefers to give and receive care"},
                {"icon": "🎯", "title": "Respect Individual Rhythms", "description": "Not everyone recharges the same way—some need togetherness, some need solitude"}
            ],
            "communication_guide": {
                "When conflict arises": "Pause before reacting. Ask 'What does this person actually need right now?'",
                "Best time to communicate": "After meals or during shared activities, not when anyone is exhausted",
                "Space each person needs": "Notice who needs physical space vs. emotional space, and honor both"
            }
        }
    
    return {
        "family_narrative": f"你們這個{len(members)}人家庭是一個獨特的星群。每個人帶來不同的能量，創造出超越個體總和的動力學。和諧的關鍵不是讓每個人一樣，而是尊重每個人的獨特設計，同時找到連結你們的共同線索。（設定 OPENAI_API_KEY 以啟用更深入的 AI 分析）",
        "member_reports": member_reports,
        "relationship_matrix": relationship_matrix,
        "family_prescription": [
            {"icon": "🏠", "title": "每週家庭時光", "description": "每週保留30分鐘，讓每個人分享一件開心的事和一件困難的事"},
            {"icon": "💬", "title": "說對方的語言", "description": "觀察每個家庭成員喜歡如何給予和接收關心"},
            {"icon": "🎯", "title": "尊重個人節奏", "description": "不是每個人都用同樣方式充電——有些人需要陪伴，有些人需要獨處"}
        ],
        "communication_guide": {
            "當衝突發生時": "先暫停再反應。問自己『這個人現在真正需要的是什麼？』",
            "最好的溝通時機": "飯後或共同活動時，而不是任何人疲憊的時候",
            "每個人需要的空間": "注意誰需要物理空間、誰需要情感空間，並尊重兩者"
        }
    }


async def generate_family_report(members: List[Dict[str, Any]], lang: str = "zh-TW", tier: str = "standard") -> Dict[str, Any]:
    """Generate AI-powered family constellation report"""
    fp = FAMILY_PROMPTS.get(lang, FAMILY_PROMPTS["zh-TW"])
    
    if not client or not settings.OPENAI_API_KEY:
        return _build_family_fallback(members, lang)
    
    # Serialize all member charts
    members_text = "\n\n".join([
        f"[Member {i+1}: {m.get('name', 'Unknown')} - {m.get('role', 'member')}]\n{_serialize_chart(m.get('chart', {}))}"
        for i, m in enumerate(members)
    ])
    
    is_zh = lang.startswith("zh")
    if tier == "lite":
        length_hint = "請精簡輸出：family_narrative 150字，member_reports 每人1句話，relationship_matrix 只給最重要的1-2對。" if is_zh else "Keep it concise."
        max_tokens = 1000
    elif tier == "premium":
        length_hint = "請深度輸出：family_narrative 400字，每個關係都要深入分析，給出具體的家庭活動建議。" if is_zh else "Go deep with vivid specifics."
        max_tokens = 2500
    else:
        length_hint = "請平衡深度與長度。" if is_zh else "Balanced depth."
        max_tokens = 1800
    
    prompt = f"""以下是一個家庭的所有成員命盤資料：

{members_text}

{fp['schema']}

{length_hint}"""
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": fp["system"]},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=max_tokens
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    result["_ai_metadata"] = {
        "model": response.model,
        "tier": tier,
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0
    }
    return result


def _build_annual_fallback(chart: Dict[str, Any], year: int, lang: str = "zh-TW") -> Dict[str, Any]:
    """Build a fallback annual report when AI is not available"""
    bazi = chart.get("bazi", {})
    dm = bazi.get("day_master", "")
    element = _GAN_TO_ELEMENT.get(dm[0] if dm else "", "土")
    hd = chart.get("humandesign", {})
    hd_type = hd.get("energy_type", "")
    
    is_en = lang == "en"
    current_year = year
    
    # Simple annual pillar calculation (simplified)
    year_gan = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"][(current_year - 2020) % 10]
    year_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"][(current_year - 2020) % 12]
    annual_pillar = f"{year_gan}{year_zhi}"
    
    if is_en:
        themes = {
            "金": "Year of Refinement", "木": "Year of Growth", "水": "Year of Flow",
            "火": "Year of Action", "土": "Year of Consolidation"
        }
        return {
            "year_theme": themes.get(element, "Year of Discovery"),
            "yearly_overview": f"{current_year} brings the {annual_pillar} annual pillar. For your {dm} Day Master ({element}), this year invites you to {'focus on structure and boundaries' if element == '金' else 'expand and take risks' if element == '木' else 'go with the flow and trust intuition' if element == '水' else 'take bold action and lead' if element == '火' else 'build solid foundations'}. As a {hd_type}, your strategy this year is to {'respond to what excites you' if hd_type in ['生產者', '顯示生產者'] else 'wait for the right invitations' if hd_type == '投射者' else 'initiate and inform' if hd_type == '顯示者' else 'observe the full lunar cycle before deciding'}. (Set OPENAI_API_KEY for deeper analysis)",
            "bazi_luck": {
                "annual_pillar": annual_pillar,
                "luck_direction": f"The {element} element interacts with this year's energy",
                "element_balance": f"Focus on balancing {element} with its complementary elements"
            },
            "key_opportunities": [
                "Learning and skill development",
                "Building meaningful connections",
                "Exploring new directions aligned with your design"
            ],
            "key_challenges": [
                "Resisting external pressure to move faster than your natural pace",
                "Overcommitting due to excitement",
                "Neglecting rest and recovery"
            ],
            "monthly_insights": [
                {"month": i, "theme": f"Month {i} focus", "advice": "Tune into your body's signals", "energy": "medium"}
                for i in range(1, 13)
            ],
            "annual_prescription": [
                {"icon": "🌱", "title": "Plant Seeds in Q1", "description": "Use the first quarter to set intentions aligned with your inner authority"},
                {"icon": "⚡", "title": "Build Momentum in Q2", "description": "Take action on what genuinely excites your sacral or your design"},
                {"icon": "🛡️", "title": "Consolidate in Q4", "description": "Review the year and protect your energy as you prepare for the next cycle"}
            ]
        }
    
    themes = {
        "金": "精煉之年", "木": "成長之年", "水": "流動之年",
        "火": "行動之年", "土": "扎根之年"
    }
    return {
        "year_theme": themes.get(element, "探索之年"),
        "yearly_overview": f"{current_year}年迎來{annual_pillar}流年。對於{dm}日主（五行{element}）的你來說，這一年邀請你{'專注於結構與邊界' if element == '金' else '拓展與冒險' if element == '木' else '順流而下、信任直覺' if element == '水' else '大膽行動、展現領導力' if element == '火' else '建立穩固基礎'}。以你的人類圖類型{hd_type}來說，今年的策略是{'回應讓你興奮的事物' if hd_type in ['生產者', '顯示生產者'] else '等待正確的邀請' if hd_type == '投射者' else '主動發起並告知' if hd_type == '顯示者' else '觀察完整月週期再做決定'}。（設定 OPENAI_API_KEY 以啟用更深入的分析）",
        "bazi_luck": {
            "annual_pillar": annual_pillar,
            "luck_direction": f"{element}元素與今年流年能量的互動",
            "element_balance": f"專注於平衡{element}與其互補元素"
        },
        "key_opportunities": [
            "學習與技能發展",
            "建立有意義的連結",
            "探索與你設計一致的新方向"
        ],
        "key_challenges": [
            "抗拒外在壓力、不被迫加快速度",
            "因興奮而過度承諾",
            "忽略休息與恢復"
        ],
        "monthly_insights": [
            {"month": i, "theme": f"第{i}月重點", "advice": "聆聽身體的訊號", "energy": "medium"}
            for i in range(1, 13)
        ],
        "annual_prescription": [
            {"icon": "🌱", "title": "第一季播種", "description": "利用第一季度設定與內在權威一致的意圖"},
            {"icon": "⚡", "title": "第二季累積動能", "description": "對真正激發你薦骨或設計的事物採取行動"},
            {"icon": "🛡️", "title": "第四季鞏固", "description": "回顧這一年，保護你的能量，為下一個週期做準備"}
        ]
    }


async def generate_annual_report(chart: Dict[str, Any], year: int, lang: str = "zh-TW", tier: str = "standard") -> Dict[str, Any]:
    """Generate AI-powered annual destiny report"""
    ap = ANNUAL_PROMPTS.get(lang, ANNUAL_PROMPTS["zh-TW"])
    
    if not client or not settings.OPENAI_API_KEY:
        return _build_annual_fallback(chart, year, lang)
    
    chart_text = _serialize_chart(chart)
    
    is_zh = lang.startswith("zh")
    if tier == "lite":
        length_hint = "請精簡輸出：yearly_overview 150字，monthly_insights 只給重點月份。" if is_zh else "Keep it concise."
        max_tokens = 1000
    elif tier == "premium":
        length_hint = "請深度輸出：yearly_overview 400字，每個月都要有具體主題和建議，annual_prescription 5條。" if is_zh else "Go deep with month-by-month specifics."
        max_tokens = 3000
    else:
        length_hint = "請平衡深度與長度，12個月都要涵蓋。" if is_zh else "Balanced depth, cover all 12 months."
        max_tokens = 2000
    
    prompt = f"""目標年份：{year}

命盤資料：
{chart_text}

{ap['schema']}

{length_hint}"""
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": ap["system"]},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=max_tokens
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    result["_ai_metadata"] = {
        "model": response.model,
        "tier": tier,
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0
    }
    return result
