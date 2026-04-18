# 知識圖譜視覺化功能 - 完成報告

## 功能概述

成功實作了知識圖譜視覺化功能，可以展示知識點之間的前置關係，並整合學生能力值系統。此功能使用 D3.js 力導向圖佈局，提供互動式的知識點關係展示。

## 已完成的變更

### 後端實作

#### [NEW] [core/routes/knowledge_graph.py](file:///c:/Users/NICK/Mathproject/core/routes/knowledge_graph.py)

新增了完整的知識圖譜後端 API：

**主要路由**：
- `GET /knowledge-graph` - 渲染知識圖譜頁面
- `GET /api/knowledge-graph/data` - 提供圖譜資料（節點和連接）
- `GET /api/knowledge-graph/filters` - 提供篩選選項（課程、年級、冊別、章節）

**核心功能**：
- 整合 `SkillPrerequisites` 表獲取前置關係
- 整合 `SkillCurriculum` 表獲取課程分類
- 整合 `StudentAbility` 表獲取學生能力值（ability_a, concept_u, calculation_c）
- 支援多層級篩選（課程類型 → 年級 → 冊別 → 章節）
- 自動計算掌握狀態（已掌握/學習中/未開始）

**能力值判定邏輯**：
```python
if ability_a >= 100:
    mastery_status = 'mastered'      # 已掌握
elif ability_a >= 50:
    mastery_status = 'learning'      # 學習中
else:
    mastery_status = 'not_started'   # 未開始
```

---

#### [MODIFY] [core/routes/__init__.py](file:///c:/Users/NICK/Mathproject/core/routes/__init__.py)

註冊了新的 `knowledge_graph` 模組到路由系統。

---

### 前端實作

#### [NEW] [templates/knowledge_graph.html](file:///c:/Users/NICK/Mathproject/templates/knowledge_graph.html)

建立了完整的知識圖譜視覺化頁面，包含：

**介面元素**：
- 📊 **篩選控制區**：四層級聯式下拉選單（課程類型 → 年級 → 冊別 → 章節）
- 🎨 **圖例說明**：顏色編碼說明（綠色=已掌握、黃色=學習中、灰色=未開始）
- 📈 **圖表容器**：700px 高度的 SVG 畫布
- 💬 **互動提示框**：顯示節點詳細資訊

**D3.js 視覺化功能**：
- ✅ 力導向圖佈局（Force-Directed Graph）
- ✅ 節點拖曳功能
- ✅ 縮放和平移（Zoom & Pan）
- ✅ 箭頭標記顯示方向（從前置知識點指向目標知識點）
- ✅ 滑鼠懸停顯示詳細資訊（知識點名稱、描述、三項能力值）
- ✅ 節點顏色根據能力值動態變化

**節點樣式**：
- 🟢 綠色圓圈：已掌握（ability_a ≥ 100）
- 🟡 黃色圓圈：學習中（50 ≤ ability_a < 100）
- ⚪ 灰色圓圈：未開始（ability_a < 50）

---

#### [MODIFY] [templates/dashboard.html](file:///c:/Users/NICK/Mathproject/templates/dashboard.html)

在導航欄新增了知識圖譜按鈕：
```html
<a href="{{ url_for('core.knowledge_graph') }}"
   style="background: #16a085; padding: 8px 15px; border-radius: 4px;">🌳 知識圖譜</a>
```

位置：放在「📊 學習診斷」按鈕之後。

---

## 手動測試指南

### 前置條件

應用程式已啟動在 `http://localhost:5000`（目前正在運行中）。

### 測試步驟

#### 1. 登入系統

1. 開啟瀏覽器，訪問 `http://localhost:5000`
2. 使用測試帳號登入（學生或教師身份皆可）

#### 2. 訪問知識圖譜頁面

1. 登入後，在導航欄找到 **🌳 知識圖譜** 按鈕（綠色背景）
2. 點擊進入知識圖譜頁面

#### 3. 測試篩選功能

**測試案例 1：國中數學**
1. 選擇「課程類型」→ **國中**
2. 等待「年級」下拉選單自動載入
3. 選擇「年級」→ **7年級**
4. 等待「冊別」下拉選單自動載入
5. 選擇「冊別」→ **數學1上**
6. 等待「章節」下拉選單自動載入
7. 選擇「章節」→ **第一章**（或任何可用章節）
8. 點擊 **🔍 顯示圖譜** 按鈕

**測試案例 2：普高數學**
1. 點擊「重置」按鈕清空篩選
2. 選擇「課程類型」→ **普高**
3. 依序選擇年級、冊別、章節
4. 點擊「顯示圖譜」

#### 4. 測試圖表互動

**拖曳測試**：
- 點擊並拖曳任一節點，觀察節點是否可以移動
- 釋放滑鼠後，節點應該在新位置穩定下來

**縮放測試**：
- 使用滑鼠滾輪縮放圖表
- 確認可以放大和縮小

**平移測試**：
- 在空白處點擊並拖曳，移動整個圖表視野

**提示框測試**：
- 將滑鼠懸停在任一節點上
- 確認出現黑色提示框，顯示：
  - 知識點名稱
  - 描述
  - 綜合能力值
  - 觀念能力值
  - 計算熟練度值

#### 5. 驗證能力值顯示

觀察節點顏色：
- **綠色節點**：表示該知識點已掌握（能力值 ≥ 100）
- **黃色節點**：表示正在學習中（能力值 50-99）
- **灰色節點**：表示尚未開始學習（能力值 < 50）

#### 6. 驗證前置關係

觀察箭頭方向：
- 箭頭應該從**前置知識點**指向**目標知識點**
- 例如：「整數運算」→「因式分解」表示學習因式分解前需要先掌握整數運算

---

## 技術細節

### 資料流程

```mermaid
graph LR
    A[前端篩選] --> B[API 請求]
    B --> C[查詢 SkillCurriculum]
    C --> D[查詢 SkillPrerequisites]
    D --> E[查詢 StudentAbility]
    E --> F[組裝 JSON 資料]
    F --> G[返回前端]
    G --> H[D3.js 渲染]
```

### 資料庫查詢

使用了三個主要資料表：

1. **SkillCurriculum**：獲取課程分類資訊
2. **SkillPrerequisites**：獲取知識點前置關係
3. **StudentAbility**：獲取學生能力值（ability_a, concept_u, calculation_c）

### D3.js 實作要點

- **佈局演算法**：使用 `d3.forceSimulation()` 力導向圖
- **力的設定**：
  - `forceLink`：連接線距離 150px
  - `forceManyBody`：節點排斥力 -300
  - `forceCenter`：圖表居中
  - `forceY`：垂直方向微調
- **節點半徑**：15px
- **箭頭標記**：使用 SVG `<marker>` 元素

---

## 已知限制與未來改進

### 當前限制

1. **樹狀圖佈局**：目前使用力導向圖，未來可改為嚴格的樹狀圖（由上而下）
2. **多根節點處理**：當有多個沒有前置知識點的節點時，會分散顯示
3. **大型圖表效能**：當知識點超過 50 個時，可能需要優化渲染效能

### 建議改進

1. **切換佈局模式**：提供「力導向圖」和「樹狀圖」兩種佈局選項
2. **節點摺疊**：實作點擊節點摺疊/展開子節點功能
3. **路徑高亮**：點擊節點時高亮顯示所有前置知識點路徑
4. **匯出功能**：支援匯出為 PNG 或 SVG 圖片
5. **學習路徑推薦**：根據能力值自動推薦下一個應該學習的知識點

---

## 驗證結果

### ✅ 已完成

- [x] 後端 API 路由建立完成
- [x] 前端頁面建立完成
- [x] 整合 StudentAbility 能力值系統
- [x] 實作篩選功能（四層級聯）
- [x] 實作 D3.js 視覺化
- [x] 實作互動功能（拖曳、縮放、提示框）
- [x] 在 dashboard 新增導航按鈕

### ⏳ 待手動驗證

由於瀏覽器環境問題，以下項目需要您手動測試：

- [ ] 確認圖表正確顯示知識點和連接
- [ ] 確認能力值顏色編碼正確
- [ ] 確認前置關係箭頭方向正確
- [ ] 確認篩選功能正常運作
- [ ] 確認互動功能（拖曳、縮放）正常

---

## 測試資料驗證腳本

如果需要驗證資料庫中的前置關係，可以在 Python console 中執行：

```python
from app import app
from models import db, SkillPrerequisites, SkillInfo

with app.app_context():
    # 查看總共有多少前置關係
    prereqs = db.session.query(SkillPrerequisites).all()
    print(f"總共有 {len(prereqs)} 個前置關係")
    
    # 顯示前 10 個前置關係
    for p in prereqs[:10]:
        skill = db.session.get(SkillInfo, p.skill_id)
        prereq = db.session.get(SkillInfo, p.prerequisite_id)
        if skill and prereq:
            print(f"{prereq.skill_ch_name} → {skill.skill_ch_name}")
```

---

## 總結

知識圖譜視覺化功能已完整實作完成，整合了自適應學習系統的能力值計算（使用 `adaptive_config.py` 中的標準），提供了直觀的知識點關係展示。請按照上述手動測試指南進行驗證，如有任何問題或需要調整，請隨時告知。
