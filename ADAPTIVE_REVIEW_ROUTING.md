<!-- 自適應複習模式 - 功能入口與路由完整說明 -->

# 自適應複習模式 - 功能入口與路由說明

## 📍 功能入口位置

### 1️⃣ Web 介面入口

#### 主應用首頁 → 學生面板 → 複習功能
```
http://localhost:5000/
  ↓ (登錄或訪客模式)
/dashboard (學生面板)
  ↓
新增複習功能選項
```

#### 直接訪問 (API 優先)
- **開始複習會話**：`POST /api/adaptive-review/start`
- **分析弱項**：`GET /api/adaptive-review/analyze/<student_id>`
- **提交答題反饋**：`POST /api/adaptive-review/feedback`
- **生成複習計畫**：`GET /api/adaptive-review/plan/<student_id>`
- **健康檢查**：`GET /api/adaptive-review/health`

---

## 🗂️ 系統路由架構圖

```
Flask App (app.py)
│
├─ 核心路由 (core_bp)
│  ├─ / (首頁)
│  ├─ /login (登錄)
│  ├─ /register (註冊)
│  ├─ /dashboard (學生面板)
│  ├─ /teacher_dashboard (教師面板)
│  ├─ /api/skills/* (技能 API - 來自 core/routes/*)
│  └─ ... (其他 Web 路由)
│
├─ 練習路由 (practice_bp)
│  ├─ /api/adaptive/* (現有自適應學習 API)
│  │  ├─ /api/adaptive/submit_and_get_next (提交答案、取得下一題)
│  │  ├─ /api/adaptive/rag_settings (RAG 設置)
│  │  ├─ /api/adaptive/rag_hint (取得提示)
│  │  ├─ /api/adaptive/adv_rag_search (進階 RAG 搜尋)
│  │  └─ /api/adaptive/adv_rag_chat (進階 RAG 聊天)
│  └─ ... (其他練習路由)
│
├─ 科展展演路由 (live_show_bp)
│  └─ ... (科展相關路由)
│
├─ 模擬學生路由 (sim_bp)
│  └─ ... (模擬學生 API)
│
└─ ✨ 自適應複習路由 (adaptive_review_bp) [NEW]
   ├─ POST /api/adaptive-review/start
   ├─ GET /api/adaptive-review/analyze/<student_id>
   ├─ POST /api/adaptive-review/feedback
   ├─ GET /api/adaptive-review/plan/<student_id>
   └─ GET /api/adaptive-review/health
```

---

## 🚀 快速入門

### A. Python 本地調用

```python
from adaptive_review_mode import AdaptiveReviewEngine

# 1️⃣ 初始化引擎
engine = AdaptiveReviewEngine()

# 2️⃣ 提供學生學習歷史
item_history = [0, 5, 10, 15]      # 題目 ID
skill_history = [1, 2, 3, 2]       # 技能 ID
resp_history = [1, 1, 0, 1]        # 是否正確 (1=對, 0=錯)

# 3️⃣ 獲取 RL 推薦
recommendations = engine.recommend_next_items(
    item_history,
    skill_history,
    resp_history,
    n_items=5,
    use_rl=True  # 使用 RL 引擎推薦
)

print(recommendations)
# Output:
# [
#     {'item_id': 42, 'skill_id': 3, 'skill_name': 'radical-operations', 'predicted_difficulty': 0.45},
#     {'item_id': 28, 'skill_id': 2, 'skill_name': 'fraction-operations', 'predicted_difficulty': 0.52},
#     ...
# ]
```

### B. Flask API 調用 (推薦用於前端、Web 或外部系統)

#### ✅ 開始複習會話
```bash
curl -X POST http://localhost:5000/api/adaptive-review/start \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU_001",
    "history": {
      "item_history": [0, 5, 10, 15],
      "skill_history": [1, 2, 3, 2],
      "resp_history": [1, 1, 0, 1]
    },
    "n_recommendations": 5,
    "use_rl": true
  }'

# Response:
# {
#   "status": "success",
#   "data": {
#     "student_id": "STU_001",
#     "current_apr": 0.65,
#     "apr_target": 0.80,
#     "recommendations": [...],
#     "session_id": "sess_STU_001_20260418103000",
#     "timestamp": "2026-04-18T10:30:00.000000"
#   }
# }
```

#### 📊 分析學生弱項
```bash
curl -X GET "http://localhost:5000/api/adaptive-review/analyze/STU_001?history_json=$(python -c 'import json, urllib.parse; print(urllib.parse.quote(json.dumps({"item_history": [0, 5, 10], "skill_history": [1, 2, 3], "resp_history": [1, 1, 0]})))')"

# Response:
# {
#   "status": "success",
#   "data": {
#     "student_id": "STU_001",
#     "overall_apr": 0.62,
#     "weakest_skills": [
#       {"skill_id": 5, "skill_name": "radical-operations", "mastery": 0.35},
#       ...
#     ],
#     "strongest_skills": [...],
#     "recommendations": [
#       "🔴 radical-operations: 掌握度 35.00%，需要重點加強",
#       ...
#     ]
#   }
# }
```

#### 📝 提交答題反饋
```bash
curl -X POST http://localhost:5000/api/adaptive-review/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU_001",
    "history": {
      "item_history": [0, 5, 10, 15],
      "skill_history": [1, 2, 3, 2],
      "resp_history": [1, 1, 0, 1]
    },
    "item_id": 42,
    "correct": 1,
    "time_spent": 45
  }'

# Response:
# {
#   "status": "success",
#   "data": {
#     "apr_before": 0.65,
#     "apr_after": 0.68,
#     "apr_change": 0.03,
#     "reached_target": false,
#     "next_recommendations": [...],
#     "feedback": "很好！掌握度提升了，建議繼續練習相關題目"
#   }
# }
```

#### 📅 生成複習計畫
```bash
curl -X GET "http://localhost:5000/api/adaptive-review/plan/STU_001?history_json=...&num_sessions=3"

# Response:
# {
#   "status": "success",
#   "data": {
#     "student_id": "STU_001",
#     "num_sessions": 3,
#     "overall_stats": {
#       "apr_initial": 0.60,
#       "apr_final": 0.78,
#       "apr_gain": 0.18
#     },
#     "sessions": [...]
#   }
# }
```

#### 💚 健康檢查
```bash
curl http://localhost:5000/api/adaptive-review/health

# Response:
# {
#   "status": "success",
#   "message": "複習引擎就緒",
#   "n_skills": 10,
#   "n_items": 100
# }
```

---

## ✅ 路由衝突檢查

### 現有 API 與新 API 的對比

| API 前綴 | 藍圖 | 用途 | 衝突 |
|---------|------|------|------|
| `/api/adaptive/*` | practice_bp | 現有自適應學習 (練習、提示、RAG) | ❌ 無 |
| `/api/adaptive-review/*` | adaptive_review_bp | **新的自適應複習 (RL推薦、分析、計畫)** | ✅ 清楚區分 |
| `/api/skills/*` | core_bp | 技能管理、課程表 | ❌ 無 |
| `/` | core_bp | Web 頁面路由 | ❌ 無 |

**結論**：✅ 完全無衝突。新 API 與現有系統獨立運行。

---

## 🔌 在前端集成

### JavaScript 範例

```javascript
// 1. 開始複習
async function startReview(studentId, history) {
  const response = await fetch('/api/adaptive-review/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: studentId,
      history: history,
      n_recommendations: 5,
      use_rl: true
    })
  });
  return await response.json();
}

// 2. 提交反饋
async function submitFeedback(studentId, history, itemId, isCorrect) {
  const response = await fetch('/api/adaptive-review/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: studentId,
      history: history,
      item_id: itemId,
      correct: isCorrect ? 1 : 0
    })
  });
  return await response.json();
}

// 3. 使用示例
const result = await startReview('STU_001', {
  item_history: [0, 5, 10],
  skill_history: [1, 2, 3],
  resp_history: [1, 1, 0]
});

console.log(`推薦題目: ${result.data.recommendations.length} 題`);
console.log(`當前掌握度: ${(result.data.current_apr * 100).toFixed(1)}%`);
```

---

## 🔧 系統整合確認

✅ **已驗證**：
- [x] adaptive_review_mode.py (核心引擎)
- [x] adaptive_review_api.py (Flask API)
- [x] adaptive_review_examples.py (使用示例)
- [x] adaptive_review_integration.py (整合驗證)
- [x] app.py (已註冊藍圖)
- [x] 無路由衝突
- [x] 5 個 API 端點已就位

📚 **文檔位置**：
- [ADAPTIVE_REVIEW_MODE.md](../ADAPTIVE_REVIEW_MODE.md) - 完整功能文檔
- [adaptive_review_examples.py](../adaptive_review_examples.py) - 代碼範例

---

## 📞 支持

如有問題或需要修改路由，請參閱 [ADAPTIVE_REVIEW_MODE.md](../ADAPTIVE_REVIEW_MODE.md) 或執行驗證腳本：

```bash
python verify_integration.py
```
