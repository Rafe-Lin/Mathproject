# 自適應診斷正式產品規格 v1

## 一、產品定位
「本單元自適應學習（總結性診斷）」配置於每個大單元練習的最後，作為論文版自適應學習系統的正式前台產品。

它不是一般練習頁，也不是單純 API demo，而是：

- 像一次完整綜合測驗
- 題目會依學生表現動態調整
- 卡關時會自動啟動補救提示
- 最後產出可解釋的診斷結果

## 二、核心目標
1. 用 `family_id` 做題型層級診斷。
2. 用 `subskill_nodes` 做微技能層級追蹤。
3. 用 `AKT` 更新 `Local APR`。
4. 用 `PPO` 決定下一題與教學策略。
5. 用 `Hybrid RAG` 在 `Review` 時提供補救提示。
6. 全程寫入 `adaptive_learning_logs` 供論文分析。

## 三、使用情境
入口位置：

- 每個大單元最後新增按鈕：`本單元自適應學習（總結性診斷）`

使用流程：

1. 學生完成單元一般練習。
2. 點入自適應診斷。
3. 系統建立 `session_id`。
4. 開始一題一題動態測驗。
5. 若連錯或 APR 過低，自動切入補救策略。
6. 完成後顯示診斷報告與建議。

## 四、頁面規格
頁面名稱：

- `adaptive_practice_v2.html`
- 最終可命名為 `adaptive_summative.html`

頁面區塊：

1. 頂部資訊列
   - 單元名稱
   - 診斷狀態
   - session id
   - step number
   - Local APR
   - PPO strategy
   - frustration index

2. 主題目區
   - 題目文字 / LaTeX
   - 圖形或視覺輔助
   - family_id 顯示
   - subskill_nodes 顯示

3. 作答區
   - 文字輸入框
   - 題型需要時可擴充成單選或多欄位輸入
   - `送出答案` 按鈕
   - 送出後自動進入下一題

4. AI 助教區
   - 可手動提問
   - 可自動顯示 Review 補救提示
   - 回答一律繁中、國中生可懂、只能引導不能直接講答案

5. 軌跡視覺化區
   - Mastery Trajectory
   - X 軸：step
   - Y 軸：Local APR
   - 達標線：0.65
   - `ppo_strategy == 3` 時加標記

6. 診斷報告區
   - 完成後顯示 mastery 變化
   - 常錯 subskills
   - 是否進入 Review
   - 建議補強方向

## 五、出題系統規格
資料源：

- [skill_breakpoint_catalog.csv](/D:/Python/Mathproject/docs/自適應實作/skill_breakpoint_catalog.csv)

原則：

- 每個 `family_id` 都應對應一支微技能 Python 腳本
- 不可只靠大單元 `generate()` 混用

腳本位置建議：

- `skills/micro/`
- 或 `skills/adaptive/`

每支腳本輸出 JSON 至少包含：

```json
{
  "question": "題目文字",
  "latex": "LaTeX 題目",
  "answer": "標準答案",
  "family_id": "p5b",
  "subskill_nodes": ["divide_terms", "conjugate_rationalize"]
}
```

必要文件：

- `skill_manifest.json`

內容至少包含：

- `family_id`
- `skill_id`
- `script_path`
- `subskill_nodes`
- `version`
- `model_name`
- `healer_applied`

## 六、決策引擎規格
1. AKT
   - 輸入：上一題 `subskill_nodes`、`is_correct`、歷史作答序列
   - 輸出：`Local APR`

2. PPO
   - 輸入：`Local APR`、`frustration_index`、`step_number`、已走過 family
   - 輸出：`target_family_id`、`ppo_strategy`

策略編碼固定：

- `0 = Max-Fisher`
- `1 = ZPD`
- `2 = Diversity`
- `3 = Review`

## 七、RAG 規格
API：

- `GET /api/adaptive/rag_hint`

觸發條件：

- `ppo_strategy == 3`
- 或學生手動按「查看提示」

檢索來源：

1. 知識圖譜節點
2. 課本文本
3. `SKILL.md` 解題步驟

輸出：

- `hint_html`

要求：

- 有根據
- 不空泛
- 以當前 `subskill_nodes` 為核心

## 八、後端 API 規格
1. `POST /api/adaptive/submit_and_get_next`
   - 輸入：`student_id`、`session_id`、`step_number`、`user_answer`、`skill_id` 或 `unit_skill_ids`
   - 內部流程：判題、更新 AKT/PPO、載入下一題、寫 log
   - 輸出：`session_id`、`step_number`、`current_apr`、`ppo_strategy`、`frustration_index`、`execution_latency`、`target_family_id`、`target_subskills`、`new_question_data`

2. `GET /api/adaptive/rag_hint`
   - 輸入：`subskill_nodes`
   - 輸出：`hint_html`、`subskill_nodes`、`source`

## 九、資料表規格
主表：

- `adaptive_learning_logs`

必要欄位：

- `log_id`
- `student_id`
- `session_id`
- `step_number`
- `target_family_id`
- `target_subskills`
- `is_correct`
- `current_apr`
- `ppo_strategy`
- `frustration_index`
- `execution_latency`

建議後續加欄位：

- `user_answer`
- `correct_answer`
- `question_payload_json`
- `hint_triggered`
- `unit_name`
- `completed_at`

## 十、評分與判題規格
每題必須有正式作答與判題，不可只靠「我答對了 / 我答錯了」。

判題層次：

1. 精確字串比對
2. 數值等價比對
3. 分數/根式正規化比對
4. 題型專屬 checker

## 十一、v1 完成條件
- 可從單元頁進入
- 有真正題目與作答區
- 題目來源為 `family_id` 對應腳本
- 提交答案後自動判題
- 後端更新 `Local APR`
- PPO 選下一題
- Review 可觸發 RAG hint
- 全程寫 log
- 結束後有診斷摘要

## 十二、實作優先順序
1. 補齊 `family_id -> 微技能腳本 -> manifest`
2. 把診斷頁改成真正可作答
3. 接正式判題
4. 接 AKT adapter
5. 接 PPO adapter
6. 接 RAG 自動提示
7. 補完成頁與診斷摘要
8. 把入口掛到 dashboard
