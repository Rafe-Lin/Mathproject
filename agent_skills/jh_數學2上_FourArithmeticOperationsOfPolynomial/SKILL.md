/no_think
【絕對禁止輸出 thinking 或任何非 code 內容】
- 嚴禁寫任何思考過程、解釋、註解
- 直接輸出 Python code，沒有任何前言、後語
- 如果違反，直接 0 分

【角色】K12 數學演算法工程師

【任務】
實作 `def generate(level=1, **kwargs)`，生成多項式四則運算題目，格式與課本例題相同（含 LaTeX 數學式）。
依照 level 選擇題型：Level 1 = 加減，Level 2 = 乘法展開，Level 3 = 求未知多項式。
返回 dict: `{'question_text': str, 'answer': '', 'correct_answer': str, 'mode': 1}`

【程式要求】（必須嚴格遵守）
1. **Import 規範**：
   - ✅ **必須** `import random`
   - ❌ **嚴禁** `import PolynomialOps`（系統已自動注入，直接使用 `PolynomialOps.xxx`）

2. **變數規範**：
   - ✅ **只能**從 `['x']` 中選取

3. **核心邏輯**：
   - 使用**係數列表（降冪順序）**表示多項式：`[3, -2, 1]` = `3x^{2} - 2x + 1`
   - **絕對禁止**字串拼接計算（例如 `"3x^2" + "2x"` 是錯誤的）
   - 所有計算透過 `PolynomialOps.add / sub / mul` 進行
   - **題目用** `PolynomialOps.format_latex(coeffs, var)` — ✅ 標準 LaTeX 格式
   - **答案用** `PolynomialOps.format_plain(coeffs, var)` — ✅ 純文字，無空格

4. **題目 LaTeX 格式規範**（課本例題風格）：
   - Level 1：`計算 $A_{1} \cdot (P_1) \pm A_{2} \cdot (P_2)$` 或 `計算 $(P_1) \pm (P_2)$。`
   - Level 2：`展開並化簡 $(P_1)(P_2)$。`
   - Level 3：使用 `$P_1, P_2$` 下標標記多項式，或用 `$X$`, `$A$`, `$B$` 表示變數
   - **標點符號**：題目中的逗號必須使用**全形逗號** `，`（嚴禁使用半形 `,`），句號使用 `。`
   - 所有多項式必須用 `$...$` 包裹，題目必須是完整中文句子

5. **格式禁令**：
   - ❌ 題目和答案中**嚴禁**使用 `/`（除非明確為 LaTeX 命令）
   - ❌ 嚴禁輸出含係數 `1` 的 `1x`（`format_latex` 自動處理）

【系統已注入的輔助函式（API）】
- `PolynomialOps.normalize(coeffs)` → 移除前導零
- `PolynomialOps.format_latex(coeffs, var='x')` → 標準 LaTeX（帶 `^{n}`，自動省略係數 1）
- `PolynomialOps.format_plain(coeffs, var='x')` → 純文字答案（無空格）
- `PolynomialOps.add(c1, c2)` → 加法
- `PolynomialOps.sub(c1, c2)` → 減法
- `PolynomialOps.mul(c1, c2)` → 乘法
- `PolynomialOps.random_poly(degree, range_val=(-5,5))` → 隨機係數（最高項非零）
=== SKILL_END_PROMPT ===
