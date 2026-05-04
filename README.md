# 🔮 Family Destiny — 家族命盤分析系統

> 融合東西方五大命理系統，生成個人化命盤與關係分析

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask" />
  <img src="https://img.shields.io/badge/NASA%20JPL-Skyfield-0B3D91?logo=nasa" />
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" />
</p>

<p align="center">
  <b>不是迷信，是「用數據理解傳統文化」</b><br/>
  八字 + 西洋占星 + 紫微斗數 + 人類圖 + 星宿，五系統整合分析
</p>

---

## ✨ 五大命理系統

| 系統 | 核心內容 | 技術實現 |
|------|---------|---------|
| **八字 (Bazi)** | 年柱、月柱、日柱、時柱、五行分析 | 天干地支算法 + 節氣判斷 |
| **西洋占星** | 太陽星座、行星位置、宮位 | NASA JPL de421.bsp 星曆表 + Skyfield |
| **紫微斗數** | 命宮、身宮、主星、輔星、四化 | 農曆轉換 + 紫微排盤算法 |
| **人類圖 (Human Design)** | 能量類型、權威、策略、閘門、通道 | 天文計算 Personality/Design 雙層 |
| **星宿** | 二十八星宿歸屬 | 農曆日對照表 |

### 🧠 整合畫像引擎

五系統資料匯入 `integrator.py`，生成統一的人格畫像：
- 能量分數計算
- 優勢與挑戰摘要
- 關係相容性分析

---

## 🛠️ 技術棧

| 層 | 技術 |
|----|------|
| **後端框架** | Flask |
| **天文計算** | Skyfield (NASA JPL ephemeris) |
| **農曆轉換** | 自製農曆查詢表 (lunar_table.json) |
| **資料庫** | SQLite |
| **前端** | Flask Jinja2 Templates |
| **行動版** | Flutter (mobile/ 目錄) |

---

## 🚀 快速開始

### 後端

```bash
cd family-destiny-app
pip install -r requirements.txt

# 首次執行會自動下載 ~17MB 的 de421.bsp 星曆表
python app.py
```

開啟瀏覽器訪問 `http://localhost:5000`

### 行動版 (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

---

## 📁 專案結構

```
family-destiny-app/
├── app.py                  # Flask 主應用
├── bazi_calculator.py      # 八字計算器
├── chart_calculator.py     # 出生圖計算（占星 + 八字雙系統）
├── engine/
│   ├── core.py             # 核心計算邏輯
│   ├── ziwei.py            # 紫微斗數
│   ├── humandesign.py      # 人類圖
│   ├── xingxiu.py          # 星宿
│   ├── lunar_lookup.py     # 農曆查詢
│   └── integrator.py       # 整合畫像引擎
├── backend/                # API 與資料層
├── mobile/                 # Flutter 行動版
├── templates/              # HTML 模板
├── skyfield_data/          # 天文資料（自動生成）
├── de421.bsp               # NASA JPL 星曆表
└── lunar_table.json        # 農曆對照表
```

---

## 🗺️ 產品路線圖

- [x] **核心五系統計算**
- [x] **整合畫像引擎**
- [x] **關係矩陣分析**
- [x] **家族組織圖生成**
- [ ] **AI 解盤助手** — 用 LLM 生成自然語言解讀
- [ ] **運勢預測** — 大運、流年推算
- [ ] **多人比對** — 情侶/合夥人相容性深度分析

---

## 📝 License

MIT License © 2026
