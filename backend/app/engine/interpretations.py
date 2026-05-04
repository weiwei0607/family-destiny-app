"""Rule-based chart interpretations (free tier)

Provides human-readable descriptions for each of the 5 systems.
Zero cost — pure code, no AI.
"""

# ---------- Bazi Interpretations ----------

_DAY_MASTER_TRAITS = {
    "甲": {
        "zh-TW": "甲木日主——像一棵大樹，天生有領導氣質，做事有原則、有遠見。",
        "zh-CN": "甲木日主——像一棵大树，天生有领导气质，做事有原则、有远见。",
        "en": "Wood Day Master — like a tall tree. Natural leadership, principled, visionary."
    },
    "乙": {
        "zh-TW": "乙木日主——像藤蔓，柔軟卻韌性極強，擅長適應環境、察言觀色。",
        "zh-CN": "乙木日主——像藤蔓，柔软却韧性极强，擅长适应环境、察言观色。",
        "en": "Yin Wood Day Master — like a vine. Flexible yet resilient, adapts well."
    },
    "丙": {
        "zh-TW": "丙火日主——像太陽，熱情、明亮、天生有感染力。",
        "zh-CN": "丙火日主——像太阳，热情、明亮、天生有感染力。",
        "en": "Fire Day Master — like the sun. Warm, bright, naturally uplifting."
    },
    "丁": {
        "zh-TW": "丁火日主——像燭光，細膩、專注、有深度，洞察力極強。",
        "zh-CN": "丁火日主——像烛光，细腻、专注、有深度，洞察力极强。",
        "en": "Yin Fire Day Master — like candlelight. Subtle, focused, deep insight."
    },
    "戊": {
        "zh-TW": "戊土日主——像大地，穩重、包容、值得信賴。",
        "zh-CN": "戊土日主——像大地，稳重、包容、值得信赖。",
        "en": "Earth Day Master — like the ground. Steady, reliable, trustworthy."
    },
    "己": {
        "zh-TW": "己土日主——像田園土壤，細心、耐心、善於孕育。",
        "zh-CN": "己土日主——像田园土壤，细心、耐心、善于孕育。",
        "en": "Yin Earth Day Master — like garden soil. Careful, patient, nurturing."
    },
    "庚": {
        "zh-TW": "庚金日主——像寶劍，果斷、正直、有原則。",
        "zh-CN": "庚金日主——像宝剑，果断、正直、有原则。",
        "en": "Metal Day Master — like a sword. Decisive, upright, principled."
    },
    "辛": {
        "zh-TW": "辛金日主——像珠寶，精緻、敏銳、有品味。",
        "zh-CN": "辛金日主——像珠宝，精致、敏锐、有品味。",
        "en": "Yin Metal Day Master — like jewelry. Refined, sharp, tasteful."
    },
    "壬": {
        "zh-TW": "壬水日主——像大海，聰明、變化多端、適應力極強。",
        "zh-CN": "壬水日主——像大海，聪明、变化多端、适应力极强。",
        "en": "Water Day Master — like the ocean. Intelligent, adaptable, ever-changing."
    },
    "癸": {
        "zh-TW": "癸水日主——像雨露，細膩、直覺強、有靈性。",
        "zh-CN": "癸水日主——像雨露，细腻、直觉强、有灵性。",
        "en": "Yin Water Day Master — like morning dew. Delicate, intuitive, spiritual."
    }
}

_WUXING_BALANCE = {
    "zh-TW": {
        "金旺": "金氣旺盛，你做事果斷、講原則，但要注意別太過強勢，讓身邊的人感到壓力。",
        "木旺": "木氣旺盛，你有很強的行動力和成長動能，但要避免衝動，給自己沉澱的時間。",
        "水旺": "水氣旺盛，你思維靈活、適應力強，但容易思慮過多，學會適時停止腦內小劇場。",
        "火旺": "火氣旺盛，你熱情洋溢、感染力強，但要避免情緒起伏過大，影響判斷。",
        "土旺": "土氣旺盛，你穩重可靠、值得信賴，但有時會過於固執，學會接受變化。",
        "平衡": "五行相對平衡，你具備多方面的適應能力，能在不同情境中找到自己的位置。",
    },
    "zh-CN": {
        "金旺": "金气旺盛，你做事果断、讲原则，但要注意别太过强势，让身边的人感到压力。",
        "木旺": "木气旺盛，你有很强的行动力和成长动能，但要避免冲动，给自己沉淀的时间。",
        "水旺": "水气旺盛，你思维灵活、适应力强，但容易思虑过多，学会适时停止脑内小剧场。",
        "火旺": "火气旺盛，你热情洋溢、感染力强，但要避免情绪起伏过大，影响判断。",
        "土旺": "土气旺盛，你稳重可靠、值得信赖，但有时会过于固执，学会接受变化。",
        "平衡": "五行相对平衡，你具备多方面的适应能力，能在不同情境中找到自己的位置。",
    },
    "en": {
        "金旺": "Strong Metal — decisive and principled, but don't overpower others.",
        "木旺": "Strong Wood — great drive for growth, but avoid impulsiveness.",
        "水旺": "Strong Water — flexible mind, but stop overthinking.",
        "火旺": "Strong Fire — passionate and infectious, but watch mood swings.",
        "土旺": "Strong Earth — steady and reliable, but don't be too stubborn.",
        "平衡": "Balanced elements — adaptable, can find your place in any situation.",
    }
}

# ---------- Astrology Interpretations ----------

_SUN_SIGN_TRAITS = {
    "zh-TW": {
        "牡羊": "太陽牡羊——行動快、膽子大、討厭拖泥帶水。",
        "金牛": "太陽金牛——重視穩定與質感，值得信賴、有耐心。",
        "雙子": "太陽雙子——好奇、靈活、擅長溝通。",
        "巨蟹": "太陽巨蟹——敏感、念舊、保護欲強。",
        "獅子": "太陽獅子——自信、慷慨、有領導魅力。",
        "處女": "太陽處女——細心、務實、追求完美。",
        "天秤": "太陽天秤——優雅、公平、善於社交。",
        "天蠍": "太陽天蠍——深刻、專注、情感強烈。",
        "射手": "太陽射手——樂觀、自由、熱愛冒險。",
        "摩羯": "太陽摩羯——有紀律、有野心、能吃苦。",
        "水瓶": "太陽水瓶——獨立、有遠見、重視理念。",
        "雙魚": "太陽雙魚——同理心強、直覺敏銳、有藝術天賦。",
    },
    "zh-CN": {
        "牡羊": "太阳牡羊——行动快、胆子大、讨厌拖泥带水。",
        "金牛": "太阳金牛——重视稳定与质感，值得信赖、有耐心。",
        "雙子": "太阳双子——好奇、灵活、擅长沟通。",
        "巨蟹": "太阳巨蟹——敏感、念旧、保护欲强。",
        "獅子": "太阳狮子——自信、慷慨、有领导魅力。",
        "處女": "太阳处女——细心、务实、追求完美。",
        "天秤": "太阳天秤——优雅、公平、善于社交。",
        "天蠍": "太阳天蝎——深刻、专注、情感强烈。",
        "射手": "太阳射手——乐观、自由、热爱冒险。",
        "摩羯": "太阳摩羯——有纪律、有野心、能吃苦。",
        "水瓶": "太阳水瓶——独立、有远见、重视理念。",
        "雙魚": "太阳双鱼——同理心强、直觉敏锐、有艺术天赋。",
    },
    "en": {
        "牡羊": "Sun Aries — fast, bold, hates delays.",
        "金牛": "Sun Taurus — values stability, reliable, patient.",
        "雙子": "Sun Gemini — curious, flexible, communicative.",
        "巨蟹": "Sun Cancer — sensitive, nostalgic, protective.",
        "獅子": "Sun Leo — confident, generous, charismatic.",
        "處女": "Sun Virgo — detail-oriented, practical, perfection-seeking.",
        "天秤": "Sun Libra — elegant, fair, harmony-seeking.",
        "天蠍": "Sun Scorpio — deep, focused, emotionally intense.",
        "射手": "Sun Sagittarius — optimistic, freedom-loving, adventurous.",
        "摩羯": "Sun Capricorn — disciplined, ambitious, resilient.",
        "水瓶": "Sun Aquarius — independent, visionary, idealistic.",
        "雙魚": "Sun Pisces — empathetic, intuitive, artistic.",
    }
}

_MOON_SIGN_NOTE = {
    "zh-TW": "月亮星座代表你的內在需求和情緒反應模式。",
    "zh-CN": "月亮星座代表你的内在需求和情绪反应模式。",
    "en": "Your Moon sign represents your inner needs and emotional response patterns.",
}

# ---------- Human Design Interpretations ----------

_HD_TYPE_TRAITS = {
    "zh-TW": {
        "顯示者": {
            "trait": "顯示者——天生有發起和創造的能力。",
            "strategy": "",
            "authority_note": ""
        },
        "生產者": {
            "trait": "生產者——天生有持續建造的能量。",
            "strategy": "",
            "authority_note": ""
        },
        "顯示生產者": {
            "trait": "顯示生產者——同時擁有行動力和建造力。",
            "strategy": "",
            "authority_note": ""
        },
        "投射者": {
            "trait": "投射者——天生有洞察和引導的天賦。",
            "strategy": "",
            "authority_note": ""
        },
        "反映者": {
            "trait": "反映者——佔人口不到 1%，像鏡子反映環境真實狀態。",
            "strategy": "",
            "authority_note": ""
        },
    },
    "zh-CN": {
        "顯示者": {
            "trait": "显示者——天生有发起和创造的能力。",
            "strategy": "",
            "authority_note": ""
        },
        "生產者": {
            "trait": "生产者——天生有持续建造的能量。",
            "strategy": "",
            "authority_note": ""
        },
        "顯示生產者": {
            "trait": "显示生产者——同时拥有行动力和建造力。",
            "strategy": "",
            "authority_note": ""
        },
        "投射者": {
            "trait": "投射者——天生有洞察和引导的天赋。",
            "strategy": "",
            "authority_note": ""
        },
        "反映者": {
            "trait": "反映者——占人口不到 1%，像镜子反映环境真实状态。",
            "strategy": "",
            "authority_note": ""
        },
    },
    "en": {
        "Manifestor": {
            "trait": "Manifestor — born to initiate and create.",
            "strategy": "",
            "authority_note": ""
        },
        "Generator": {
            "trait": "Generator — born to build continuously.",
            "strategy": "",
            "authority_note": ""
        },
        "Manifesting Generator": {
            "trait": "Manifesting Generator — speed + building power combined.",
            "strategy": "",
            "authority_note": ""
        },
        "Projector": {
            "trait": "Projector — born to see and guide.",
            "strategy": "",
            "authority_note": ""
        },
        "Reflector": {
            "trait": "Reflector — less than 1% of population. A mirror of the environment.",
            "strategy": "",
            "authority_note": ""
        },
    }
}

_HD_AUTHORITY_NOTE = {
    "zh-TW": {
        "情緒中心": "情緒中心權威——決定需要時間，等平靜時的聲音。",
        "薦骨": "薦骨權威——身體知道答案，注意『嗯嗯』的回應。",
        "直覺": "直覺權威——第一瞬間知道真相。",
        "意志力": "意志力權威——你想做什麼，就去做。",
        "自我投射": "自我投射權威——說出來，聽自己怎麼說。",
        "月周期": "月周期權威——重大決定給自己28天。",
        "無內在權威": "無內在權威——決定需要和信任的人討論。",
    },
    "zh-CN": {
        "情緒中心": "情绪中心权威——决定需要时间，等平静时的声音。",
        "薦骨": "荐骨权威——身体知道答案，注意『嗯嗯』的回应。",
        "直覺": "直觉权威——第一瞬间知道真相。",
        "意志力": "意志力权威——你想做什么，就去做。",
        "自我投射": "自我投射权威——说出来，听自己怎么说。",
        "月周期": "月周期权威——重大决定给自己28天。",
        "無內在權威": "无内在权威——决定需要和信任的人讨论。",
    },
    "en": {
        "情緒中心": "Emotional Authority — decisions need time. Wait for calm.",
        "薦骨": "Sacral Authority — your body knows the answer.",
        "直覺": "Splenic Authority — first instant knows the truth.",
        "意志力": "Ego Authority — you want it, go for it.",
        "自我投射": "Self-Projected Authority — speak it out, listen to your tone.",
        "月周期": "Lunar Cycle Authority — major decisions need 28 days.",
        "無內在權威": "No Inner Authority — discuss with trusted people.",
    }
}

# ---------- Ziwei Interpretations ----------

_ZIWEI_PALACE_MEANING = {
    "zh-TW": {
        "命宮": "命宮代表你這一生的核心特質、先天性格和命運主軸。",
        "身宮": "身宮代表你後天發展的方向、中年後的重心和實際作為。",
        "夫妻宮": "夫妻宮反映你的感情模式、擇偶標準和親密關係的課題。",
        "財帛宮": "財帛宮顯示你的金錢觀、賺錢方式和財運起伏。",
        "官祿宮": "官祿宮揭示你的事業傾向、工作態度和社會成就的領域。",
    },
    "zh-CN": {
        "命宮": "命宫代表你这一生的核心特质、先天性格和命运主轴。",
        "身宮": "身宫代表你后天发展的方向、中年后的重心和实际作为。",
        "夫妻宮": "夫妻宫反映你的感情模式、择偶标准和亲密关系的课题。",
        "財帛宮": "财帛宫显示你的金钱观、赚钱方式和财运起伏。",
        "官祿宮": "官禄宫揭示你的事业倾向、工作态度和社会成就的领域。",
    },
    "en": {
        "命宮": "Life Palace represents your core traits, innate personality, and destiny axis.",
        "身宮": "Body Palace represents your postnatal development direction and midlife focus.",
        "夫妻宮": "Spouse Palace reflects your relationship patterns and intimacy lessons.",
        "財帛宮": "Wealth Palace shows your money mindset and earning style.",
        "官祿宮": "Career Palace reveals your professional tendencies and social achievement areas.",
    }
}

_ZIWEI_MAIN_STAR_TRAITS = {
    "zh-TW": {
        "紫微": "紫微坐命——天生有領導氣場。",
        "天機": "天機坐命——聰明機靈、反應快。",
        "太陽": "太陽坐命——熱心、光明磊落。",
        "武曲": "武曲坐命——務實、果斷。",
        "天同": "天同坐命——溫和、樂天。",
        "廉貞": "廉貞坐命——感情豐富、追求完美。",
        "天府": "天府坐命——穩重、善於管理。",
        "太陰": "太陰坐命——溫柔、細膩。",
        "貪狼": "貪狼星坐命，多才多藝、欲望強、魅力十足。你對生活充滿好奇，但要學會專注，貪多嚼不爛。",
        "巨門": "巨門坐命——口才好、觀察力強。",
        "天相": "天相坐命——重視形象、善於協調。",
        "天梁": "天梁坐命——成熟、有正義感。",
        "七殺": "七殺坐命——果斷、有衝勁。",
        "破軍": "破軍坐命——創新、敢破敢立。",
    },
    "zh-CN": {
        "紫微": "紫微坐命——天生有领导气场。",
        "天機": "天机坐命——聪明机灵、反应快。",
        "太陽": "太阳坐命——热心、光明磊落。",
        "武曲": "武曲坐命——务实、果断。",
        "天同": "天同坐命——温和、乐天。",
        "廉貞": "廉贞坐命——感情丰富、追求完美。",
        "天府": "天府坐命——稳重、善于管理。",
        "太陰": "太阴坐命——温柔、细腻。",
        "貪狼": "贪狼坐命——多才多艺、魅力十足。",
        "巨門": "巨门坐命——口才好、观察力强。",
        "天相": "天相坐命——重视形象、善于协调。",
        "天梁": "天梁坐命——成熟、有正义感。",
        "七殺": "七杀坐命——果断、有冲劲。",
        "破軍": "破军坐命——创新、敢破敢立。",
    },
    "en": {
        "紫微": "Zi Wei — natural leadership aura.",
        "天機": "Tian Ji — clever, quick-thinking, strategic.",
        "太陽": "Tai Yang — warm, upright, nurturing.",
        "武曲": "Wu Qu — practical, decisive, results-driven.",
        "天同": "Tian Tong — gentle, optimistic, blessed.",
        "廉貞": "Lian Zhen — emotional, principled, perfectionist.",
        "天府": "Tian Fu — steady, inclusive, managerial.",
        "太陰": "Tai Yin — gentle, delicate, artistic.",
        "貪狼": "Tan Lang — versatile, desirous, charismatic.",
        "巨門": "Ju Men — eloquent, observant, truth-seeking.",
        "天相": "Tian Xiang — image-conscious, service-oriented, diplomatic.",
        "天梁": "Tian Liang — mature, just, helpful.",
        "七殺": "Qi Sha — decisive, driven, fearless.",
        "破軍": "Po Jun — innovative, disruptive, freedom-loving.",
    }
}

# ---------- Xingxiu Interpretations ----------

_XINGXIU_TRAITS = {
    "zh-TW": {
        "角": "角宿的人外表柔和、內心堅定，有藝術天賦。你在人際中善於化解衝突，但容易為了和諧壓抑真實感受。",
        "亢": "亢宿的人正直、有原則、追求完美。你對自己要求高，但過度自我批評會讓你錯過當下的美好。",
        "氐": "氐宿的人務實、有責任感、重視家庭。你是可靠的支柱，但承擔太多會讓你忘記自己的需要。",
        "房": "房宿的人優雅、有魅力、善於社交。你天生吸引人，但要分辨誰是真正值得信任的人。",
        "心": "心宿的人熱情、敏感、情感豐富。你的直覺極強，但情緒的波動會影響你的判斷，學會觀察而非立即反應。",
        "尾": "尾宿的人直率、有行動力、不喜歡拐彎抹角。你說話直接，但這份真誠是難得的禮物，只是要注意場合。",
        "箕": "箕宿的人開朗、樂觀、善於傳播歡樂。你是派對的靈魂，但內心深處可能有不被理解的孤獨。",
        "斗": "斗宿的人沉穩、有毅力、目標導向。你像老樹一樣可靠，但偶爾也要允許自己搖曳，不是每刻都要站穩。",
        "牛": "牛宿的人勤奮、踏實、重視物質安全感。你一步一腳印，但不要讓對安全的執著限制了你的可能性。",
        "女": "女宿的人獨立、有才華、追求自我實現。你有很強的個人風格，但在關係中學會柔軟不是妥協，是智慧。",
        "虛": "虛宿的人理想主義、有靈性、富想像力。你活在現實與夢想的交界，記得偶爾把腳踩回地面。",
        "危": "危宿的人聰明、有危機意識、善於避險。你的警覺保護了你很多次，但過度防備會讓你錯過風景。",
        "室": "室宿的人穩重、有建設力、喜歡打造舒適環境。你是空間的魔法師，但走出去看看，世界比你想像的大。",
        "壁": "壁宿的人內向、有深度、重視隱私。你有堅強的內在堡壘，但讓信任的人進來，你不會因此變得脆弱。",
        "奎": "奎宿的人有學問、愛學習、追求智慧。你是終身學習者，但知識要轉化為行動才有意義。",
        "婁": "婁宿的人忠誠、重承諾、有團隊精神。你說到做到，但學會重新協商不是失信，是成熟。",
        "胃": "胃宿的人務實、有組織力、重視效率。你擅長把混沌變有序，但生命有些混亂是不需要整理的。",
        "昴": "昴宿的人注重美感、有品味、追求精緻。你對細節的敏感是才華，但完美主義可能讓你遲遲無法完成。",
        "畢": "畢宿的人有毅力、能吃苦、目標導向。你像竹子一樣韌性十足，但別忘了欣賞沿途的風景。",
        "觜": "觜宿的人機靈、反應快、善於表達。你的口才讓你脫穎而出，但話語的力量在於質量而非數量。",
        "参": "参宿的人勇敢、冒險、不畏挑戰。你天生帶有開拓者的血液，但衝動前記得帶上地圖。",
        "井": "井宿的人博愛、有服務精神、重視公平。你像泉水一樣滋潤他人，但要確認源頭沒有乾涸。",
        "鬼": "鬼宿的人直覺強、有靈性、能看透表象。你的第六感很準，但不要讓疑心病毀了信任。",
        "柳": "柳宿的人有表現力、重視形象、善於社交。你天生適合站在人前，但台下充電和台上發光同等重要。",
        "星": "星宿的人獨立、有創意、追求完美。你有自己的步調，不要被外界的節奏打亂。",
        "張": "張宿的人熱情、有感染力、喜歡連結人。你像網絡的節點，但深度關係比廣度關係更滋養你。",
        "翼": "翼宿的人謹慎、細心、善於規劃。你考慮周全，但過度規劃可能讓你錯過即興的美好。",
        "軫": "軫宿的人善變、適應力強、喜歡移動。你像風一樣自由，但偶爾也需要一個可以回來的地方。",
    },
    "zh-CN": {
        "角": "角宿的人外表柔和、内心坚定，有艺术天赋。你在人际中善于化解冲突，但容易为了和谐压抑真实感受。",
        "亢": "亢宿的人正直、有原则、追求完美。你对自己要求高，但过度自我批评会让你错过当下的美好。",
        "氐": "氐宿的人务实、有责任感、重视家庭。你是可靠的支柱，但承担太多会让你忘记自己的需要。",
        "房": "房宿的人优雅、有魅力、善于社交。你天生吸引人，但要分辨谁是真正值得信任的人。",
        "心": "心宿的人热情、敏感、情感丰富。你的直觉极强，但情绪的波动会影响你的判断，学会观察而非立即反应。",
        "尾": "尾宿的人直率、有行动力、不喜欢拐弯抹角。你说话直接，但这份真诚是难得的礼物，只是要注意场合。",
        "箕": "箕宿的人开朗、乐观、善于传播欢乐。你是派对的灵魂，但内心深处可能有不被理解的孤独。",
        "斗": "斗宿的人沉稳、有毅力、目标导向。你像老树一样可靠，但偶尔也要允许自己摇曳，不是每刻都要站稳。",
        "牛": "牛宿的人勤奋、踏实、重视物质安全感。你一步一脚印，但不要让对安全的执着限制了你的可能性。",
        "女": "女宿的人独立、有才华、追求自我实现。你有很强的个人风格，但在关系中学会柔软不是妥协，是智慧。",
        "虛": "虚宿的人理想主义、有灵性、富想像力。你活在现实与梦想的交界，记得偶尔把脚踩回地面。",
        "危": "危宿的人聪明、有危机意识、善于避险。你的警觉保护了你很多次，但过度防备会让你错过风景。",
        "室": "室宿的人稳重、有建设力、喜欢打造舒适环境。你是空间的魔法师，但走出去看看，世界比你想像的大。",
        "壁": "壁宿的人内向、有深度、重视隐私。你有坚强的内在堡垒，但让信任的人进来，你不会因此变得脆弱。",
        "奎": "奎宿的人有学问、爱学习、追求智慧。你是终身学习者，但知识要转化为行动才有意义。",
        "婁": "娄宿的人忠诚、重承诺、有团队精神。你说到做到，但学会重新协商不是失信，是成熟。",
        "胃": "胃宿的人务实、有组织力、重视效率。你擅长把混沌变有序，但生命有些混乱是不需要整理的。",
        "昴": "昴宿的人注重美感、有品味、追求精致。你对细节的敏感是才华，但完美主义可能让你迟迟无法完成。",
        "畢": "毕宿的人有毅力、能吃苦、目标导向。你像竹子一样韧性十足，但别忘了欣赏沿途的风景。",
        "觜": "觜宿的人机灵、反应快、善于表达。你的口才让你脱颖而出，但话语的力量在于质量而非数量。",
        "参": "参宿的人勇敢、冒险、不畏挑战。你天生带有开拓者的血液，但冲动前记得带上地图。",
        "井": "井宿的人博爱、有服务精神、重视公平。你像泉水一样滋润他人，但要确认源头没有干涸。",
        "鬼": "鬼宿的人直觉强、有灵性、能看透表象。你的第六感很准，但不要让疑心病毁了信任。",
        "柳": "柳宿的人有表现力、重视形象、善于社交。你天生适合站在人前，但台下充电和台上发光同等重要。",
        "星": "星宿的人独立、有创意、追求完美。你有自己的步调，不要被外界的节奏打乱。",
        "張": "张宿的人热情、有感染力、喜欢连结人。你像网络的节点，但深度关系比广度关系更滋养你。",
        "翼": "翼宿的人谨慎、细心、善于规划。你考虑周全，但过度规划可能让你错过即兴的美好。",
        "軫": "轸宿的人善变、适应力强、喜欢移动。你像风一样自由，但偶尔也需要一个可以回来的地方。",
    },
    "en": {
        "角": "Jiao — gentle outside, firm inside, artistic. Good at conflict resolution, but may suppress true feelings for harmony.",
        "亢": "Kang — upright, principled, perfectionist. High self-expectations; don't let self-criticism steal the present.",
        "氐": "Di — practical, responsible, family-oriented. A reliable pillar, but don't forget your own needs.",
        "房": "Fang — elegant, charming, social. Naturally attractive, but discern who is truly trustworthy.",
        "心": "Xin — passionate, sensitive, intuitive. Strong gut feelings, but emotions affect judgment. Observe before reacting.",
        "尾": "Wei — direct, action-oriented, straightforward. Your honesty is a gift, but mind the occasion.",
        "箕": "Ji — cheerful, optimistic, joy-spreader. The soul of the party, but may feel misunderstood deep down.",
        "斗": "Dou — steady, persistent, goal-oriented. Reliable as an old tree, but allow yourself to sway sometimes.",
        "牛": "Niu — hardworking, grounded, security-minded. Step by step, but don't let safety obsession limit possibilities.",
        "女": "Nyu — independent, talented, self-actualizing. Strong personal style; softness in relationships is wisdom, not compromise.",
        "虛": "Xu — idealistic, spiritual, imaginative. Living between reality and dreams; occasionally plant your feet on the ground.",
        "危": "Wei — smart, risk-aware, good at avoiding danger. Your alertness has saved you, but excessive defense makes you miss the view.",
        "室": "Shi — steady, constructive, comfort-creating. A space magician, but go out — the world is bigger than you think.",
        "壁": "Bi — introverted, deep, privacy-valuing. You have strong inner walls, but letting trusted people in doesn't make you weak.",
        "奎": "Kui — learned, curious, wisdom-seeking. A lifelong learner, but knowledge only matters when turned into action.",
        "婁": "Lou — loyal, committed, team-oriented. You keep promises, but renegotiating is maturity, not betrayal.",
        "胃": "Wei — practical, organized, efficiency-focused. Good at ordering chaos, but some mess doesn't need tidying.",
        "昴": "Mao — aesthetic, tasteful, refined. Detail sensitivity is talent, but perfectionism may delay completion.",
        "畢": "Bi — persistent, resilient, goal-driven. Flexible as bamboo, but don't forget to enjoy the scenery.",
        "觜": "Zi — clever, quick, expressive. Eloquence makes you stand out, but quality of words matters more than quantity.",
        "参": "Shen — brave, adventurous, fearless. Pioneer blood runs in you, but bring a map before rushing.",
        "井": "Jing — compassionate, service-oriented, fair. You nourish others like a spring, but ensure your source doesn't dry up.",
        "鬼": "Gui — intuitive, spiritual, sees through illusions. Your sixth sense is accurate, but don't let paranoia destroy trust.",
        "柳": "Liu — expressive, image-conscious, social. Born for the spotlight, but recharging offline is equally important.",
        "星": "Xing — independent, creative, perfectionist. You have your own rhythm; don't let the world dictate your pace.",
        "張": "Zhang — warm, infectious, connector. A network node, but depth nourishes more than breadth.",
        "翼": "Yi — cautious, careful, planner. Thorough thinking is strength, but over-planning may miss spontaneous beauty.",
        "軫": "Zhen — adaptable, changeable, mobile. Free as the wind, but occasionally you need a place to return.",
    }
}


# Element mapping (duplicate from ai_service for standalone use)
_GAN_TO_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# ---------- Interpretation Builder ----------

def interpret_bazi(bazi: dict, lang: str = "zh-TW") -> dict:
    """Generate human-readable bazi interpretation"""
    day_master = bazi.get("day_master", "")
    dm_gan = day_master[0] if day_master else ""
    
    # Count elements in pillars
    elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for pillar in [bazi.get("year", ""), bazi.get("month", ""), bazi.get("day", ""), bazi.get("hour", "")]:
        if len(pillar) >= 1:
            gan = pillar[0]
            e = _GAN_TO_ELEMENT.get(gan, "")
            if e:
                elements[e] += 1
    
    # Find dominant element
    max_count = max(elements.values()) if elements else 0
    dominant = [k for k, v in elements.items() if v == max_count and v > 0]
    
    is_en = lang == "en"
    wuxing_key = f"{dominant[0]}旺" if dominant else "平衡"
    
    return {
        "day_master_trait": _DAY_MASTER_TRAITS.get(dm_gan, {}).get(lang, _DAY_MASTER_TRAITS.get(dm_gan, {}).get("zh-TW", "")),
        "element_balance": _WUXING_BALANCE.get(lang, _WUXING_BALANCE["zh-TW"]).get(wuxing_key, _WUXING_BALANCE["zh-TW"]["平衡"]),
        "dominant_element": dominant[0] if dominant else "",
    }


def interpret_astrology(astro: dict, lang: str = "zh-TW") -> dict:
    """Generate human-readable astrology interpretation"""
    sun = astro.get("太陽", {})
    moon = astro.get("月亮", {})
    sun_sign = sun.get("sign", "") if isinstance(sun, dict) else ""
    moon_sign = moon.get("sign", "") if isinstance(moon, dict) else ""
    
    sun_trait = _SUN_SIGN_TRAITS.get(lang, _SUN_SIGN_TRAITS["zh-TW"]).get(sun_sign, "")
    moon_note = _MOON_SIGN_NOTE.get(lang, _MOON_SIGN_NOTE["zh-TW"])
    moon_trait = _SUN_SIGN_TRAITS.get(lang, _SUN_SIGN_TRAITS["zh-TW"]).get(moon_sign, "")
    
    return {
        "sun_sign_trait": sun_trait,
        "moon_sign_note": moon_note,
        "moon_sign_trait": moon_trait,
    }


def interpret_humandesign(hd: dict, lang: str = "zh-TW") -> dict:
    """Generate human-readable human design interpretation"""
    hd_type = hd.get("energy_type", "")
    authority = hd.get("authority", "")
    profile = hd.get("profile", "")
    
    type_data = _HD_TYPE_TRAITS.get(lang, _HD_TYPE_TRAITS["zh-TW"]).get(hd_type, {})
    authority_note = _HD_AUTHORITY_NOTE.get(lang, _HD_AUTHORITY_NOTE["zh-TW"]).get(authority, "")
    
    return {
        "type_trait": type_data.get("trait", ""),
        "strategy": type_data.get("strategy", ""),
        "authority_note": authority_note,
        "profile": profile,
    }


def interpret_ziwei(ziwei: dict, lang: str = "zh-TW") -> dict:
    """Generate human-readable ziwei interpretation"""
    life_palace = ziwei.get("命宮", "")
    body_palace = ziwei.get("身宮", "")
    main_stars = ziwei.get("主星", {})
    
    # Find the main star in life palace
    life_star_trait = ""
    for star_name in _ZIWEI_MAIN_STAR_TRAITS.get(lang, _ZIWEI_MAIN_STAR_TRAITS["zh-TW"]):
        if star_name in str(main_stars) or star_name in life_palace:
            life_star_trait = _ZIWEI_MAIN_STAR_TRAITS[lang].get(star_name, "")
            if not life_star_trait and lang != "zh-TW":
                life_star_trait = _ZIWEI_MAIN_STAR_TRAITS["zh-TW"].get(star_name, "")
            break
    
    # If no specific star found, try to extract from life_palace string
    if not life_star_trait and life_palace:
        for star_name in _ZIWEI_MAIN_STAR_TRAITS.get("zh-TW", {}):
            if star_name in life_palace:
                life_star_trait = _ZIWEI_MAIN_STAR_TRAITS.get(lang, _ZIWEI_MAIN_STAR_TRAITS["zh-TW"]).get(star_name, "")
                break
    
    palace_meaning = _ZIWEI_PALACE_MEANING.get(lang, _ZIWEI_PALACE_MEANING["zh-TW"]).get("命宮", "")
    
    return {
        "life_palace": life_palace,
        "body_palace": body_palace,
        "palace_meaning": palace_meaning,
        "main_star_trait": life_star_trait or palace_meaning,
    }


def interpret_xingxiu(xingxiu_name: str, lang: str = "zh-TW") -> dict:
    """Generate human-readable xingxiu interpretation"""
    xiu_char = xingxiu_name[0] if xingxiu_name else ""
    trait = _XINGXIU_TRAITS.get(lang, _XINGXIU_TRAITS["zh-TW"]).get(xiu_char, "")
    
    return {
        "xingxiu_name": xingxiu_name,
        "trait": trait,
    }


def build_free_interpretations(chart: dict, lang: str = "zh-TW") -> dict:
    """Build all free-tier interpretations from a chart"""
    return {
        "bazi": interpret_bazi(chart.get("bazi", {}), lang),
        "astrology": interpret_astrology(chart.get("astrology", {}), lang),
        "humandesign": interpret_humandesign(chart.get("humandesign", {}), lang),
        "ziwei": interpret_ziwei(chart.get("ziwei", {}), lang),
        "xingxiu": interpret_xingxiu(chart.get("xingxiu", ""), lang),
    }
