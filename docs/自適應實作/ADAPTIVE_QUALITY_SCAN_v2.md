# Adaptive Quality Scan v2

掃描時間：2026-03-26

掃描範圍：

- `jh_數學1上_FourArithmeticOperationsOfNumbers`
- `jh_數學1上_FourArithmeticOperationsOfIntegers`
- `jh_數學2上_FourArithmeticOperationsOfPolynomial`
- `jh_數學2上_FourOperationsOfRadicals`

掃描方式：

- 每個 `family_id` 生成 8 題
- 每個 family 額外保留 2 題人工審題樣本
- 共掃描 54 個 family
- 共檢查 432 題

`v2` 比 `v1` 多檢查的內容：

- 題目是否具有明確指令形狀
- family 類型與題幹語意是否一致
- 分數題是否符合 `化簡 / 填空 / 比較 / 倒數 / 文字題` 類型
- 整數題是否真的包含絕對值 / 括號 / 混合運算
- 多項式題是否含變數與展開/化簡語意
- 根式題是否真的含根號、是否對應有理化/展開等 family

結果摘要：

- `skills_scanned = 4`
- `families_scanned = 54`
- `samples_checked = 432`
- `issues_found = 0`
- `scan_version = v2`

結論：

目前這四個主 skill 在：

- 基本格式
- family 類型對位
- 教學題幹形狀
- 常見結構錯誤

這四個層次下，已通過 `v2` 掃描。

限制：

這不代表題目已達到最終論文展示品質。`v2` 仍然屬於規則化 QA，不會自動判斷：

- 哪個題幹比較像台灣國中教材
- 哪個 family 的例題更有教學價值
- 哪個題目難度更適合 C -> B 升級
- 哪個提示與 RAG 補救最搭

下一步建議：

- 建 `v3`：加入人工審題輸出頁
- 對每個 family 固定抽樣 3~5 題做人工教學品質 review
- 把低品質 family 列成優先修正清單
