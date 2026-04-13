# Experiment 1：多步數上限消融實驗（Multi-Step Ablation Study）

## 1. 實驗動機（Motivation）
在自適應學習情境中，僅以固定流程推進（Baseline）容易忽略學生當下狀態，導致學習路徑缺乏彈性。  
規則式補救（Rule-Based）雖可在錯誤後介入，但常因觸發條件僵化而出現過度補救，增加步數成本。  
因此，本研究需要驗證具動態決策能力的 Adaptive 策略，是否能更精準地在主線學習與補救之間切換。  
此外，若只看成功率，可能忽略策略是否以過多步數換取表面成效；若只看效率，又可能低估學習品質。  
本實驗因此同時評估成功率與學習效率，以建立更完整、可解釋的策略比較基準。

## 2. 實驗目的（Objective）
本實驗旨在比較三種教學策略在不同步數上限下的整體表現與效率：

- Baseline
- Rule-Based
- Adaptive（我們的方法）

比較條件為 `MAX_STEPS = 30 / 40 / 50`。主要評估指標包含：

- Success Rate
- Avg Steps
- Unnecessary Remediation
- Final Mastery

## 3. 實驗設定（Experimental Setup）

### 3.1 學生類型（Student Types）
本實驗使用三種學生模型：

- Careless（粗心型）：整體能力可達一定水準，但較容易出現失誤。
- Average（一般型）：能力分布中等，學習表現相對穩定。
- Weak Foundation（基礎薄弱）：前置基礎較弱，達成目標通常需要更多支持。

---

### 3.2 樣本數設計（Sample Size）
本實驗採平衡設計（balanced design）：

- 每類型學生：100 人
- 三種類型：每策略 300 人
- 三種策略：每個 `MAX_STEPS` 共 900 人
- 三組 `MAX_STEPS`（30 / 40 / 50）：總計 2700 筆模擬

此設計可避免因類型樣本不均而導致策略比較偏誤。

---

### 3.3 關鍵參數（Key Parameters）
- `MAX_STEPS = 30 / 40 / 50`
- 每個 episode 皆有步數上限（hard cap）
- 使用固定亂數種子（`random.seed`）以確保隨機過程可重現

## 4. 方法（Method）
每位模擬學生在對應策略下進行一系列解題 episode。策略差異主要反映在決策流程：是否持續主技能路徑、何時進入補救、以及何時返回主線。  
本實驗採用 Monte Carlo simulation：透過隨機生成學生能力分布，並重複模擬學習歷程，估計各策略在不同條件下的統計表現。  
此作法讓評估不依賴單次樣本，而是以多次隨機抽樣後的整體趨勢進行比較。  
系統在每一步都追蹤作答結果與學習狀態，並累積 mastery 變化與步數使用情形。  
最終以策略層級與學生類型層級彙整指標，評估各方法在效果與成本上的整體表現。

## 5. 執行方式（Execution）
```bash
python scripts/run_multi_steps_experiment.py
```

執行後會產生：

- 統計表（summary table）
- 三張核心圖：
  - `fig_multi_steps_success_rate.png`
  - `fig_exp1_student_type_improved.png`
  - `fig_multi_steps_efficiency.png`

## 6. 實驗結果（Results）
整體趨勢顯示，Adaptive（我們的方法）在各 `MAX_STEPS` 設定下皆呈現最高成功率。  
隨步數上限提高，Adaptive 的優勢更為明顯，代表其可有效利用額外學習步數。  
Baseline 雖有一定成長，但提升幅度相對有限。  
Rule-Based 在多數情境下呈現較高的不必要補救，顯示固定規則介入可能造成效率損失。

## 7. 結果分析（Analysis）
Adaptive 的主要優勢來自動態決策（dynamic routing）：能依當前作答與能力狀態調整主線與補救切換時機，降低錯配補救的機率。  
相較之下，Rule-Based 較容易在不需要時仍觸發補救，導致步數消耗增加，影響整體效率。  
從效率觀點來看，Adaptive 能在較少步數下取得較高成功率，呈現更佳的成功率與步數權衡。  
不同學生類型中，Adaptive 皆維持相對優勢，尤其在學習條件較不利的族群中仍可提供可觀改善。  

"The weak foundation group shows low absolute success rates, but Adaptive (Ours) still achieves the highest relative improvement."

## 8. 結論（Conclusion）
本消融實驗顯示，Adaptive 明顯優於 Baseline 與 Rule-Based。  
其效果不僅體現在整體成功率，也能在不同學生類型下維持穩定優勢。  
在成功率與效率之間，Adaptive 展現出最佳平衡。  
研究結果支持在自適應學習系統中導入智慧決策機制的必要性。

## 9. 備註（Notes，可選）
- 本實驗為可控的模擬環境評估。
- 實驗流程與條件固定，具可重現性（reproducible）。
- 本實驗屬於隨機模擬（stochastic simulation），結果來自多次隨機樣本的統計平均，因此具有穩定性與可重現性（在固定 random seed 下）。
- 相關統計結果與圖表輸出可由同一指令完整重建。
