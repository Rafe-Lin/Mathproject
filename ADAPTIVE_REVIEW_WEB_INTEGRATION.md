<!-- 自適應複習模式 - Web 集成完成說明 -->

# 自適應複習模式 - Web 集成使用指南

## ✅ 集成完成確認

所有組件已成功整合到 Flask Web 應用中。

### 已部署的組件

| 組件 | 位置 | 狀態 |
|------|------|------|
| 複習模式頁面 | `/templates/adaptive_review.html` | ✅ 已創建 |
| 儀表板入口按鈕 | `/templates/dashboard.html` (已更新) | ✅ 已添加 |
| Flask 路由 | `/app.py` (`/adaptive-review`) | ✅ 已註冊 |
| API 層 | `/adaptive_review_api.py` | ✅ 已整合 |
| 核心引擎 | `/adaptive_review_mode.py` | ✅ 已運行 |

---

## 🚀 快速開始

### 1️⃣ 啟動應用

```bash
cd c:\Users\NICK\Downloads\Mathproject-main\ (2)\Mathproject-main
python app.py
```

訪問 `http://localhost:5000` 並登錄。

### 2️⃣ 進入自適應複習模式

**方式 A：從儀表板進入**
1. 登錄後進入學生儀表板 (`/dashboard`)
2. 在右上角找到紫色按鈕：**✨ RL 智慧複習**
3. 點擊進入複習模式

**方式 B：直接訪問**
- 打開 `http://localhost:5000/adaptive-review`

### 3️⃣ 使用複習功能

```
┌─────────────────────────────────────────────────────────┐
│                    📚 自適應複習模式                     │
├──────────────────┬──────────────────────────────────────┤
│                  │                                      │
│  左側面板        │     主內容區                          │
│  ━━━━━━━━━━━━   │     ━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                  │                                      │
│ 📊 複習進度      │  💡 RL 引擎推薦題目                 │
│ • 當前掌握度     │  • 5 個推薦題目                     │
│ • 目標掌握度     │  • 難度預估                         │
│ • 已答題數       │  • RL 分數                          │
│ • 正確率         │                                      │
│                  │  📝 選擇題目 → 提交答案             │
│ 🚀 開始複習      │  • 答對/答錯反饋                   │
│ 📅 生成計畫      │  • 自動計算掌握度變化               │
│ ← 返回           │  • 推薦下一步學習                   │
│                  │                                      │
│                  │  📅 複習計畫 (可選)                 │
│                  │  • 多會話建議                       │
│                  │  • 預期掌握度進度                   │
│                  │                                      │
└──────────────────┴──────────────────────────────────────┘
```

#### 功能說明

**🚀 開始複習**
- 基於您的學習歷史，AI RL 模型推薦最適合的複習題目
- 系統計算當前掌握度
- 推薦題目按難度和重要性排序

**選擇題目**
- 點擊任何推薦卡片選擇該題目
- 卡片會高亮顯示選中狀態

**提交答案**
- 答對/答錯反饋
- 系統根據結果更新知識追蹤 (AKT)
- 自動推薦下一題

**📅 生成計畫**
- 分析當前掌握度
- 生成多會話複習計畫
- 預估達到目標掌握度的時間

---

## 📊 頁面布局詳解

### 左側面板（統計 & 控制）

```
📊 複習進度

┌──────────────┬──────────────┐
│ 當前掌握度   │ 目標掌握度   │
│     65%      │     80%      │
├──────────────┼──────────────┤
│ 已答題數     │ 正確率       │
│      8       │    75%       │
└──────────────┴──────────────┘

總體掌握度進度
[████████░░░░░░░░░░░░░░░░░░░░░░░░░]
65% / 80%

[🚀 開始複習]
[📅 生成計畫]
[← 返回]
```

### 右側主內容（推薦 & 反饋）

```
📖 推薦題目

會話已啟動，為您準備最佳複習題目...

💡 RL 引擎推薦

┌─────────────────────────────────┐
│ 根式運算              困難       │
│ 題目 ID: 42 | RL 分數: 0.85     │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 分數運算              中等       │
│ 題目 ID: 28 | RL 分數: 0.72     │
└─────────────────────────────────┘

[已選擇題目後]

您對這道題目的感受如何？
[✅ 答對了] [❌ 答錯了] [💡 需要提示]
```

---

## 🔌 API 端點 (後端開發者)

### 1. 開始複習會話

**端點**：`POST /api/adaptive-review/start`

**請求**：
```json
{
  "student_id": "STU_001",
  "history": {
    "item_history": [0, 5, 10],
    "skill_history": [1, 2, 3],
    "resp_history": [1, 1, 0]
  },
  "n_recommendations": 5,
  "use_rl": true
}
```

**回應**：
```json
{
  "status": "success",
  "data": {
    "student_id": "STU_001",
    "current_apr": 0.65,
    "apr_target": 0.80,
    "recommendations": [
      {
        "item_id": 42,
        "skill_id": 3,
        "skill_name": "radical-operations",
        "predicted_difficulty": 0.45,
        "rl_score": 0.85,
        "recommendation_score": 4.2
      },
      ...
    ],
    "session_id": "sess_STU_001_20260418103000",
    "timestamp": "2026-04-18T10:30:00"
  }
}
```

### 2. 提交答題反饋

**端點**：`POST /api/adaptive-review/feedback`

**請求**：
```json
{
  "student_id": "STU_001",
  "history": {...},
  "item_id": 42,
  "correct": 1,
  "time_spent": 45
}
```

**回應**：
```json
{
  "status": "success",
  "data": {
    "apr_before": 0.65,
    "apr_after": 0.68,
    "apr_change": 0.03,
    "reached_target": false,
    "next_recommendations": [...],
    "feedback": "很好！掌握度提升了，建議繼續練習相關題目"
  }
}
```

### 3. 分析學生弱項

**端點**：`GET /api/adaptive-review/analyze/<student_id>`

**參數**：
- `history_json`: URL-encoded JSON

**回應**：
```json
{
  "status": "success",
  "data": {
    "overall_apr": 0.62,
    "weakest_skills": [
      {"skill_id": 5, "skill_name": "radical-operations", "mastery": 0.35},
      ...
    ],
    "recommendations": [...]
  }
}
```

### 4. 生成複習計畫

**端點**：`GET /api/adaptive-review/plan/<student_id>`

**參數**：
- `history_json`: URL-encoded JSON
- `num_sessions`: 會話數 (預設 3)

### 5. 健康檢查

**端點**：`GET /api/adaptive-review/health`

**回應**：
```json
{
  "status": "success",
  "message": "複習引擎就緒",
  "n_skills": 17,
  "n_items": 212
}
```

---

## 💻 JavaScript 前端集成

### 初始化

```html
<script>
  // 全局變數
  let currentStudentId = '{{ current_user.id }}';
  let learningHistory = {
    item_history: [],
    skill_history: [],
    resp_history: []
  };

  // 開始複習
  async function startReview() {
    const response = await fetch('/api/adaptive-review/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudentId,
        history: learningHistory,
        n_recommendations: 5,
        use_rl: true
      })
    });
    const data = await response.json();
    displayRecommendations(data.data.recommendations);
  }

  // 提交反饋
  async function submitFeedback(itemId, isCorrect) {
    learningHistory.item_history.push(itemId);
    // ... 更新其他歷史

    const response = await fetch('/api/adaptive-review/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudentId,
        history: learningHistory,
        item_id: itemId,
        correct: isCorrect ? 1 : 0
      })
    });
    const data = await response.json();
    updateStats(data.data);
  }
</script>
```

---

## 📁 檔案結構

```
project-root/
├── app.py                              (新增路由)
│   └── @app.route('/adaptive-review')
│
├── templates/
│   ├── adaptive_review.html            (新建)
│   └── dashboard.html                  (已更新，新增按鈕)
│
├── adaptive_review_mode.py             (核心引擎)
├── adaptive_review_api.py              (API 層)
│
├── ADAPTIVE_REVIEW_MODE.md             (功能文檔)
├── ADAPTIVE_REVIEW_ROUTING.md          (路由說明)
├── ADAPTIVE_REVIEW_WEB_INTEGRATION.md  (本文件)
│
└── verify_web_integration.py           (驗證腳本)
```

---

## 🧪 測試與驗證

### 運行驗證腳本

```bash
python verify_web_integration.py
```

**輸出示例**：
```
================================================================================
自適應複習模式 - 完整 Web 集成驗證
================================================================================

[1/5] 驗證 HTML 模板...
   ✅ adaptive_review.html - 正常
   ✅ dashboard.html - 正常

[2/5] 驗證 Flask 應用路由...
   ✅ 頁面路由已註冊: ['/adaptive-review']
   ✅ 複習相關 API 路由: 5 個

[3/5] 驗證 API 藍圖...
   ✅ adaptive_review_bp 已導入

[4/5] 驗證核心模組...
   ✅ AdaptiveReviewEngine 已初始化
      • 技能數: 17
      • 題目數: 212

[5/5] 檢查文檔...
   ✅ 所有文檔已就位

✅ 完整 Web 集成驗證完成！
```

### 手動測試

1. **訪問儀表板**
   ```
   http://localhost:5000/dashboard
   ```
   應能看到右上角的「✨ RL 智慧複習」按鈕

2. **進入複習模式**
   ```
   http://localhost:5000/adaptive-review
   ```
   應看到歡迎頁面和「開始複習」按鈕

3. **測試 API**
   ```bash
   curl -X GET http://localhost:5000/api/adaptive-review/health
   ```
   應返回：`{"status": "success", ...}`

---

## 📋 功能清單

| 功能 | 狀態 | 備註 |
|------|------|------|
| Web 頁面 | ✅ 完成 | `/adaptive-review` 已就位 |
| 儀表板入口 | ✅ 完成 | 添加「RL 智慧複習」按鈕 |
| RL 推薦引擎 | ✅ 完成 | 5 個 API 端點 |
| 知識追蹤 (AKT) | ✅ 完成 | 自動計算掌握度 |
| 反饋系統 | ✅ 完成 | 答對/答錯追蹤 |
| 計畫生成 | ✅ 完成 | 多會話建議 |
| 統計儀表板 | ✅ 完成 | 實時進度顯示 |
| 前端 UI | ✅ 完成 | 響應式設計 |

---

## 🎓 使用場景

### 場景 1：學生進行自我評估複習

1. 學生登錄進入儀表板
2. 點擊「RL 智慧複習」按鈕
3. 系統基於學習歷史推薦題目
4. 學生練習→提交反饋→系統推薦下一題
5. 查看複習計畫了解進度

### 場景 2：教師安排學生複習

1. 教師在教師面板設置複習要求
2. 學生收到複習任務提醒
3. 學生使用自適應複習模式完成任務
4. 教師查看學生完成情況和掌握度提升

### 場景 3：系統診斷與補救

1. 系統檢測到學生在某技能上掌握度低
2. 自動推薦相關複習題目
3. 學生通過複習逐步提升
4. 系統追蹤進度並自動調整難度

---

## 🔧 自訂與擴展

### 修改推薦題目數量

編輯 `adaptive_review.html`，找到：
```javascript
n_recommendations: 5,  // 改為其他數字
```

### 修改目標掌握度

編輯 `adaptive_review_mode.py`：
```python
BETA_THRESHOLD = 0.80  # 改為 0.70, 0.85 等
```

### 自訂前端樣式

編輯 `adaptive_review.html` 中的 `<style>` 部分

---

## 📞 常見問題

**Q: 我應該如何開始？**
A: 執行 `python app.py`，然後訪問 `http://localhost:5000/adaptive-review`

**Q: RL 推薦是如何工作的？**
A: 系統使用 PPO 算法，基於學生當前知識狀態推薦最有幫助的題目

**Q: 掌握度是如何計算的？**
A: 使用 AKT (Attentive Knowledge Tracing) 模型追蹤

**Q: 我可以離線使用嗎？**
A: 可以。API 是本地的，只需要 Flask 應用在線

---

## ✅ 完成清單

- [x] 複習模式 HTML 頁面
- [x] 儀表板入口按鈕
- [x] Flask 路由
- [x] API 藍圖
- [x] 前端 JavaScript
- [x] 統計儀表板
- [x] 推薦系統
- [x] 反饋機制
- [x] 計畫生成
- [x] 文檔

---

**🎉 自適應複習模式的 Web 集成已完全完成！系統已可正式使用。**
