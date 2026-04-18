# LOCAL_APR_AKT_STUB_EXPLAINER

更新日期: 2026-04-10  
範圍: 自適應學習頁面中的 `current_apr` / Local APR  
對應實作: `core/adaptive/akt_adapter.py`

---

## 1. 這份文件在說什麼

自適應學習頁面左側圓環顯示的「掌握度」，以及右側軌跡圖每個 Step 的百分比，都是後端回傳的 `current_apr`。

在目前 PoC 版本中，`current_apr` 不是正式 AKT 模型推論出的機率，而是一個模仿 AKT 行為的本地啟發式分數。程式中把它放在 `akt_adapter.py`，原因是它扮演 AKT adapter 的位置：接收上一題作答結果，輸出一個可供 PPO / routing 使用的 Local APR。

換句話說：

```text
目前版本:
作答結果 + subskill 數量 + 挫折指數
  -> heuristic update_local_apr()
  -> current_apr
  -> 前端顯示掌握度 / PPO 策略參考

理想正式版本:
作答歷史 + subskill 序列 + 題目特徵
  -> AKT model inference
  -> P(correct | target_subskills)
  -> Local APR
```

---

## 2. 名詞定義

### 2.1 APR

APR 在目前系統中可理解為：

```text
系統對學生在當前目標微技能上的即時掌握度估計
```

數值範圍是 `0.05 ~ 0.98`，前端會乘上 100 顯示成百分比。

例如：

```text
current_apr = 0.55
前端顯示 = 55%
```

### 2.2 Local APR

文件 `ARCHITECTURE_NOTES.md` 中的理想定義是：

```text
LocalAPR_t = mean( P(correct | subskill in target_subskills_t) )
```

意思是：只看目前題目或目前 family 涉及的 subskills，不把其他不相關技能混進來。這樣 PPO 的決策訊號比較乾淨，不會被全域能力值污染。

目前 PoC 沒有真的跑 AKT 模型，所以用 `update_local_apr()` 做近似。

### 2.3 frustration_index

`frustration_index` 是挫折指數，也就是連續答錯的累積。

規則在 `core/adaptive/session_engine.py`：

```text
尚未作答: 沿用上一筆，若沒有上一筆則為 0
答對: 0
答錯: 上一筆 frustration_index + 1
```

它的作用是讓連續答錯時，APR 下降更明顯，並且影響 PPO 是否切到 Review / 補救。

### 2.4 subskill_count

`subskill_count` 是上一題關聯到的 subskill 數量。

目前公式會給 subskill 數量一個小幅加成 `span_bonus`。這個設計的直覺是：如果一題涵蓋較多微技能，答對時代表學生可能展現了較廣的掌握；答錯時則先不要讓跨度造成過度懲罰，所以公式中仍保留小幅正向補償。

---

## 3. 初始 APR

每個 adaptive session 第一次沒有上一題作答結果，因此使用 bootstrap 值：

```python
def bootstrap_local_apr() -> float:
    return 0.45
```

所以新 session 的第一步通常會看到：

```text
current_apr = 0.45
前端顯示 = 45%
```

這不是學生真的只有 45 分，而是系統在尚未觀察到本 session 作答前，採用的中低初始估計。

---

## 4. APR 更新公式

核心函式是：

```python
def update_local_apr(
    previous_apr: float,
    is_correct: bool,
    frustration_index: int,
    subskill_count: int = 1,
) -> float:
```

先計算題目跨度加成：

```text
span_bonus = min(max(subskill_count, 1), 4) * 0.01
```

也就是：

| subskill_count | span_bonus |
|---:|---:|
| 0 或 1 | 0.01 |
| 2 | 0.02 |
| 3 | 0.03 |
| 4 | 0.04 |
| 5 以上 | 0.04 |

### 4.1 答對時

```text
new_apr =
  previous_apr
  + 0.08
  + span_bonus
  - min(frustration_index, 3) * 0.01
```

含意：

1. 答對會讓 APR 上升 `0.08`。
2. 題目涵蓋的 subskill 越多，最多額外加 `0.04`。
3. 如果學生之前累積挫折，答對後仍會略微扣回，避免一次答對就過度樂觀。
4. 因為答對會把 `frustration_index` 歸零，所以一般答對題通常不會吃到挫折扣分。

### 4.2 答錯時

```text
new_apr =
  previous_apr
  - 0.10
  + span_bonus
  - min(frustration_index, 3) * 0.02
```

含意：

1. 答錯會讓 APR 下降 `0.10`。
2. 題目跨度仍給一點補償，避免多 subskill 題目過度拉低估計。
3. 連續答錯時，`frustration_index` 變大，額外懲罰最多到 `3 * 0.02 = 0.06`。
4. 因此連錯越多，APR 掉得越快，系統越容易切入 Review / 補救。

### 4.3 範圍限制

更新後會套用 clamp：

```text
new_apr = max(0.05, min(0.98, new_apr))
```

最後四捨五入到 4 位小數：

```text
return round(new_apr, 4)
```

所以 APR 不會低於 `5%`，也不會高於 `98%`。

---

## 5. 實際例子

### 5.1 第一次載入

沒有上一題作答：

```text
current_apr = 0.45
前端顯示 = 45%
```

### 5.2 第一題答對，題目有 2 個 subskills

條件：

```text
previous_apr = 0.45
is_correct = True
frustration_index = 0
subskill_count = 2
span_bonus = 0.02
```

計算：

```text
new_apr = 0.45 + 0.08 + 0.02 - 0
        = 0.55
```

前端顯示：

```text
55%
```

### 5.3 第一題答錯，題目有 2 個 subskills

條件：

```text
previous_apr = 0.45
is_correct = False
frustration_index = 1
subskill_count = 2
span_bonus = 0.02
```

計算：

```text
new_apr = 0.45 - 0.10 + 0.02 - 1 * 0.02
        = 0.35
```

前端顯示：

```text
35%
```

### 5.4 連續第二題答錯

假設上一題後 APR 是 `0.35`，這題又答錯，仍有 2 個 subskills：

```text
previous_apr = 0.35
is_correct = False
frustration_index = 2
subskill_count = 2
span_bonus = 0.02
```

計算：

```text
new_apr = 0.35 - 0.10 + 0.02 - 2 * 0.02
        = 0.23
```

前端顯示：

```text
23%
```

這時因為 `frustration_index >= 2`，PPO stub 也會傾向切到 Review 策略。

---

## 6. APR 和 PPO 策略的關係

APR 更新完之後，系統會用 `current_apr`、`frustration_index`、`step_number` 選策略。

目前 PoC 的策略規則在 `core/adaptive/ppo_adapter.py`：

```text
if frustration_index >= 2:
    ppo_strategy = 3  # Review
elif current_apr < 0.45:
    ppo_strategy = 1  # ZPD
elif step_number > 0 and step_number % 4 == 0:
    ppo_strategy = 2  # Diversity
else:
    ppo_strategy = 0  # Max-Fisher
```

策略代碼固定為：

| code | 策略 | 用途 |
|---:|---|---|
| 0 | Max-Fisher | 最大資訊探索 |
| 1 | ZPD | 近側發展區 |
| 2 | Diversity | 多樣化抽樣 |
| 3 | Review | 觀念補救 / RAG 介入 |

所以 APR 的角色不是單純顯示分數，它也是 routing / PPO 的輸入訊號之一。

---

## 7. 前端如何顯示 APR

後端 API 回傳：

```json
{
  "current_apr": 0.55,
  "ppo_strategy": 0,
  "frustration_index": 0
}
```

前端在 `templates/adaptive_practice_v2.html` 中轉成百分比：

```javascript
const apr = Number(response.current_apr || 0);
const percent = Math.round(apr * 100);
```

因此：

```text
0.55 -> 55%
0.452 -> 45%
0.977 -> 98%
```

左側圓環與右側軌跡圖使用的是同一個 `current_apr`。

---

## 8. 和正式 AKT 的差異

目前版本稱為「模仿 AKT」或「AKT stub」，主要差異如下：

| 面向 | 目前 PoC heuristic APR | 正式 AKT |
|---|---|---|
| 輸入 | 上一題對錯、subskill 數量、挫折指數 | 完整作答序列、題目序列、技能嵌入、時間序列特徵 |
| 更新方式 | 手寫公式 | 模型推論 |
| 輸出意義 | 即時掌握度近似值 | `P(correct | skill, history)` |
| 可解釋性 | 高，容易展示 | 較低，需要模型解釋 |
| 精準度 | 粗略 | 取決於訓練資料與模型品質 |
| 用途 | PoC 閉環、前端展示、PPO stub 訊號 | 正式個人化診斷與策略決策 |

因此在論文、簡報或系統說明中，建議用以下說法：

```text
目前系統以 heuristic Local APR 作為 AKT adapter 的 PoC 替代器，
用來模擬知識追蹤模型對學生當前微技能掌握度的即時估計。
正式版本可將 `update_local_apr()` 替換為 AKT / DKT / SAINT 類模型推論，
而不改變下游 PPO routing 與前端顯示介面。
```

---

## 9. 為什麼這樣設計

這個設計的目的不是宣稱已完成完整 AKT，而是讓三層架構先形成可運作閉環：

1. progression 決定教材主線與 prerequisite 意圖。
2. AKT adapter 位置輸出 Local APR。
3. PPO / routing 根據 APR、挫折指數與歷史狀態決定下一步。
4. remediation / RAG 在 Review 或補救條件成立時介入。
5. 前端用同一個 `current_apr` 顯示 mastery trajectory。

因為 `update_local_apr()` 被封裝在 adapter 中，未來替換成正式 AKT 時，下游只要繼續接收 `current_apr` 即可。

---

## 10. 常見誤解

### 10.1 APR 是考試分數嗎？

不是。APR 是本 session 內對當前學習目標的即時掌握估計，不等同於成績分數。

### 10.2 APR 是全科能力值嗎？

不是。它是 Local APR，目標是反映當前題目 / family / subskills 的掌握狀態。

### 10.3 55% 代表學生真的只會 55% 嗎？

不是。55% 是 heuristic tracker 的當下估計，用於自適應路由與畫面回饋。

### 10.4 為什麼答錯還有 span_bonus？

因為多 subskill 題目本身跨度較大，公式保留小幅補償，避免一次多點失誤就讓 APR 掉得過度劇烈。真正主要影響仍是答錯懲罰與連錯挫折懲罰。

### 10.5 可以換成真正 AKT 嗎？

可以。此設計刻意把 APR 更新集中在 `akt_adapter.py`，未來可以把 `update_local_apr()` 換成模型推論，只要仍輸出 `0~1` 的 `current_apr`，PPO routing 與前端就能沿用。

---

## 11. 相關檔案

| 檔案 | 角色 |
|---|---|
| `core/adaptive/akt_adapter.py` | APR bootstrap 與 heuristic 更新公式 |
| `core/adaptive/session_engine.py` | 讀取上一筆 log、計算 frustration_index、呼叫 APR 更新、回傳 current_apr |
| `core/adaptive/ppo_adapter.py` | 使用 current_apr / frustration_index / step_number 選策略 |
| `templates/adaptive_practice_v2.html` | 把 current_apr 轉成百分比並繪製圓環與軌跡 |
| `docs/自適應實作/ARCHITECTURE_NOTES.md` | Local APR 的架構定義 |
| `docs/simulated_student.md` | 模擬學生也使用同一 APR 更新函式作公平對照 |

