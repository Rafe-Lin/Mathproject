# 自適應複習模式 (Adaptive Review Mode)

## 📖 概述

**自適應複習模式**是一個基於 **RL (強化學習) + AKT (知識追蹤)** 的智能題目推薦系統，用於為學生生成個性化複習方案。

### 核心特性

- ✅ **知識狀態推論**：使用 AKT 模型實時評估學生的掌握度
- ✅ **RL 題目推薦**：基於 PPO 算法的智能題目選擇
- ✅ **多模態分析**：技能掌握度、弱項診斷、學習建議
- ✅ **多會話規劃**：自動生成完整複習計畫
- ✅ **REST API**：易於集成到現有應用

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                    自適應複習系統                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────┐                 │
│  │ 學生歷史輸入 │ ───→ │ AKT 推論層  │                 │
│  │              │      │ (知識狀態)   │                 │
│  └──────────────┘      └──────┬───────┘                 │
│                                │                         │
│                        ┌───────▼────────┐               │
│                        │ 知識狀態 sₜ     │               │
│                        │ APR = 平均掌握度│               │
│                        └───────┬────────┘                │
│                                │                         │
│  ┌──────────────┐      ┌───────▼────────┐   ┌────────┐ │
│  │ RL 推薦引擎  │ ◄────┤ PPO 策略網絡  │───┤ 最優  │ │
│  │ (題目選擇)   │      │ (決策邏輯)    │   │題目ID │ │
│  └──────┬───────┘      └──────────────┘   └────────┘ │
│         │                                              │
│  ┌──────▼────────────────────────────────────────────┐│
│  │ 推薦結果                                           ││
│  │ • Item ID (題目編號)                               ││
│  │ • Skill ID (技能類別)                              ││
│  │ • Predicted Difficulty (預測難度)                 ││
│  │ • Skill Name (技能名稱)                            ││
│  └─────────────────────────────────────────────────┘│
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 數據流向

```
Session Flow:
1. 輸入學生歷史
2. AKT 推論知識狀態
3. 計算 APR (掌握度)
4. RL 推薦題目
5. 學生作答
6. 更新知識狀態
7. 重複步驟 3-6
8. 生成複習報告
```

---

## 📦 文件結構

```
adaptive_review_mode.py          # 核心引擎（無外部依賴）
├─ AdaptiveReviewEngine          # 主類
│  ├─ get_knowledge_state()      # 推論知識狀態
│  ├─ get_apr()                  # 計算 APR
│  ├─ recommend_next_items()     # 推薦題目
│  ├─ simulate_session()         # 模擬會話
│  └─ _load_item_properties()    # 載入題目屬性
├─ analyze_weak_skills()         # 弱項分析
└─ generate_review_plan()        # 計畫生成

adaptive_review_api.py           # Flask API 層
├─ /api/adaptive-review/start    # 開始複習
├─ /api/adaptive-review/analyze  # 分析弱項
├─ /api/adaptive-review/feedback # 提交反饋
├─ /api/adaptive-review/plan     # 生成計畫
└─ /api/adaptive-review/health   # 健康檢查

adaptive_review_examples.py      # 使用示例
├─ example_local_usage()         # 本地使用
├─ example_api_usage()           # API 使用
└─ AdaptiveReviewClient          # API 客戶端
```

---

## 🚀 快速開始

### 前置要求

```bash
# 確保已有以下模型文件
models/akt_curriculum.pth              # AKT 知識追蹤模型
models/rl_akt_curriculum/ppo_akt_curriculum.zip  # PPO RL 模型
synthesized_training_data.csv          # 訓練數據（用於載入題目屬性）
```

### 1️⃣ 本地使用（Python）

```python
from adaptive_review_mode import AdaptiveReviewEngine, analyze_weak_skills

# 初始化引擎
engine = AdaptiveReviewEngine()

# 學生學習歷史
history = {
    'item_history': [0, 5, 10, 15, 20],      # 做過的題目 ID
    'skill_history': [0, 1, 2, 3, 4],        # 對應的技能 ID
    'resp_history': [1, 0, 1, 1, 0],         # 答對/答錯 (1/0)
}

# 獲取知識狀態
s_t = engine.get_knowledge_state(
    history['item_history'],
    history['skill_history'],
    history['resp_history']
)

# 計算 APR（平均掌握度）
apr = engine.get_apr(s_t)
print(f"當前 APR: {apr:.4f}")

# 分析弱項
analysis = analyze_weak_skills(engine, 
    history['item_history'],
    history['skill_history'], 
    history['resp_history']
)
print(f"最弱技能: {analysis['weakest_skills'][0]['skill_name']}")

# 推薦下一批題目
recommendations = engine.recommend_next_items(
    history['item_history'],
    history['skill_history'],
    history['resp_history'],
    n_items=5,
    use_rl=True  # 使用 RL 推薦
)

for rec in recommendations:
    print(f"推薦: Item {rec['item_id']} - {rec['skill_name']}")
```

### 2️⃣ 通過 API 使用（REST）

```bash
# 1. 確保應用已註冊 API 藍圖
# 在 app.py 中添加：
from adaptive_review_api import adaptive_review_bp
app.register_blueprint(adaptive_review_bp)

# 2. 啟動應用
python app.py

# 3. 調用 API
curl -X POST http://127.0.0.1:5000/api/adaptive-review/start \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU_001",
    "history": {
      "item_history": [0, 5, 10],
      "skill_history": [0, 1, 2],
      "resp_history": [1, 0, 1]
    },
    "n_recommendations": 5,
    "use_rl": true
  }'
```

### 3️⃣ Python API 客戶端

```python
from adaptive_review_examples import AdaptiveReviewClient

client = AdaptiveReviewClient('http://127.0.0.1:5000')

# 檢查 API 是否在線
assert client.health_check()

# 開始複習
result = client.start_review(
    student_id='STU_001',
    history={
        'item_history': [0, 5, 10],
        'skill_history': [0, 1, 2],
        'resp_history': [1, 0, 1]
    },
    n_recommendations=5
)

# 分析弱項
analysis = client.analyze_student('STU_001', history)
print(analysis['data']['weakest_skills'])

# 提交反饋
feedback = client.submit_feedback(
    'STU_001', 
    history, 
    item_id=42, 
    correct=1
)
print(f"APR 增幅: {feedback['data']['apr_change']:+.4f}")

# 生成複習計畫
plan = client.get_review_plan('STU_001', history, num_sessions=3)
print(f"預期最終 APR: {plan['data']['overall_stats']['apr_final']:.4f}")
```

---

## 📊 API 參考

### 1. POST /api/adaptive-review/start

**開始新的複習會話**

**請求示例：**
```json
{
  "student_id": "STU_001",
  "history": {
    "item_history": [0, 5, 10, 15, 20],
    "skill_history": [0, 1, 2, 3, 4],
    "resp_history": [1, 0, 1, 1, 0]
  },
  "n_recommendations": 5,
  "use_rl": true
}
```

**響應示例：**
```json
{
  "status": "success",
  "data": {
    "student_id": "STU_001",
    "current_apr": 0.6423,
    "apr_target": 0.65,
    "recommendations": [
      {
        "item_id": 42,
        "skill_id": 3,
        "skill_name": "polynomial-operations",
        "predicted_difficulty": 0.45
      },
      ...
    ],
    "session_id": "sess_STU_001_20240115103000",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

---

### 2. GET /api/adaptive-review/analyze/{student_id}

**分析學生的弱項和強項**

**查詢參數：**
- `history_json`: URL 編碼的歷史 JSON

**響應示例：**
```json
{
  "status": "success",
  "data": {
    "student_id": "STU_001",
    "overall_apr": 0.62,
    "target_apr": 0.65,
    "weakest_skills": [
      {
        "skill_id": 5,
        "skill_name": "radical-operations",
        "mastery": 0.35,
        "variance": 0.08,
        "practice_count": 3
      },
      ...
    ],
    "strongest_skills": [
      {
        "skill_id": 1,
        "skill_name": "addition",
        "mastery": 0.85,
        ...
      }
    ],
    "recommendations": [
      "建議加強根式運算",
      "已掌握基本整數運算，可考慮進階內容"
    ]
  }
}
```

---

### 3. POST /api/adaptive-review/feedback

**提交答題反饋**

**請求示例：**
```json
{
  "student_id": "STU_001",
  "history": {...},
  "item_id": 42,
  "correct": 1,
  "time_spent": 45
}
```

**響應示例：**
```json
{
  "status": "success",
  "data": {
    "student_id": "STU_001",
    "item_id": 42,
    "correct": 1,
    "apr_before": 0.6423,
    "apr_after": 0.6580,
    "apr_change": 0.0157,
    "target_apr": 0.65,
    "reached_target": true,
    "next_recommendations": [...],
    "feedback": "🎉 恭喜！已達到目標掌握度 (65.80%)",
    "timestamp": "2024-01-15T10:35:00"
  }
}
```

---

### 4. GET /api/adaptive-review/plan/{student_id}

**生成多會話複習計畫**

**查詢參數：**
- `history_json`: URL 編碼的歷史 JSON
- `num_sessions`: 會話數（預設 3）

**響應示例：**
```json
{
  "status": "success",
  "data": {
    "student_id": "STU_001",
    "num_sessions": 3,
    "overall_stats": {
      "apr_initial": 0.60,
      "apr_final": 0.78,
      "total_items_practiced": 18
    },
    "sessions": [
      {
        "session_name": "複習會話 #1",
        "apr_initial": 0.60,
        "apr_final": 0.68,
        "apr_gain": 0.08,
        "correct_rate": 0.67,
        "skills_practiced": {"polynomial-operations": 3, ...}
      },
      ...
    ]
  }
}
```

---

## 🔧 配置選項

在 `adaptive_review_mode.py` 中修改 `REVIEW_CONFIG`：

```python
REVIEW_CONFIG = {
    'min_session_length': 3,          # 最少出題數
    'max_session_length': 15,         # 最多出題數
    'target_apr_increment': 0.10,     # 目標 APR 增長
    'max_consecutive_failures': 3,    # 連續失敗上限
    'review_diversity_weight': 0.3,   # 多樣性權重
}

# 獎勵函數權重
W_LEARN = 1.0   # 學習增益
W_FRUST = 0.3   # 挫折感懲罰
W_BORED = 0.2   # 無聊感懲罰
W_DIVER = 0.4   # 多樣性獎勵
W_EFFIC = 0.1   # 效率懲罰

# 掌握度閾值
BETA_THRESHOLD = 0.65  # 65% 判定為掌握
```

---

## 📈 工作流程示例

### 場景：學生數學複習

```
Step 1: 初始診斷
┌──────────────────────────────┐
│ 輸入: 過去 10 題的作答記錄    │
│ 輸出: APR = 0.62 (未達標)    │
│ 弱項: 根式運算、多項式因式分解 │
└──────────────────────────────┘

Step 2: 生成複習計畫
┌──────────────────────────────┐
│ 推薦: 7 題補強序列            │
│ 重點: 根式 × 3, 多項式 × 4   │
│ 難度: 逐步遞增                │
└──────────────────────────────┘

Step 3: 動態調整
┌──────────────────────────────┐
│ 根式題 1: ✓ (答對)            │
│ 根式題 2: ✗ (答錯)            │
│ → 調整難度，推薦基礎題        │
│ 多項式題 1: ✓ (答對)          │
│ → APR 提升至 0.68             │
└──────────────────────────────┘

Step 4: 最終評估
┌──────────────────────────────┐
│ 完成 7 題後                   │
│ 最終 APR: 0.75 (✅ 達標)     │
│ 建議: 進階內容或其他技能      │
└──────────────────────────────┘
```

---

## 🧪 測試

```bash
# 運行完整示例
python adaptive_review_examples.py

# 運行特定示例
python adaptive_review_examples.py 1  # 本地使用
python adaptive_review_examples.py 2  # 多會話計畫
python adaptive_review_examples.py 3  # API 使用 (需要 Flask)
```

---

## 🔌 與現有應用的集成

### 在 app.py 中添加：

```python
from flask import Flask
from adaptive_review_api import adaptive_review_bp

app = Flask(__name__)

# ... 其他藍圖 ...

# 註冊自適應複習 API
app.register_blueprint(adaptive_review_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

### 在模板中調用：

```html
<!-- 複習按鈕 -->
<button onclick="startReview()">🎯 開始適性複習</button>

<script>
async function startReview() {
    const history = {
        item_history: [0, 5, 10, 15, 20],
        skill_history: [0, 1, 2, 3, 4],
        resp_history: [1, 0, 1, 1, 0]
    };
    
    const response = await fetch('/api/adaptive-review/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            student_id: 'STU_001',
            history: history,
            n_recommendations: 5
        })
    });
    
    const data = await response.json();
    displayRecommendedQuestions(data.data.recommendations);
}
</script>
```

---

## 📚 資源

### 相關模型
- [AKT 模型 (akt_v2.py)](akt_v2.py) - 知識追蹤
- [AKT 推論 (akt_inference.py)](akt_inference.py) - 知識狀態評估
- [RL 訓練 (train_rl_akt_curriculum.py)](train_rl_akt_curriculum.py) - RL 策略學習

### 參考論文
- Ghosh et al., "Context-Aware Attentive Knowledge Tracing", KDD 2020
- arXiv:2305.04475 - Knowledge Tracing with Attention

---

## 🐛 故障排除

| 問題 | 原因 | 解決方案 |
|------|------|--------|
| `ModuleNotFoundError: No module named 'akt_inference'` | 導入路徑錯誤 | 確保在正確的目錄運行，或設定 PYTHONPATH |
| `FileNotFoundError: akt_curriculum.pth` | 模型文件不存在 | 確保模型文件在 `models/` 目錄 |
| `CUDA out of memory` | GPU 內存不足 | 設定 `DEVICE='cpu'` 使用 CPU |
| API 返回 500 錯誤 | 伺服器異常 | 檢查日誌，確保 Flask 應用已正確註冊 API 藍圖 |

---

## 📝 許可證

MIT License - 詳見 LICENSE 文件

---

## 👥 貢獻

歡迎提交 Issue 和 Pull Request！

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0
