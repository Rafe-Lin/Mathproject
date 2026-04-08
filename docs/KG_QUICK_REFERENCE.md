# 快速參考 - 知識圖譜 JSON 版本

## 🎯 快速開始

### 1️⃣ 查看現有知識圖譜

打開瀏覽器訪問:
```
http://localhost:5000/knowledge-graph
```

### 2️⃣ 生成靜態 HTML

```bash
# 整個年級
python scripts/generate_kg_visualization.py --grade 國一上

# 特定單元
python scripts/generate_kg_visualization.py --grade 國一上 --unit JH_NUM_INT_NL

# 全部生成 (所有年級和單元)
python scripts/generate_kg_visualization.py --all
```

### 3️⃣ 在代碼中使用

```python
from core.kg_data_loader import get_kg_loader

loader = get_kg_loader()

# 獲取所有年級
grades = loader.get_all_grades()

# 獲取圖譜數據
graph = loader.get_graph_data('國一上', 'JH_NUM_INT_NL')
# → {'nodes': [...], 'links': [...]}

# 搜尋
results = loader.search_nodes('國一上', '正負數')
```

---

## 📋 新文件列表

| 文件 | 說明 | 用途 |
|------|------|------|
| `core/kg_data_loader.py` | JSON 加載器 | 核心數據模塊 |
| `scripts/generate_kg_visualization.py` | HTML 生成器 | 靜態生成 |
| `docs/KG_JSON_USAGE_GUIDE.md` | 詳細文檔 | 學習參考 |
| `test_kg_loader.py` | 測試腳本 | 驗證功能 |

---

## 🔄 修改文件列表

| 文件 | 改動 | 主要變化 |
|------|------|---------|
| `core/routes/knowledge_graph.py` | V1.0 → V2.0 | 改為 JSON 查詢，移除數據庫 |
| `templates/knowledge_graph.html` | V1.0 → V2.0 | 更新 UI 和 API 調用 |

---

## 📊 API 端點速覽

```bash
# 獲取圖譜數據
GET /api/knowledge-graph/data?grade=國一上[&unit_id=JH_NUM_INT_NL]

# 獲取篩選選項
GET /api/knowledge-graph/filters[?grade=國一上]

# 搜尋
GET /api/knowledge-graph/search?grade=國一上&keyword=正負數

# 統計
GET /api/knowledge-graph/statistics?grade=國一上[&unit_id=JH_NUM_INT_NL]
```

---

## ✅ 驗證清單

- [x] JSON 加載器完成
- [x] 後端 API 改造
- [x] 前端頁面更新
- [x] 靜態生成腳本
- [x] 完整文檔
- [x] 測試驗證
- [x] 所有測試通過 ✓

---

## 🎨 數據結構一覽

### 節點示例
```json
{
  "id": "JH_NUM_INT_NL_L3_01",
  "level": "L3",
  "name": "正負數的引入與意義",
  "parent_id": "JH_NUM_INT_NL",
  "description": "...",
  "difficulty": 1
}
```

### 連接示例
```json
{
  "source": "JH_NUM_INT_NL",
  "target": "JH_NUM_INT_NL_L3_01"
}
```

### 階級說明
- **L0**: 教育階段 (如 "國中")
- **L1**: 領域 (如 "數與量")
- **L2**: 單元 (如 "整數與數線")
- **L3**: 主題 (如 "正負數的引入")
- **L4**: 次主題 (具體知識點)

---

## 🐛 快速故障排除

| 問題 | 解決方案 |
|------|---------|
| 年級顯示為空 | 檢查 `kg_outputs/` 目錄是否存在 |
| 圖譜顯示異常 | 打開瀏覽器開發工具查看控制臺錯誤 |
| HTML 生成失敗 | 確保 `outputs/` 目錄存在且有寫入權限 |
| JSON 解析錯誤 | 該檔案會被跳過，加載器會繼續運行 ✓ |

---

## 📚 完整文檔

- **詳細指南**: `docs/KG_JSON_USAGE_GUIDE.md`
- **遷移總結**: `docs/KG_MIGRATION_SUMMARY.md`

---

## 💡 常用操作

### 更新 JSON 數據
新的 JSON 檔案放入 `kg_outputs/[年級]/` 後，重啟應用

### 批量生成報告
```bash
for grade in 國一上 國一下 國二上 國二下; do
  python scripts/generate_kg_visualization.py --grade "$grade"
done
```

### 查看統計信息
```bash
curl "http://localhost:5000/api/knowledge-graph/statistics?grade=國一上"
```

---

**最後更新**: 2026-04-07  
**狀態**: ✅ 完成並驗證
