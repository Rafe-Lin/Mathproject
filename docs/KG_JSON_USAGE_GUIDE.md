# 知識圖譜 JSON 版本 - 使用指南

## 概述

這是一個全新的知識圖譜可視化系統，改為基於 `kg_outputs` 目錄中的 JSON 文件。相比之前直接從數據庫查詢，新系統具有以下優勢：

- ✅ **無數據庫依賴**：完全獨立運作，可離線使用
- ✅ **快速加載**：JSON 文件提前加載至內存，查詢速度快
- ✅ **易於維護**：JSON 文件結構清晰，便於編輯和版本控制
- ✅ **靈活擴展**：支持生成靜態 HTML 文件，可在任何環境展示

## 文件結構

```
core/
├── kg_data_loader.py          # JSON 數據加載器（核心模塊）
└── routes/
    └── knowledge_graph.py      # 更新的路由層（使用 JSON 數據）

scripts/
└── generate_kg_visualization.py  # 靜態 HTML 生成腳本

templates/
└── knowledge_graph.html        # 升級的前端界面

kg_outputs/
├── 國一上/
│   ├── all_units.json
│   ├── JH_NUM_INT_NL.json
│   ├── JH_NUM_FRAC_OPS.json
│   └── ...
├── 國一下/
│   ├── all_units.json
│   └── ...
└── ...
```

## 核心模塊說明

### 1. `core/kg_data_loader.py` - KGDataLoader 類

這是核心模塊，負責加載和查詢 JSON 數據。

#### 主要方法：

```python
from core.kg_data_loader import get_kg_loader

kg_loader = get_kg_loader()

# 獲取所有年級
grades = kg_loader.get_all_grades()
# ['國一上', '國一下', '國二上', '國二下']

# 獲取特定年級的所有單元
units = kg_loader.get_units_for_grade('國一上')
# {'JH_NUM_INT_NL': {...}, 'JH_NUM_FRAC_OPS': {...}, ...}

# 獲取特定單元的完整資料
unit_data = kg_loader.get_unit_data('國一上', 'JH_NUM_INT_NL')

# 獲取圖譜資料（節點和連接）
graph_data = kg_loader.get_graph_data('國一上', 'JH_NUM_INT_NL')
# {'nodes': [...], 'links': [...]}

# 搜尋功能
results = kg_loader.search_nodes('國一上', '正負數')

# 獲取難度分佈統計
difficulty_dist = kg_loader.get_difficulty_distribution('國一上')
# {1: 15, 2: 30, 3: 5}
```

## 後端 API 使用

### 1. 獲取知識圖譜數據

**端點**：`GET /api/knowledge-graph/data`

**參數**：
- `grade` (必需)：年級名稱，如 `國一上`
- `unit_id` (可選)：單元 ID，如 `JH_NUM_INT_NL`

**示例**：
```bash
# 獲取整個國一上年級的圖譜
curl "http://localhost:5000/api/knowledge-graph/data?grade=國一上"

# 獲取特定單元的圖譜
curl "http://localhost:5000/api/knowledge-graph/data?grade=國一上&unit_id=JH_NUM_INT_NL"
```

**返回**：
```json
{
  "nodes": [
    {
      "id": "L0_JH",
      "level": "L0",
      "name": "國中",
      "parent_id": null
    },
    {
      "id": "JH_NUM_INT_NL_L3_01",
      "level": "L3",
      "name": "正負數的引入與意義",
      "parent_id": "JH_NUM_INT_NL",
      "description": "...",
      "difficulty": 1
    },
    ...
  ],
  "links": [
    {"source": "L0_JH", "target": "L1_JH_NUM"},
    {"source": "JH_NUM_INT_NL", "target": "JH_NUM_INT_NL_L3_01"},
    ...
  ]
}
```

### 2. 獲取篩選選項

**端點**：`GET /api/knowledge-graph/filters`

**參數**：
- `grade` (可選)：年級名稱

**示例**：
```bash
# 獲取所有可用的年級
curl "http://localhost:5000/api/knowledge-graph/filters"

# 獲取特定年級的所有單元
curl "http://localhost:5000/api/knowledge-graph/filters?grade=國一上"
```

**返回**：
```json
{
  "grades": ["國一上", "國一下", "國二上", "國二下"]
}
```

或

```json
{
  "units": ["JH_NUM_INT_NL", "JH_NUM_FRAC_OPS", "JH_NUM_INT_ALG"]
}
```

### 3. 搜尋功能

**端點**：`GET /api/knowledge-graph/search`

**參數**：
- `grade` (必需)：年級名稱
- `keyword` (必需)：搜尋關鍵字
- `unit_id` (可選)：限制在特定單元內搜尋

**示例**：
```bash
curl "http://localhost:5000/api/knowledge-graph/search?grade=國一上&keyword=正負數"
```

### 4. 統計信息

**端點**：`GET /api/knowledge-graph/statistics`

**參數**：
- `grade` (必需)：年級名稱
- `unit_id` (可選)：單元 ID

**返回**：
```json
{
  "difficulty_distribution": {1: 15, 2: 30, 3: 5},
  "total_nodes": 150,
  "total_links": 120
}
```

## 前端頁面

### 知識圖譜頁面（`/knowledge-graph`）

這是主要的交互式界面，提供：

1. **年級選擇**：下拉菜單選擇要查看的年級
2. **單元選擇**：可選的單元篩選
3. **互動式圖譜**：
   - 支持縮放和拖拽
   - 鼠標懸停顯示節點詳情
   - 根據階級（L0-L4）使用不同顏色

## 靜態 HTML 生成

### 使用腳本生成靜態 HTML

可以使用 `scripts/generate_kg_visualization.py` 根據 JSON 文件生成靜態 HTML 文件。

#### 安裝依賴

```bash
pip install -r requirements.txt
```

#### 生成單個年級

```bash
python scripts/generate_kg_visualization.py --grade 國一上
# 生成: outputs/kg_國一上_all.html
```

#### 生成特定單元

```bash
python scripts/generate_kg_visualization.py --grade 國一上 --unit JH_NUM_INT_NL
# 生成: outputs/kg_國一上_JH_NUM_INT_NL.html
```

#### 生成所有年級和單元

```bash
python scripts/generate_kg_visualization.py --all
# 生成所有組合的 HTML 文件
```

#### 自定義輸出目錄

```bash
python scripts/generate_kg_visualization.py --all --output-dir custom_outputs/
```

### 生成的 HTML 功能

生成的靜態 HTML 文件包含：

- 📊 節點和連接的交互式 D3 圖表
- 🎨 根據階級自動配色
- 📈 難度分佈直方圖
- 🔍 Tooltip 節點詳情
- 🖱️ 拖拽和縮放功能
- 📝 完整的知識點描述

## 數據結構說明

### JSON 文件格式

#### al_units.json (合併文件)

```json
{
  "units": [
    {
      "unit_info": {
        "l0_grade": "國中",
        "l1_domain": "數與量",
        "l2_unit": "整數與數線",
        "l2_unit_id": "JH_NUM_INT_NL"
      },
      "nodes": [
        {
          "id": "JH_NUM_INT_NL_L3_01",
          "level": "L3",
          "name": "正負數的引入與意義",
          "parent_id": "JH_NUM_INT_NL",
          "description": "...",
          "difficulty": 1
        }
      ]
    }
  ]
}
```

#### 單個單元 JSON

```json
{
  "unit_info": {
    "l0_grade": "國中",
    "l1_domain": "數與量",
    "l2_unit": "整數與數線",
    "l2_unit_id": "JH_NUM_INT_NL"
  },
  "nodes": [...]
}
```

### 節點階級說明

- **L0**：教育階段（如 "國中"）
- **L1**：領域（如 "數與量"）
- **L2**：單元（如 "整數與數線"）
- **L3**：主題（如 "正負數的引入與意義"）
- **L4**：次主題（如 "以正負符號表示相反的量"）

## 性能優化

### 數據加載

- 所有 JSON 文件在第一次調用 `get_kg_loader()` 時被加載至內存
- 後續查詢直接從內存讀取，無需磁盤 I/O
- 支持多個單位級別的查詢快速返回結果

### 快取機制

```python
# 使用全局加載器（單例）
from core.kg_data_loader import get_kg_loader
kg_loader = get_kg_loader()  # 只加載一次
```

## 故障排除

### JSON 文件找不到

確保 `kg_outputs` 目錄存在於項目根目錄：

```
Mathproject/
├── core/
├── kg_outputs/    ← 必須存在
│   ├── 國一上/
│   └── ...
└── app.py
```

### 年級名稱不符

確保使用正確的年級名稱。查看 `kg_outputs` 目錄中實際的文件夾名稱：

```bash
ls kg_outputs/
# 國一上
# 國一下
# 國二上
# 國二下
```

### 前端加載失敗

1. 檢查瀏覽器控制檯錯誤信息
2. 驗證後端 API 是否返回正確數據：

```bash
curl http://localhost:5000/api/knowledge-graph/filters
```

3. 確保使用了正確的年級和單元名稱

## 擴展和定制

### 添加新的 JSON 源

如果需要添加新的 JSON 文件：

1. 將 JSON 文件放在對應的 `kg_outputs/[年級]/` 目錄中
2. 文件會自動被 `KGDataLoader` 加載
3. 重啟應用程序以使更改生效

### 自定義顏色方案

在 HTML 或 JavaScript 中修改顏色映射：

```javascript
// 修改節點顏色
function getNodeColor(level) {
    const colorMap = {
        'L0': '#自定義顏色',
        'L1': '#自定義顏色',
        // ...
    };
    return colorMap[level] || '#默認顏色';
}
```

### 添加自定義統計功能

在 `KGDataLoader` 中添加新方法：

```python
def get_custom_statistics(self, grade: str) -> Dict:
    """自定義統計函數"""
    # 實現自定義邏輯
    return {...}
```

## API 變更日誌

### V2.0 (2026-04-07)

- ✅ 改為完全基於 JSON 文件
- ✅ 移除數據庫依賴
- ✅ 簡化篩選器（年級 + 單元）
- ✅ 添加搜尋和統計 API
- ✅ 增加靜態 HTML 生成功能
- ✅ 改進的階級顏色配色

### V1.0 (2026-01-31)

- 初始版本，使用數據庫查詢

## 許可和使用條款

本模塊作為自適應學習系統的一部分，遵循相同的許可條款。

---

**最後更新**：2026-04-07
**維護者**：Math AI Project Team
