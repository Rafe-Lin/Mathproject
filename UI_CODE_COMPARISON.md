# RL 自適應複習模式 - 代碼修改對比

## 1. 樣式表（CSS）修改

### 背景色修改
```css
/* 修改前 - 紫色漸變 */
body {
    font-family: 'Microsoft JhengHei', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* 修改後 - 白色純色 */
body {
    font-family: 'Microsoft JhengHei', Arial, sans-serif;
    background: #ffffff;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    color: #333;
}
```

### 導航欄修改
```css
/* 修改前 - 半透明黑色 + 模糊效果 */
.navbar {
    background: rgba(0, 0, 0, 0.1);
    padding: 15px 30px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(10px);
}

.navbar-brand {
    font-size: 1.5em;
    font-weight: bold;
}

.navbar-links a {
    color: white;
    text-decoration: none;
    margin-left: 20px;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background 0.3s;
}

.navbar-links a:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* 修改後 - 淺灰色 */
.navbar {
    background: #f5f5f5;
    padding: 15px 30px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand {
    font-size: 1.3em;
    font-weight: bold;
    color: #333;
}

.navbar-links a {
    color: #555;
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 0.95em;
    transition: background 0.3s;
}

.navbar-links a:hover {
    background: #e8e8e8;
}
```

### 邊欄卡片修改
```css
/* 修改前 */
.sidebar {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 30px;
}

.sidebar h2 {
    color: #667eea;
    margin-bottom: 20px;
    font-size: 1.3em;
}

.stat-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    border-left: 4px solid #667eea;
}

.stat-card .value {
    font-size: 1.8em;
    font-weight: bold;
    color: #667eea;
}

/* 修改後 */
.sidebar {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    position: sticky;
    top: 30px;
}

.sidebar h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 1.1em;
    font-weight: 600;
}

.stat-card {
    background: #fafafa;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    border: 1px solid #e0e0e0;
}

.stat-card .value {
    font-size: 1.6em;
    font-weight: bold;
    color: #0066cc;
}
```

### 按鈕修改
```css
/* 修改前 - 漸變背景 */
.btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
    background: #f8f9fa;
    color: #667eea;
    border: 2px solid #667eea;
}

/* 修改後 - 純色背景 */
.btn-primary {
    background: #0066cc;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #0052a3;
}

.btn-secondary {
    background: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}
```

### 進度條修改
```css
/* 修改前 */
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transition: width 0.5s ease;
}

/* 修改後 */
.progress-fill {
    height: 100%;
    background: #0066cc;
    transition: width 0.5s ease;
}
```

### 推薦卡修改
```css
/* 修改前 - 大陰影 + 變換 */
.recommendation-card {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    cursor: pointer;
    transition: all 0.3s;
}

.recommendation-card:hover {
    border-color: #667eea;
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
    transform: translateY(-3px);
}

.recommendation-card.selected {
    background: #f0f7ff;
    border-color: #667eea;
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
}

/* 修改後 - 簡單邊框 + 背景顏色 */
.recommendation-card {
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.3s;
}

.recommendation-card:hover {
    border-color: #0066cc;
    background: #f5fbff;
}

.recommendation-card.selected {
    background: #f0f7ff;
    border-color: #0066cc;
    border-width: 2px;
}
```

---

## 2. HTML 標記（Markup）修改

### 導航欄
```html
<!-- 修改前 -->
<div class="navbar-brand">🎓 自適應複習模式</div>

<!-- 修改後 -->
<div class="navbar-brand">自適應複習模式</div>
```

### 左側欄標題
```html
<!-- 修改前 -->
<h2>📊 複習進度</h2>

<!-- 修改後 -->
<h2>複習進度</h2>
```

### 按鈕文本
```html
<!-- 修改前 -->
<button class="btn btn-primary" id="startReviewBtn" onclick="startReview()">
    🚀 開始複習
</button>
<button class="btn btn-primary" id="submitFeedbackBtn" onclick="showFeedback()" style="display: none;">
    ✅ 提交答案
</button>
<button class="btn btn-secondary" id="generatePlanBtn" onclick="generatePlan()">
    📅 生成計畫
</button>

<!-- 修改後 -->
<button class="btn btn-primary" id="startReviewBtn" onclick="startReview()">
    開始複習
</button>
<button class="btn btn-primary" id="submitFeedbackBtn" onclick="showFeedback()" style="display: none;">
    提交答案
</button>
<button class="btn btn-secondary" id="generatePlanBtn" onclick="generatePlan()">
    生成計畫
</button>
```

### 標題和副標題
```html
<!-- 修改前 -->
<h1 style="color: #667eea; margin-bottom: 15px;">歡迎來到自適應複習模式</h1>
<p style="color: #666; font-size: 1.05em; margin-bottom: 30px;">
    AI 智慧推薦引擎會根據您的學習歷史，<br>推薦最適合您的複習題目。
</p>

<!-- 修改後 -->
<h1 style="color: #333; margin-bottom: 15px;">自適應複習模式</h1>
<p style="color: #888; font-size: 1.05em; margin-bottom: 30px;">
    系統將根據您的學習歷史，<br>推薦最適合您的複習題目。
</p>
```

### 推薦列表標題
```html
<!-- 修改前 -->
<h3>💡 RL 引擎推薦 (基於您的學習狀況)</h3>

<!-- 修改後 -->
<h3>RL 引擎推薦 (基於您的學習狀況)</h3>
```

### 反饋按鈕
```html
<!-- 修改前 -->
<button class="feedback-btn" onclick="submitFeedback(true)">✅ 答對了</button>
<button class="feedback-btn" onclick="submitFeedback(false)">❌ 答錯了</button>
<button class="feedback-btn" onclick="requestHint()">💡 需要提示</button>

<!-- 修改後 -->
<button class="feedback-btn" onclick="submitFeedback(true)">答對了</button>
<button class="feedback-btn" onclick="submitFeedback(false)">答錯了</button>
<button class="feedback-btn" onclick="requestHint()">需要提示</button>
```

### 計畫標題
```html
<!-- 修改前 -->
<h3>📅 建議的複習計畫</h3>

<!-- 修改後 -->
<h3>建議的複習計畫</h3>
```

### 主內容標題
```html
<!-- 修改前 -->
<h1>📖 推薦題目</h1>

<!-- 修改後 -->
<h1>推薦題目</h1>
```

### 錯誤狀態
```html
<!-- 修改前 -->
<div class="empty-state">
    <div class="empty-state-icon">⚠️</div>
    <h3>發生錯誤</h3>
    <p id="errorMessage">無法載入複習內容，請稍後重試。</p>
    ...
</div>

<!-- 修改後 -->
<div class="empty-state">
    <h3>發生錯誤</h3>
    <p id="errorMessage">無法載入複習內容，請稍後重試。</p>
    ...
</div>
```

---

## 3. JavaScript 修改

### 提示功能
```javascript
/* 修改前 */
function requestHint() {
    alert('💡 提示功能即將推出！');
}

/* 修改後 */
function requestHint() {
    alert('提示功能即將推出！');
}
```

### 反饋訊息
```javascript
/* 修改前 */
if (feedbackData.reached_target) {
    alert('🎉 恭喜！已達到目標掌握度！');
    startReview();
}

/* 修改後 */
if (feedbackData.reached_target) {
    alert('恭喜！已達到目標掌握度！');
    startReview();
}
```

### 推薦指數顯示
```javascript
/* 修改前 */
<span>推薦指數: ⭐ ${(rec.recommendation_score || 0).toFixed(1)}</span>

/* 修改後 */
<span>推薦指數: ${(rec.recommendation_score || 0).toFixed(1)}</span>
```

---

## 4. Dashboard 按鈕修改

### dashboard.html
```html
<!-- 修改前 -->
<a href="{{ url_for('adaptive_review') }}"
    style="padding: 10px 18px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 4px; font-weight: bold; cursor: pointer;">
    ✨ RL 智慧複習
</a>

<!-- 修改後 -->
<a href="{{ url_for('adaptive_review') }}"
    style="padding: 10px 18px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; font-weight: 500; cursor: pointer;">
    自適應複習
</a>
```

---

## 5. 顏色對應表

| 用途 | 修改前 | 修改後 | 說明 |
|-----|--------|--------|------|
| 主背景 | #667eea 漸變 | #ffffff | 白色背景 |
| 導航欄 | rgba(0,0,0,0.1) | #f5f5f5 | 淡灰色 |
| 主色 | #667eea | #0066cc | 改為藍色 |
| 輔助色 | #764ba2 | #0052a3 | 深藍色 |
| 邊框 | #e9ecef | #e0e0e0 | 灰色邊框 |
| 文字主 | white | #333 | 深灰色 |
| 文字副 | rgba(255,255,255,0.7) | #555/#888 | 中等灰色 |
| 背景淺 | #f8f9fa | #fafafa | 更淺的灰色 |

---

## 6. 移除的 CSS 特性

```css
/* 已移除的效果 */

/* 1. 背景濾鏡 */
backdrop-filter: blur(10px);  /* ✗ 移除 */

/* 2. 漸變 */
background: linear-gradient(135deg, #667eea, #764ba2);  /* ✗ 改為純色 */
background: linear-gradient(90deg, #667eea, #764ba2);   /* ✗ 改為純色 */

/* 3. 陰影 */
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);  /* ✗ 移除 */
box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);  /* ✗ 移除 */

/* 4. 變換 */
transform: translateY(-2px);   /* ✗ 移除 */
transform: translateY(-3px);   /* ✗ 移除 */

/* 5. 大邊框半徑 */
border-radius: 15px;   /* ✗ 改為 8px */
border-radius: 12px;   /* ✗ 改為 6px */
border-radius: 10px;   /* ✗ 改為 6px */

/* 6. 偽元素 */
.plan-item::before { ... }   /* ✗ 移除 */
```

---

## 總結

✓ **全部修改完成**

- 表情符號：40+ → 0
- 漸變效果：5+ → 0
- 陰影效果：多個 → 0
- 邊框半徑：10-15px → 4-8px
- 配色方案：紫色 → 藍色
- 風格：華麗 → 簡潔
