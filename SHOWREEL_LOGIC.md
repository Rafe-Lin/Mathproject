# SHOWREEL_LOGIC

- 更新日期：2026-03-25
- 專案根目錄：`D:\Python\Mathproject`
- 用途：公司電腦與家中電腦之間的交接文件

## 1. 專案定位

這個專案目前已經不是單純的練習平台，而是把研究內容逐步落成可展示的自適應診斷系統。

核心方向如下：

- 平台主體留在 `Mathproject`
- `AST_Research` 負責 agent skill / live_show / prompt / healer / research toolkit
- `practice` 的 AI 助教目前改成可切換的 `qwen3-vl-8b`
- `adaptive_summative` 已成為本單元總結性診斷入口
- `live_show`、`MCRI`、`RAG`、`whiteboard` 都已接上

---

## 2. 今天的主要討論結論

### 2.1 專案合併原則

- `D:\Python\Mathproject` 是主平台與資料庫宿主
- `D:\Python\MathProject_AST_Research` 是 agent skill 與相關研究程式的真源
- `config.py` 不能直接覆蓋，必須保留原本模型與設定，只做增量調整
- 主資料庫固定使用 `D:\Python\Mathproject\instance\kumon_math.db`
- research-only 的研究表不進主庫，只留給即時建立的實驗 DB

### 2.2 研究內容落地方向

論文最終要落成三層：

1. 大腦層：AKT + PPO
2. 雙手層：Edge AI 微技能腳本
3. 嘴巴層：Hybrid RAG 補救提示

其中：

- `AKT + PPO` 目前是完整流程，但仍屬 heuristic / stub 版
- `微技能腳本` 已有 catalog -> manifest -> script 管線
- `Hybrid RAG` 已完成真檢索版，不再只是模板字串

### 2.3 使用者介面方向

`adaptive_summative` 的介面已經調成：

- 上方：三等分資訊區
  - 本單元學習導航
  - 系統導航狀態
  - 動態精熟軌跡圖
- 中下方：題目與作答、手寫計算紙
- 右側：AI 助教與 RAG 補救提示

目標是讓學生和評審一眼能看出：

- 這是診斷頁
- 不是 debug 頁
- RAG 只影響右側補救提示與手寫檢查摘要

---

## 3. 今天已完成的事項

### 3.1 自適應診斷頁

已完成的功能：

- `adaptive_summative` 可開啟
- 有題目與作答區
- 有手寫白板
- 有 AI 助教區
- 有動態精熟軌跡圖
- 有結束條件與診斷結論
- 有 `Local APR` 與策略顯示

### 3.2 結束邏輯

目前結束規則：

- 最多 8 題
- 至少完成 5 題後
- 若 `Local APR >= 0.65`，就可提前結束

結束時會顯示：

- 是否達標
- 最終 APR
- 作答題數
- 涉及 family
- 下一步建議

### 3.3 題目與手寫一致性

已修正：

- `/analyze_handwriting` 會帶目前畫面上的 `question_text`
- 會帶 `question_context`
- 會帶 `family_id`
- 會帶 `subskill_nodes`

這樣手寫檢查不會再講到上一題。

### 3.4 線上提示與助教

目前右側助教已調整為：

- 台灣國中生可懂的繁體中文
- 不直接報答案
- 只能引導
- Review 時會強化補救

### 3.5 RAG 真檢索層

已完成：

- 不再只是 stub
- 會根據 `subskill_nodes`
- 會看 `skill_id / family_id`
- 會看 `question_context / question_text`
- 會參考 `skill_breakpoint_catalog.csv`
- 會參考對應 `SKILL.md`
- 回傳簡單中文的：
  - 課本級提示
  - 常見錯誤
  - 例題
  - 下一步提醒

RAG 目前實際影響的地方：

- 右側補救提示
- 手寫檢查摘要

它不會改變題目本身。

### 3.6 微技能腳本工廠

已完成：

- `skill_breakpoint_catalog.csv -> manifest -> script`
- 整數四則已建立 `I1~I8` 的微技能出題模式
- `skills/adaptive` 已有生成結果
- `skill_manifest.json` 已能註冊 family 與腳本路徑

### 3.7 MCRI

已修復：

- 原本 `evaluate_mcri.py` 缺檔造成 fallback 分數
- 現在已重建可用版 evaluator
- 測試可通過

### 3.8 practice 助教

已調整為：

- 預設繁體中文
- 國中生看得懂
- 只能提示，不能直接給答案
- 標題會顯示目前使用的 model 名稱

---

## 4. 目前實作狀態總覽

### 4.1 已穩定可用

- `adaptive_summative`
- `live_show`
- `practice` AI 助教
- `MCRI evaluator`
- `RAG hint`
- `whiteboard`
- `trajectory` 繪圖
- `database` 主庫結構

### 4.2 仍在持續補強

- 真正的 AKT 模型
- 真正的 PPO agent
- 全單元微技能腳本補齊
- 更完整的課本知識庫
- 更完整的 family 規格化資料管理

---

## 5. 今天修改過的重點檔案

### 5.1 自適應診斷頁

- [templates/adaptive_practice_v2.html](D:/Python/Mathproject/templates/adaptive_practice_v2.html)

調整內容：

- 三等分上方區塊
- 系統導航狀態移到上方中間
- 動態精熟軌跡圖固定高度、可捲動
- 右側 AI 助教固定視窗、高度鎖定
- AI 助教加入 RAG 影響範圍提示
- 白板工具列改成單行 icon 風格
- 移除多餘按鈕，保留必要工具
- 完成時同步更新上方 APR
- 會把最後一題的最終 APR 補進軌跡圖

### 5.2 RAG 真檢索

- [core/adaptive/rag_hint_engine.py](D:/Python/Mathproject/core/adaptive/rag_hint_engine.py)
- [core/adaptive/session_engine.py](D:/Python/Mathproject/core/adaptive/session_engine.py)
- [core/routes/adaptive_api.py](D:/Python/Mathproject/core/routes/adaptive_api.py)

### 5.3 測試

- [tests/test_adaptive_rag_hint.py](D:/Python/Mathproject/tests/test_adaptive_rag_hint.py)

測試結果：

- `pytest -q tests/test_adaptive_rag_hint.py`
- `2 passed`

---

## 6. 論文三大部分 vs 目前實作完成度

| 論文支柱 | 論文理論要求 | 目前實作狀態 | 完成度 | 主要差距 / 下一步 |
|---|---|---|---|---|
| 大腦層：AKT + PPO | 用 AKT 追蹤 `subskill_nodes`，用 PPO 根據 `Local APR`、挫折感、歷史表現決定下一題與教學策略 | 已有完整診斷流程、`Local APR`、策略切換、結束條件、軌跡圖、log 紀錄；目前是 heuristic / stub 版，不是真 AKT/PPO | 中高 | 之後要把 heuristic stub 換成真正 AKT state update 與 PPO policy 推論 |
| 雙手層：Edge AI 微技能腳本 | 依 `skill_breakpoint_catalog.csv` 批次生成每個 `family_id` 的微技能出題腳本，穩定輸出 JSON 題目 | 已有 `catalog -> manifest -> micro skill script` 管線，整數四則已做出較完整的 `I1~I8` 微技能題；其他單元仍在補齊 | 中等 | 擴充到分數、多項式、根式等其餘 family，讓每個 family 都有穩定出題器 |
| 嘴巴層：Hybrid RAG 補救提示 | 根據 `subskill_nodes`、題目脈絡、課本/知識圖譜/SKILL.md，回傳課本級提示、例題、常錯點、下一步提醒 | 已接成真 Hybrid RAG：會依 `subskill_nodes + skill_id + family_id + question_context` 產生簡單中文提示，並作用在右側助教與手寫檢查摘要 | 高 | 後續可再加更完整的課本文字庫、知識圖譜節點管理、提示歷史紀錄 |

結論：

- RAG 最完整
- AKT/PPO 已有完整流程，但仍是工程化近似版
- 微技能工廠已成立，但尚未全單元鋪滿

---

## 7. 目前最重要的 UI / UX 結論

### 7.1 上方版面

現在上方是三等分：

- 本單元學習導航
- 系統導航狀態
- 動態精熟軌跡圖

這樣比原本左右不平衡的版本更舒服。

### 7.2 右側 AI 助教

目前已明確標示：

- RAG 只影響右側補救提示與手寫檢查摘要
- 不會直接改變題目本身
- 手動提問還是以引導式助教為主

### 7.3 手寫白板

目前保留：

- 畫筆
- 橡皮擦
- 顏色
- 筆寬
- 上一步 / 下一步
- 清空白板
- AI 檢查手寫

已移除：

- 繪製示意圖
- 上傳圖片

---

## 8. 今天觀察到的重點與限制

### 8.1 `RAG` 的影響範圍

目前 RAG 的作用範圍是：

- 右側補救提示
- 手寫檢查摘要

不是整個頁面。

### 8.2 `MCRI` 的定位

現在 MCRI 已能正常運作，但屬於可用的工程版，不是最終研究版。

### 8.3 `AKT / PPO`

目前是完整流程 + 工程近似版，還沒接真模型。

---

## 9. 待完成事項

### 短期

1. 把其他 `family_id` 的微技能腳本補齊
2. 讓 `adaptive_summative` 的題目更完整、更像真正診斷測驗
3. 進一步整理 `RAG` 的課本級提示來源
4. 把 `dashboard` 每個大單元的入口掛好

### 中期

5. 將 `AKT` 與 `PPO` 從 stub 升級為真模型接法
6. 建立更完整的 `family registry / manifest`
7. 建立更完整的研究輸出資料

### 長期

8. 讓論文系統成為可重現、可展示、可維護的完整產品

---

## 10. 回家後要怎麼接著做

你回家後，只要先看這份檔案，接著從這幾個檔案開始：

1. [SHOWREEL_LOGIC.md](D:/Python/Mathproject/SHOWREEL_LOGIC.md)
2. [templates/adaptive_practice_v2.html](D:/Python/Mathproject/templates/adaptive_practice_v2.html)
3. [core/adaptive/rag_hint_engine.py](D:/Python/Mathproject/core/adaptive/rag_hint_engine.py)
4. [core/adaptive/session_engine.py](D:/Python/Mathproject/core/adaptive/session_engine.py)
5. [core/routes/adaptive_api.py](D:/Python/Mathproject/core/routes/adaptive_api.py)

如果要從交接文件直接繼續，可以直接說：

> 請從 `SHOWREEL_LOGIC.md` 繼續，先處理 `adaptive_summative` 的下一步。

---

## 11. 最後一句

目前專案已經有：

- 可展示的 `adaptive_summative`
- 可展示的 `live_show`
- 可用的 `practice` 助教
- 真可用的 `RAG` 補救層
- 可用的 `MCRI`

接下來要做的不是重新開始，而是：

1. 補齊其餘微技能腳本
2. 強化 AKT / PPO 接法
3. 讓首頁入口與論文敘事完全一致
