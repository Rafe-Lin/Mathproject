# 知識圖譜視覺化功能 - 完整修改文件

**開發日期**：2026-01-31  
**功能名稱**：知識圖譜視覺化 (Knowledge Graph Visualization)  
**開發者**：Antigravity AI Assistant

---

## 📋 目錄

1. [功能概述](#功能概述)
2. [檔案變更清單](#檔案變更清單)
3. [詳細程式碼變更](#詳細程式碼變更)
4. [資料庫整合說明](#資料庫整合說明)
5. [使用說明](#使用說明)
6. [技術架構](#技術架構)

---

## 功能概述

新增知識圖譜視覺化功能，以互動式圖表展示知識點之間的前置關係，並整合學生能力值系統。此功能幫助學生和教師清楚了解知識點的學習順序和依賴關係。

### 核心特性

- ✅ 視覺化展示知識點前置關係
- ✅ 整合學生能力值系統（ability_a, concept_u, calculation_c）
- ✅ 四層級聯篩選（課程類型 → 年級 → 冊別 → 章節）
- ✅ 互動式 D3.js 力導向圖
- ✅ 節點顏色編碼表示掌握程度
- ✅ 拖曳、縮放、提示框等互動功能

---

## 檔案變更清單

### 新增檔案 (3個)

| 檔案路徑 | 說明 | 行數 |
|---------|------|------|
| [core/routes/knowledge_graph.py](file:///c:/Users/NICK/Mathproject/core/routes/knowledge_graph.py) | 知識圖譜後端 API 路由 | 219 行 |
| [templates/knowledge_graph.html](file:///c:/Users/NICK/Mathproject/templates/knowledge_graph.html) | 知識圖譜前端視覺化頁面 | 750+ 行 |
| 專案文檔 | 任務、計畫、完成報告 | - |

### 修改檔案 (2個)

| 檔案路徑 | 修改內容 | 變更行數 |
|---------|---------|---------|
| [core/routes/__init__.py](file:///c:/Users/NICK/Mathproject/core/routes/__init__.py) | 註冊 knowledge_graph 模組 | +1 行 |
| [templates/dashboard.html](file:///c:/Users/NICK/Mathproject/templates/dashboard.html) | 新增知識圖譜導航按鈕 | +2 行 |

---

## 詳細程式碼變更

### 1. 新增：core/routes/knowledge_graph.py

**主要路由**：

#### 路由 1：知識圖譜頁面
```python
@core_bp.route('/knowledge-graph')
@login_required
def knowledge_graph():
    return render_template('knowledge_graph.html', username=current_user.username)
```

#### 路由 2：圖譜資料 API
```python
@core_bp.route('/api/knowledge-graph/data')
@login_required
def get_knowledge_graph_data():
    # 查詢參數: curriculum, grade, volume, chapter
    # 返回: JSON 格式的圖譜資料 (nodes + links)
```

**核心邏輯**：

1. 根據篩選條件查詢 `SkillCurriculum` 表
2. 查詢 `StudentAbility` 表獲取能力值
3. 查詢 `SkillPrerequisites` 表獲取前置關係
4. 計算掌握狀態：
   - `ability_a >= 100` → mastered（已掌握）
   - `50 <= ability_a < 100` → learning（學習中）
   - `ability_a < 50` → not_started（未開始）

**返回資料格式**：
```json
{
  "nodes": [{
    "id": "skill_id",
    "name": "知識點名稱",
    "ability_a": 85.5,
    "concept_u": 70.0,
    "calculation_c": 65.0,
    "mastery_status": "learning"
  }],
  "links": [{
    "source": "prerequisite_id",
    "target": "skill_id"
  }]
}
```

#### 路由 3：篩選選項 API
```python
@core_bp.route('/api/knowledge-graph/filters')
@login_required
def get_knowledge_graph_filters():
    # 根據已選條件返回下一層選項
```

---

### 2. 新增：templates/knowledge_graph.html

**頁面結構**：

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <!-- 載入動畫 -->
    <div id="loading-overlay"></div>
    
    <!-- 篩選控制區 -->
    <div class="filter-controls">
        <select id="curriculum-select"></select>
        <select id="grade-select"></select>
        <select id="volume-select"></select>
        <select id="chapter-select"></select>
        <button onclick="loadGraph()">顯示圖譜</button>
    </div>
    
    <!-- 圖例 -->
    <div class="legend">
        <div class="legend-color mastered">已掌握</div>
        <div class="legend-color learning">學習中</div>
        <div class="legend-color not-started">未開始</div>
    </div>
    
    <!-- 圖表容器 -->
    <svg id="graph-svg"></svg>
    
    <!-- 提示框 -->
    <div id="tooltip"></div>
</body>
</html>
```

**CSS 樣式**：
```css
.node.mastered circle { fill: #27ae60; }  /* 綠色 */
.node.learning circle { fill: #f39c12; }  /* 黃色 */
.node.not-started circle { fill: #95a5a6; } /* 灰色 */
```

**JavaScript 核心功能**：

1. **篩選級聯**：
```javascript
async function onCurriculumChange() {
    const curriculum = document.getElementById('curriculum-select').value;
    const response = await fetch(`/api/knowledge-graph/filters?curriculum=${curriculum}`);
    const data = await response.json();
    // 填充年級選單
}
```

2. **D3.js 渲染**：
```javascript
function renderGraph(data) {
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).distance(150))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width/2, height/2));
    
    // 繪製連接線和節點
}
```

3. **拖曳功能**：
```javascript
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}
```

---

### 3. 修改：core/routes/__init__.py

```diff
-from . import auth, admin, practice, classroom, analysis, exam
+from . import auth, admin, practice, classroom, analysis, exam, knowledge_graph
```

---

### 4. 修改：templates/dashboard.html

**位置**：第 348-350 行（導航欄）

```diff
 <a href="{{ url_for('core.student_diagnosis') }}"
     style="background: #8e44ad; padding: 8px 15px; border-radius: 4px;">📊 學習診斷</a>
+<a href="{{ url_for('core.knowledge_graph') }}"
+    style="background: #16a085; padding: 8px 15px; border-radius: 4px;">🌳 知識圖譜</a>
```

---

## 資料庫整合說明

### 使用的資料表

| 資料表 | 用途 | 主要欄位 |
|--------|------|---------|
| `SkillCurriculum` | 課程分類 | curriculum, grade, volume, chapter, section |
| `SkillPrerequisites` | 前置關係 | skill_id, prerequisite_id |
| `StudentAbility` | 能力值 | ability_a, concept_u, calculation_c |
| `SkillInfo` | 知識點資訊 | skill_ch_name, description, category |

### 能力值判定

來自 `adaptive_config.py`：

```python
# 預設值
ABILITY_DEFAULT = 20.0
CONCEPT_DEFAULT = 20.0
CALCULATION_DEFAULT = 20.0

# 掌握狀態判定
if ability_a >= 100:    # 已掌握
elif ability_a >= 50:   # 學習中
else:                   # 未開始
```

---

## 使用說明

### 訪問步驟

1. 登入系統
2. 點擊導航欄的 **🌳 知識圖譜** 按鈕
3. 選擇篩選條件（課程 → 年級 → 冊別 → 章節）
4. 點擊「顯示圖譜」

### 互動操作

- **拖曳節點**：點擊並拖曳
- **縮放**：滑鼠滾輪
- **平移**：空白處拖曳
- **查看詳情**：滑鼠懸停

### 節點顏色

- 🟢 綠色：已掌握（ability_a ≥ 100）
- 🟡 黃色：學習中（50 ≤ ability_a < 100）
- ⚪ 灰色：未開始（ability_a < 50）

---

## 技術架構

### 技術棧

**前端**：
- D3.js v7（力導向圖）
- Vanilla JavaScript
- CSS3
- Bootstrap Icons

**後端**：
- Flask
- SQLAlchemy
- Flask-Login

### API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/knowledge-graph` | GET | 頁面渲染 |
| `/api/knowledge-graph/data` | GET | 圖譜資料 |
| `/api/knowledge-graph/filters` | GET | 篩選選項 |

### 資料流程

```
前端篩選 → API 請求 → 查詢資料庫 → 組裝 JSON → 返回前端 → D3.js 渲染
```

---

## 總結

**新增檔案**：3 個  
**修改檔案**：2 個  
**總程式碼行數**：約 1000+ 行

**核心成就**：
- ✅ 完整的後端 API 系統
- ✅ 互動式 D3.js 視覺化
- ✅ 整合學生能力值系統
- ✅ 四層級聯篩選功能

**技術亮點**：
- D3.js 力導向圖演算法
- 整合 adaptive_config.py 標準
- RESTful API 設計
- 模組化架構

---

**文件版本**：1.0  
**最後更新**：2026-02-01
