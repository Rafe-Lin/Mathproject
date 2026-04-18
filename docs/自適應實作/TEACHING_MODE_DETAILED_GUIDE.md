# Teaching Mode 詳細說明

更新日期: 2026-04-05  
專案: `C:\github\Mathproject`  
範圍: `adaptive_summative` 中的 `mode=teaching` 流程  
對應單元: 目前以 `jh_數學2上_FourArithmeticOperationsOfPolynomial` 為主要實作觀察對象

---

## 1. 文件目的

這份文件用來說明目前系統中 `teaching mode` 的實際運作方式，重點回答以下問題：

1. 教學模式從哪裡開始
2. 教學模式如何選題
3. 什麼情況會切到補救
4. 補救完成後如何回主線
5. 什麼情況下整個 teaching mode 會結束
6. 它和 assessment mode 目前的關係是什麼

本文件以**現行程式實作**為準，不描述尚未落地的理想流程。

---

## 2. 教學模式在整體架構中的位置

依專案目前 guardrails，三層責任如下：

1. `progression`: 控制教材主線順序與 prerequisite intent
2. `routing`: 控制 PPO action 與 skill/subskill 路由
3. `remediation`: 控制診斷提示與 bridge candidate retrieval

`teaching mode` 不是單純出題模式，而是這三層共同作用的「教學導航模式」：

1. progression 決定目前單元主線 family 順序
2. routing 判斷是否維持主線、切補救、或從補救返回
3. remediation 在學生卡住時協助找出較合理的補強子技能與提示來源

換句話說，teaching mode 的本質不是固定題庫練習，而是：

`主線檢核 -> 發現卡點 -> 補救 -> 回主線 -> 再檢核`

---

## 3. 入口與初始化

### 3.1 入口頁

學生從 `adaptive_learning_entry.html` 選擇單元後，可點選：

1. `assessment`
2. `teaching`

前端會把以下參數帶進 `adaptive_summative`：

1. `skill_id`
2. `unit_name`
3. `mode`

對 teaching mode 而言，進頁時只知道：

1. 現在是哪一個單元
2. 現在是 `mode=teaching`

### 3.2 teaching mode 啟動時的狀態

進入 teaching mode 後，前端初始 state 會以新 session 角度開始，包含：

1. `learningMode = "main"`
2. `mode = "teaching"`
3. `assessmentCompleted = false`
4. `unitCompleted = false`
5. `localRemediationCompleted = false`

也就是說，teaching mode 目前預設是**從教學主線重新起跑**，而不是自動承接前一次 assessment 的卡點。

---

## 4. 教學模式的主線流程

### 4.1 每回合提交 API

teaching mode 的核心 API 是：

`POST /api/adaptive/submit_and_get_next`

每一輪送出作答後，後端會做以下幾件事：

1. 讀取目前 session 的 routing state
2. 根據前一題答對或答錯更新 Local APR
3. 更新 family-level performance
4. 檢查是否需要補救
5. 決定下一題仍在主線、切去補救、或從補救返回
6. 回傳新的題目與狀態摘要

### 4.2 主線題目依教材順序推進

teaching mode 不是任意抽 family，而是優先依 textbook progression 的 mainline sequence 走。

以多項式四則運算目前配置為例：

1. `F1`
2. `F2`
3. `F5`
4. `F11`

這代表 teaching mode 的預設目標是：

1. 先檢核主線核心 family
2. 依表現決定是否進下一個 family
3. 如果卡住，再進補救支線

### 4.3 教學模式每題都會累積的狀態

每題作答後，系統會持續更新：

1. `current_apr`
2. `fail_streak`
3. `frustration_index`
4. `family_performance`
5. `routing_state`
6. `routing_summary`
7. `routing_timeline`

所以 teaching mode 是一個**連續狀態機**，不是每一題彼此獨立。

---

## 5. 什麼情況會切到補救

### 5.1 補救不是一開始就啟動

teaching mode 預設先留在主線，不會一進來就直接補救。

只有在系統認為學生在某個 family 上出現穩定卡點時，才會把 `remediation_review_ready` 打開。

### 5.2 目前常見補救觸發訊號

當下列情況出現時，系統較可能認定補救已準備好：

1. 同一 family 連續答錯達到門檻
2. 整體 fail streak 達到門檻
3. `frustration_index` 升高
4. 某些特定錯誤訊號出現

以多項式單元現有 progression rules 為例：

1. `success_to_next_after_n_correct: 1`
2. `stay_on_same_family_after_n_wrong: 1`
3. `remediation_trigger_after_consecutive_wrong: 2`
4. `fallback_to_previous_family_if_no_remediation: true`

這表示：

1. 同一 family 做對 1 題即可往下一個 family
2. 同一 family 一錯就先停留觀察
3. 連續錯到 2 次時，補救需求會顯著上升

### 5.3 切補救其實是兩段判斷，不是一步到位

系統不是只要偵測到「有補救需求」就立刻切補救，而是會經過兩段判斷：

1. 先判斷是否已經出現穩定卡點
2. 再判斷這一輪 routing action 是否真的選擇 `remediate`

可以把這兩段拆成：

#### 第一段：建立補救需求

這一段的目的是產生：

`remediation_review_ready = true / false`

也就是系統先回答：

「這個學生現在是不是已經卡到值得考慮補救了？」

目前教學模式常見會讓補救需求上升的訊號包括：

1. 同一個 family 連錯達門檻
2. 整體 fail streak 達門檻
3. `frustration_index` 偏高
4. 題目或錯誤訊號呈現明顯 sign / bracket / power 類型卡點

所以白話上：

1. 錯 1 題通常還只是觀察
2. 同類題持續錯，才會被視為「穩定卡點」

#### 第二段：routing 是否批准切補救

即使第一段已經認定補救需求存在，也還不等於下一題一定切補救。

因為系統還要建立 `action_mask`，看目前允許的行為有哪些：

1. `stay`
2. `remediate`
3. `return`

接著再由 PPO route action 或 heuristic fallback 決定這一輪最後動作。

因此真正切補救的條件不是單一布林值，而是：

`有補救需求 + routing 最後選擇 remediate`

### 5.4 實際理解方式

可以把 teaching mode 中的補救切入理解成：

1. 系統先覺得你有可能真的卡住了
2. 系統再決定「這一輪要不要真的帶你去補救」

換句話說：

- `remediation_review_ready` 像是「老師判斷你可能需要補課」
- `route_action = remediate` 像是「老師這一題真的帶你去補課」

### 5.3 誰決定真的切補救

即使 `remediation_review_ready = true`，也不是直接硬切。

接下來還要經過 routing layer 判斷：

1. 可否 `stay`
2. 可否 `remediate`
3. 可否 `return`

再由 PPO route action 或 heuristic fallback 做最終選擇。

所以 teaching mode 的切補救流程是：

`發現可能卡點 -> action mask 開放 remediate -> routing 決定是否真的切入`

---

## 6. 補救模式裡發生什麼事

### 6.1 補救目標的來源

系統會根據：

1. 當前 family
2. 當前 subskill
3. 錯誤現象
4. prerequisite candidate 配置

去找出較合理的補救 skill/subskill。

以多項式單元為例，補救可能會優先往：

1. 整數符號規則
2. 整數乘除
3. 分配律
4. 括號範圍
5. 指數相關基礎規則

這也符合 guardrails 要求的 bridge 方向：

`polynomial -> numbers -> integers`

### 6.2 補救期間不等於單元完成

進入補救後，系統會記錄：

1. `in_remediation`
2. `steps_taken`
3. `recent_results`
4. `remediation_mastery`
5. `remediation_skill`
6. `remediation_subskill`

補救模式的目的，是先把卡點補回來，不是直接結束整個 teaching session。

---

## 7. 什麼情況會從補救返回主線

### 7.1 返回主線的判斷依據

系統會計算 `remediation_mastery`，並配合 return 規則判斷是否可回主線。

多項式單元目前 remediation return 規則為：

1. `return_mastery_threshold: 0.85`
2. `return_mastery_with_recent_correct_threshold: 0.75`

表示：

1. 補救掌握度高於 `0.85`，可回主線
2. 或掌握度高於 `0.75` 且最近有答對，也可回主線

### 7.2 返回主線不是補一題就回去

這裡要特別強調，補救題並不是做完一題就會回主線。

系統在補救期間會持續累積：

1. `steps_taken`
2. `recent_results`
3. `last_result`
4. `remediation_mastery`

然後再判斷：

1. 是否已達高掌握門檻
2. 是否已達較低掌握門檻且最近答對

只有當 return 規則通過時，routing 才會允許 `return` 這個 action。

所以白話上：

1. 補救不是「做過」就算
2. 要補到系統覺得你真的有補回來，才會放你回主線

### 7.2 返回主線後的狀態

返回主線時，系統通常會標記：

1. `return_to_mainline = true`
2. `local_remediation_completed = true`
3. `learning_mode = returned`

這表示「本輪局部補救成功」，但**不等於整個 teaching mode 完成**。

---

## 7A. 補救子技能是怎麼決定的

這一段是 teaching mode 中最容易被誤解的部分。

目前系統不是用單一檔案直接寫死：

「F2 錯了就一定回某一個固定子技能」

而是分成多段決策。

### 7A.1 第一層：先決定這個 family 可回哪些候選補救子技能

這一層主要由單元 progression 設定決定。

以多項式四則運算為例，每個 family 都會在教材設定中宣告：

1. `main_subskills`
2. `prerequisite_candidates`
3. `prerequisite_candidate_descriptions`

例如：

1. `F2` 可能對應 `outer_minus_scope`
2. `F2` 也可能對應 `monomial_distribution`
3. `F2` 也可能對應 `like_term_combination`

因此這一層回答的是：

「如果這個 family 卡住，合理的補救候選有哪些？」

### 7A.2 第二層：再從候選裡挑這次最像哪個卡點

候選出來之後，系統不一定直接選第一個，而是會進一步根據學生這次作答現象做診斷。

這一層會綜合使用：

1. 當前 family
2. 當前 subskill
3. 題目文字
4. 學生答案
5. 正確答案
6. 錯誤訊號 hint

在多項式單元中，這一步可能產出：

1. `suggested_prereq_subskill`
2. `selected_prereq_subskill`
3. `selected_runtime_subskill`

### 7A.3 第三層：如果診斷沒選出來，才走 fallback

如果候選診斷不夠明確，系統還會走 heuristic fallback。

例如：

1. sign / bracket 類型錯誤時，優先回外層負號、分配律、同類項整理
2. power 類型錯誤時，優先回 signed power interpretation、same-base multiplication rule、power-of-power rule、product-power distribution

所以最終補救子技能的決策不是單一步驟，而是：

`family -> 候選補救清單 -> 診斷選擇 -> 若失敗則 fallback`

### 7A.4 文件層面要怎麼看這件事

如果要追這個流程，通常要分開看三類設定：

1. `textbook_progression_polynomial.yaml`
   用來決定 family 的補救候選清單

2. `rag_diagnosis_mapping.yaml`
   用來把某些錯誤概念映射到較合理的 prereq subskill

3. `subskill_remediation.yaml`
   用來描述 subskill 與更底層 bridge target 的對應

---

## 7B. 系統裡「學生的錯法」是怎麼定義的

這一段直接影響 teaching mode 的補救決策。

### 7B.1 錯法不是只有「答錯」

目前系統中的錯法至少分兩層：

1. 第一層：是否答對 `is_correct`
2. 第二層：如果答錯，進一步把錯誤歸類成某個 `error_concept`

所以：

- `is_correct = false` 只是代表答錯
- 真正影響補救決策的是後續的 `error_concept`

### 7B.2 第一層：答對/答錯如何判

系統會先透過批改器比對：

1. 數值答案是否相同
2. 分數值是否等價
3. 代數式是否符號等價
4. 商與餘式格式是否正確

這一層回答的是：

「學生有沒有答對」

### 7B.3 第二層：答錯後如何判定錯法

答錯之後，系統會嘗試把這次錯誤歸成一個較具教學意義的 `error_concept`。

以多項式單元來說，目前常見概念標籤包括：

1. `outer_minus_scope`
2. `sign_distribution`
3. `sign_flip_after_distribution`
4. `combine_like_terms_after_distribution`
5. `coefficient_arithmetic_error`
6. `binomial_expansion_structure_error`
7. `mixed_simplify_transition_error`
8. `family_isomorphism_confusion`
9. `nested_grouping_structure_error`

這些概念標籤不是完整的人工語意分析，而是系統根據當前情境推定出的錯誤概念。

### 7B.4 系統用哪些訊號推定錯法

目前主要看：

1. 當前 family
2. 當前 subskill
3. 題目文字特徵
4. 學生答案與正解的差異
5. 目前 session 的 error type hint

例如：

1. 在 `F2` 且題目有 `-(` 這類括號結構時，較可能判成 `outer_minus_scope`
2. 在多項式展開 family 中，若和展開結構相關，可能判成 `binomial_expansion_structure_error`
3. 若學生答案與正解都含變數但未正確整理，可能判成 `combine_like_terms_after_distribution`

### 7B.5 錯法最後怎麼接到補救

一旦 `error_concept` 被推定出來，系統會再把它映射成：

1. `suggested_prereq_skill`
2. `suggested_prereq_subskill`

再交由 routing 決定：

1. 是先留在主線
2. 還是切去補救

所以完整鏈條是：

`答錯 -> 推定 error_concept -> 映射到 prereq subskill -> routing 決定是否補救`

---

## 8. Teaching Mode 真正的結束條件

### 8.1 結束不是看單一 APR 門檻

teaching mode 現在的結束條件不是：

- APR 到某個百分比就停

而是看**單元完成 gate**。

### 8.2 單元完成 gate 的三個條件

系統會計算：

1. `covered_core_families`
2. `passed_core_families`
3. `integrative_family_passed`

再判斷：

1. `coverage_ok`
2. `mastery_ok`
3. `integrative_ok`

只有三者都成立，才會：

`unit_completed = true`

接著後端才會回傳：

`completed = true`

### 8.3 多項式單元目前的 teaching 過關標準

多項式四則運算目前設定如下：

- 核心 family: `F1`, `F2`, `F5`, `F11`
- `minimum_covered_core_families: 4`
- `minimum_passed_core_families: 3`
- `require_integrative_family_pass: true`
- `integrative_family_id: F11`

白話意思是：

1. `F1`, `F2`, `F5`, `F11` 這四個核心 family 都要被碰到
2. 至少三個核心 family 要有答對紀錄
3. `F11` 綜合化簡一定要做對過

只要這三件都成立，teaching mode 才會真正結束。

### 8.4 什麼不算 teaching mode 結束

下列情況都不算整體完成：

1. 只是剛從補救回到主線
2. 只是某一個 family 做對
3. 只是 APR 變高
4. 只是單次補救成功

這些最多只代表：

1. 局部進步
2. 補救成功
3. 可以回主線繼續檢核

---

## 9. Teaching Mode 與 Assessment Mode 的關係

### 9.1 目前兩者尚未正式串接

現行實作中：

1. assessment mode 會產出 `diagnostic_report`
2. teaching mode 會開新 session 自己開始跑

但 assessment 的 breakpoint / weaknesses 目前**沒有正式交接**到 teaching mode。

### 9.2 目前 assessment 的用途

assessment mode 目前主要用途是：

1. 找出弱項 family
2. 產出 APR / score / weaknesses 報告
3. 告訴使用者建議切到 teaching mode

但 teaching mode 目前還不會自動說：

「我知道你剛剛 assessment 卡在 F2，所以我直接從 F2 補起。」

### 9.3 對產品體驗的實際影響

這代表目前使用者感受會比較像：

1. assessment 負責健檢
2. teaching 負責教學
3. 兩者邏輯上相關，但資料交接尚未完整

所以 teaching mode 目前是完整的教學狀態機，但不是 assessment 的自然續接。

---

## 10. Teaching Mode 的使用者可見行為總結

從學生角度看，teaching mode 的體驗可整理成：

1. 先從本單元主線開始做題
2. 如果在某個觀念上持續出錯，系統會切到補救
3. 補救到一定程度後，系統再帶回主線
4. 如此循環，直到整個單元過關

因此 teaching mode 不是單純「一直教同一題型」，而是：

`主線教學 + 補救橋接 + 返回主線驗證`

---

## 11. 目前實作下最重要的三個判讀原則

### 原則 1：Teaching mode 是整單元導向，不是單題導向

它會根據 family 級別掌握狀態決定是否繼續，而不是做完某一題就算結束。

### 原則 2：補救完成不等於單元完成

`local_remediation_completed = true` 只表示這一輪補救結束，還要回主線持續檢核。

### 原則 3：目前 assessment 與 teaching 還沒有記憶串接

assessment mode 能找出卡點，但 teaching mode 目前不會自動接手前次 assessment 的 breakpoint。

---

## 12. 後續文件建議

如果後續要持續擴充教學模式文件，建議再拆出三份：

1. `TEACHING_MODE_STATE_MACHINE.md`
   說明 `mainline / remediation / returned / completed` 狀態轉移

2. `TEACHING_MODE_COMPLETION_GATES.md`
   逐單元列出 completion gate 設定

3. `ASSESSMENT_TO_TEACHING_HANDOFF.md`
   說明 assessment 結果如何正式交接到 teaching mode

---

## 13. 一句話總結

目前 teaching mode 的本質是：

**以教材主線為骨架，根據學生作答動態切換補救，再回主線驗證，直到整個單元完成 gate 通過為止。**
