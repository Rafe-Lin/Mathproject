# Adaptive Quality Scan v1

掃描時間：2026-03-26

掃描範圍：

- `jh_數學1上_FourArithmeticOperationsOfNumbers`
- `jh_數學1上_FourArithmeticOperationsOfIntegers`
- `jh_數學2上_FourArithmeticOperationsOfPolynomial`
- `jh_數學2上_FourOperationsOfRadicals`

掃描方式：

- 每個 `family_id` 生成 8 題
- 共掃描 54 個 family
- 共檢查 432 題

目前 v1 掃描器檢查的內容：

- 題幹是否缺失
- 答案是否缺失
- 是否含 `???` / placeholder
- 是否含控制字元
- 是否仍出現 stub answer marker
- `Fill-Blank` 題是否真的有空格
- `Simplification` 題是否已經先被化簡
- `Comparison` 題答案是否為 `> < =`

結果摘要：

- `skills_scanned = 4`
- `families_scanned = 54`
- `samples_checked = 432`
- `issues_found = 0`

判讀：

這份 `v1` 結果代表目前四個主 skill 在「基本結構」上已通過第一輪掃描。
它不代表所有題目都已達到教學品質最佳化，只代表：

- 沒再掃到明顯壞字串
- 沒再掃到已化簡卻要求化簡
- 沒再掃到假填空題
- 沒再掃到空答案或 stub 標記

限制：

`v1` 還沒做這些較深層的檢查：

- 題幹是否符合台灣國中國語敘事
- 題意是否自然
- 題目是否過於簡單或過於怪異
- 題目與 `subskill_nodes` 的教學對位是否最佳
- 題目與 RAG 提示是否真正一致

下一步建議：

做 `v2` 掃描器，加入：

- 題幹語意規則
- 題型難度分布
- family 與 subskill 的語意對位檢查
- 答案判題回歸測試
- 抽樣輸出題庫供人工審題
