# ✅ Benchmark 系統驗證報告
**日期:** 2026-02-17  
**狀態:** 🟢 全部就緒，可執行高分測試

---

## 📋 驗證摘要

### 1️⃣ 模型選擇菜單 ✅

**修正前問題:**
- 顯示 4 個模型（包含 legacy 的 qwen2.5-coder-14b）

**修正內容:**
- 在 [benchmark.py](../benchmark.py#L58-L93) 新增白名單過濾
- 只顯示 3 個主要實驗模型

**驗證結果:**
```
🤖 [模型選擇] 請選擇要使用的 AI 模型
======================================================================
   [1] ☁️  gemini-3-flash-preview (Gemini 3.0 Flash Preview)
   [2] 💻 qwen3-14b-nothink:latest (Qwen3-14B No-Think)
   [3] 💻 qwen3:8b (Qwen3-8B Thinking Allowed)
```

---

### 2️⃣ Ab1 Prompt 配置 ✅

**文件位置:**  
`agent_skills/jh_數學2上_FourOperationsOfRadicals/experiments/ab1_bare_prompt.md`

**關鍵修正 (已完成):**
- ✅ 明確要求 `check()` 函數必須回傳字典
- ✅ 絕對禁止中文註解和標點符號
- ✅ 禁止任何說明文字、只輸出純代碼

**驗證結果:**
```
✓ 包含 check() 函數格式要求
✓ 包含中文註解禁令
```

---

### 3️⃣ Ab2/Ab3 Prompt 配置 ✅

**文件位置:**  
`agent_skills/jh_數學2上_FourOperationsOfRadicals/SKILL.md`

**關鍵修正 (已完成):**
- ✅ 明確 `check()` 函數格式（回傳 dict）
- ✅ 修正 `is_first` 參數用法：`(len(terms)==0)` 而非 `bool(terms)`
- ✅ 修正 `format_expression` 參數：傳入 `{radicand: coeff}` 字典
- ✅ 提供完整正確範例代碼
- ✅ 新增檢查清單 (Checklist)

**驗證結果:**
```
✓ 包含 is_first 正確用法說明
✓ 包含 format_expression 正確用法說明
✓ 包含中文註解禁令
```

---

### 4️⃣ Healer 流程驗證 ✅

**Ab1 (Bare - 原生能力測試):**
```python
healed_code = raw_code  # 無任何修復
```

**Ab2 (Engineered + Minimal Healer):**
```python
healed_code, stats = regex_healer.heal_minimal(raw_code)
healed_code = build_calculation_skeleton(skill_name) + "\n" + healed_code
healed_code, _ = _inject_domain_libs(healed_code)
```

**Ab3 (Full Healing - 完整系統):**
```python
temp_code, r_fixes = regex_healer.heal(raw_code)       # Regex 修復
healed_code, a_fixes = ast_healer.heal(temp_code)      # AST 修復
healed_code = build_calculation_skeleton(skill_name) + "\n" + healed_code
healed_code, _ = _inject_domain_libs(healed_code)
```

**驗證結果:**
```
✅ RegexHealer.heal_minimal() 可用 (Ab2)
✅ RegexHealer.heal() 可用 (Ab3)
✅ ASTHealer.heal() 可用 (Ab3)
```

---

### 5️⃣ 測試用例配置 ✅

**文件位置:**  
`agent_skills/jh_數學2上_FourOperationsOfRadicals/evals.json`

**測試分佈:**
- Ab1: 2 個測試用例
- Ab2: 4 個測試用例
- Ab3: 4 個測試用例
- **總計:** 10 個測試用例

---

## 🎯 預期結果

### 分數預測

**Ab1 (Bare):**
- 預期 Program Score: 20-30/50
- 預期 Math Score: 0-10/50 (可能因中文註解、check() 格式錯誤失分)
- **Total: 20-40/100**

**Ab2 (Engineered + Minimal):**
- 預期 Program Score: 40-45/50
- 預期 Math Score: 40-48/50 (SKILL.md 明確規範應大幅提升)
- **Total: 80-93/100** ⭐

**Ab3 (Full Healing):**
- 預期 Program Score: 48-50/50 (AST 修復保證)
- 預期 Math Score: 45-50/50 (完整修復 + 規範)
- **Total: 93-100/100** ⭐⭐

---

## 🚀 執行方式

### 命令行執行
```bash
cd E:\Python\MathProject_AST_Research
python agent_tools/benchmark.py
```

### 互動式選單流程
1. **選擇 Skill:**  
   `[1] jh_數學2上_FourOperationsOfRadicals`

2. **選擇 Ablation:**  
   `[0] Run All Ablations` (Ab1 + Ab2 + Ab3)

3. **設定重複次數:**  
   建議 `1` (每個測試生成 1 次)

4. **選擇模型:**  
   - [1] Gemini 3.0 Flash (最快，雲端)
   - [2] Qwen3-14B (高品質，本地)
   - [3] Qwen3-8B (平衡，本地)

5. **執行測試**  
   系統自動運行並生成報表

---

## 📊 輸出檔案

### 測試代碼 (temp_code/)
```
agent_tools/temp_code/
├── {eval_id}_gen1_{timestamp}_raw.txt          # AI 原始輸出
├── {eval_id}_gen1_{timestamp}_extracted.py     # 提取的代碼
└── {eval_id}_gen1_{timestamp}_healed.py        # 修復後代碼
```

### 評分報表 (reports/)
```
agent_tools/reports/
├── benchmark_{timestamp}.db                    # SQLite 資料庫
├── experiment_runs_{timestamp}.csv             # 詳細分數
├── evaluation_items_{timestamp}.csv            # L1-L5 逐項評分
└── ablation_summary_{timestamp}.csv            # 統計摘要
```

---

## ✅ 確認清單

- [x] 模型選擇菜單顯示正確（3 個模型）
- [x] Ab1 Prompt 包含 check() 格式要求
- [x] Ab1 Prompt 禁止中文註解
- [x] Ab2/Ab3 Prompt 正確說明 is_first 用法
- [x] Ab2/Ab3 Prompt 正確說明 format_expression 用法
- [x] Ab2 使用 heal_minimal() 
- [x] Ab3 使用 heal() + AST
- [x] evals.json 包含 10 個測試用例
- [x] benchmark.py 正確讀取對應 Prompt
- [x] 輸出目錄已設定為 agent_tools/temp_code/

---

## 🎓 實驗設計邏輯

### Ab1 → Ab2 (證明 Prompt 工程的價值)
- **變因:** 從簡單 Prompt → 結構化 SKILL.md
- **期望:** Math Score 從 0-10 提升到 40-48
- **結論:** 證明「工程化 Prompt」可大幅提升正確率

### Ab2 → Ab3 (證明 Healer 的價值)
- **變因:** 從輕量級修復 → 完整 Regex + AST 修復
- **期望:** Program Score 從 40-45 提升到 48-50
- **結論:** 證明「自動修復系統」可保證程式正確性

---

**🎯 系統已就緒，可開始執行高分測試！**
