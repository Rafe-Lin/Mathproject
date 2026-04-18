# Experiment 1 結果總表

| MAX_STEPS | 策略 | 達標率 Success Rate (%) | 平均步數 Avg Steps | 平均不必要補救次數 Avg Unnecessary Remediations | 平均最終精熟度 Avg Final Mastery |
|---:|---|---:|---:|---:|---:|
| 30 | Baseline | 45.00 | 24.92 | 0.00 | 0.67 |
| 30 | Rule-Based | 45.33 | 24.35 | 0.60 | 0.69 |
| 30 | Adaptive（Ours） | 62.67 | 22.00 | 0.20 | 0.68 |
| 40 | Baseline | 55.33 | 30.35 | 0.00 | 0.69 |
| 40 | Rule-Based | 59.33 | 29.26 | 0.81 | 0.71 |
| 40 | Adaptive（Ours） | 66.00 | 25.92 | 0.18 | 0.68 |
| 50 | Baseline | 62.33 | 34.60 | 0.00 | 0.70 |
| 50 | Rule-Based | 64.67 | 33.41 | 0.76 | 0.73 |
| 50 | Adaptive（Ours） | 71.00 | 29.02 | 0.19 | 0.69 |

註：在弱基礎組（Weak Foundation）中，雖然絕對達標率仍偏低，但 Adaptive（Ours）仍呈現最高的相對改善幅度。

## Experiment 1 學生類型假設（繁中說明）

Experiment 1 的執行路徑為：`scripts/run_experiment1_multisteps.py` -> `simulate_student.run_batch_experiments()` -> `simulate_episode()` -> `SimulatedStudent(...)`。  
程式會先初始化完整的多項式子技能向量（`sign_handling`, `combine_like_terms`, `sign_distribution`, `expand_monomial`, `expand_binomial`, `family_isomorphism`），再由該向量計算整體多項式精熟度。

| 學生類型 | 初始精熟均值 | 變異 / 隨機性 | 子技能初始化邏輯 | 解讀 |
|---|---:|---|---|---|
| Careless | mean = 0.70 | 每個子技能以高斯分佈抽樣，`std = 0.17`（`random.gauss`），再截斷到 `[0.05, 0.98]` | 六個子技能皆使用同一套高斯規則（無固定偏移） | 整體能力偏高，但 slip 行為較強；即使高精熟仍可能出錯 |
| Average | 基礎曲線均值為 `[0.68, 0.62, 0.58, 0.53, 0.48, 0.44]` | 每個子技能加入均勻擾動 `random.uniform(-0.05, +0.05)`，再截斷到 `[0.05, 0.98]` | 非單一分佈；各子技能採遞減曲線 + 擾動 | 代表中等且均衡能力，基礎子技能通常高於後段結構技能 |
| Weak Foundation | mean = 0.32 | 每個子技能以高斯分佈抽樣，`std = 0.06`（`random.gauss`），再截斷到 `[0.05, 0.98]` | 六個子技能皆使用同一套高斯規則（無固定偏移） | 全面低起點且分布較集中，對應整體基礎薄弱 |

- 六個多項式子技能都會被明確初始化，不會留下空值或預設缺漏。
- 整體多項式精熟度不是單純平均；程式使用加權均值加上最低子技能懲罰：`0.75 * weighted_mean + 0.25 * weakest_subskill`，最後截斷到 `[0.0, 1.0]`。
- 為確保可重現性，實驗使用條件化種子：`MAX_STEPS=30 -> 42`、`40 -> 43`、`50 -> 44`。
- 各學生類型差異不只初始精熟度：
- `slip/guess` 參數不同（`Careless`: slip 0.20, guess 0.06；`Average`: slip 0.10, guess 0.04；`Weak`: slip 0.07, guess 0.03）。
- Careless 在命中子技能精熟度 `>= 0.70` 時有額外 slip 增量 `+0.05`。
- Weak 有較強的前置轉移係數（`0.06` vs `0.03`），並含 weak-only progression gate（`foundation mean < 0.55`）限制前期 family 路由。
- 精熟更新邊界：
- 初始化截斷：每個子技能初值限制在 `[0.05, 0.98]`。
- 更新截斷：子技能與聚合精熟度皆限制在 `[0.0, 1.0]`。
- Experiment 1 迴圈以 `MAX_STEPS` 實施硬上限（`if total_steps >= MAX_STEPS: break`）。

## Experiment 1 樣本數（繁中說明）

Experiment 1 由 `scripts/run_experiment1_multisteps.py` 執行，分別在 `MAX_STEPS` 為 30、40、50 下獨立跑條件種子。`scripts/simulate_student.py` 內集中定義樣本數 `EXP1_EPISODES_PER_TYPE = 100`，執行時各策略均採相同設定。

| 範圍 | 樣本數 | 說明 |
|---|---:|---|
| 每個學生類型（單一策略、單一 MAX_STEPS） | 100 | 由 `EXP1_EPISODES_PER_TYPE = 100` 定義 |
| Careless（每策略、每 MAX_STEPS） | 100 | 由 `STUDENT_TYPES` 迴圈與每類型 episode 數決定 |
| Average（每策略、每 MAX_STEPS） | 100 | 同上 |
| Weak Foundation（每策略、每 MAX_STEPS） | 100 | 執行標籤為 `Weak`，報告命名為 Weak Foundation |
| 單一策略（單一 MAX_STEPS）總數 | 300 | 3 種學生類型 × 100 |
| 單一 MAX_STEPS（全部 3 策略）總數 | 900 | 3 策略 × 3 類型 × 100 |
| 完整 Experiment 1（30/40/50）總數 | 2700 | 3 組 MAX_STEPS × 900 |

整體採平衡設計（balanced design），各類型樣本數一致，可降低因組間樣本不均造成的比較偏誤。
