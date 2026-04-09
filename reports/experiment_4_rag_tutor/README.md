# Experiment 4：Retrieval-Augmented Tutor（RAG）延伸實驗

## 一、研究目的與定位

本實驗旨在評估：在 **Experiment 3（weak foundation support）已建立之強 baseline** 上，加入 Retrieval-Augmented Tutor（RAG）後，是否仍能提供額外且可解釋的學習價值。  
因此，本研究問題並非「RAG 是否有效」，而是：

> **在既有教學時機（when to teach）已優化的條件下，RAG 對學習成效與效率是否仍具邊際貢獻？**

---

## 二、實驗設計

### 2.1 比較條件

1. `weak_ab3_foundation`（baseline）  
2. `weak_ab3_foundation_rag`（在 baseline 上加入 RAG tutor）

### 2.2 設計原則

- 不調整成功判準（success criteria）
- 不更動核心學習更新機制
- 以相同弱學生設定進行對照
- 比較重點為「在強 baseline 上的額外增益」

---

## 三、評估指標（Metrics）

| 指標 | 定義 | 研究意義 |
|---|---|---|
| Success Rate | 成功 episode 比例 | 衡量最終達標能力 |
| Final Mastery | 最終 polynomial mastery 平均 | 衡量最終能力水準 |
| Subskill Gain | 各子技能最終 - 初始 mastery | 檢查能力改善分布 |
| Breakpoint Shift | 失敗案例 weakest subskill 分布變化 | 檢查瓶頸是否轉移 |
| Learning Efficiency | `mastery_gain / total_steps` | 衡量單位學習成本效益 |

> **Learning Efficiency 定義：**  
> \[
> \text{learning\_efficiency} = \frac{\text{mastery\_gain}}{\text{total\_steps}}
> \]

---

## 四、核心結果（貼近實際觀察）

依目前實驗輸出（`rag_vs_baseline_summary.csv`、`rag_efficiency_summary.csv`、`rag_subskill_summary.csv`、`rag_breakpoint_shift.csv`）可歸納：

1. **Success Rate：小幅提升，但未呈現明確大幅差距**。  
2. **Final Mastery：兩組差異極小，整體接近持平**。  
3. **Learning Efficiency：出現輕微提升（約 1% 左右量級）**。  
4. **Subskill Gain：呈現混合效果，非所有子技能一致受益**。  
5. **Breakpoint Shift：分布變化有限，結構性瓶頸仍存在**。  
6. **`family_isomorphism` 等高階結構子技能仍為主要難點**。  

---

## 五、結果解釋（Discussion）

### 5.1 邊際改善而非突破性提升

本實驗顯示，RAG 在此設定下提供的是**邊際改善（marginal improvement）**，而非跨層級的成效躍升。其主要效益較多反映在「學習效率」而非「最終能力上限」。

### 5.2 強 baseline 的天花板效應

由於 Experiment 3 的 baseline 已具備弱學生 foundation support，系統已吸收相當比例的可得收益；RAG 介入後的可提升空間自然受限。

### 5.3 Targeting 能力尚未充分顯現

若 RAG 真正強化弱點對準（targeted support），理應在 weakest subskills 與 breakpoint 分布上產生更明顯轉移；目前僅見有限變化，表示其 targeting 行為尚不強。

---

## 六、關鍵洞見（Research Insight）

> **當學習策略層（when to teach）已相對成熟時，內容檢索層（what to teach）的可提升空間往往縮小。**  
> 在此情境下，RAG 更像是系統微調（refinement）工具，而非決定性增益來源。

---

## 七、研究限制（Limitations）

1. 現行 retrieval 機制可能仍屬簡化版本。  
2. RAG 尚未深度整合至決策 policy（僅局部介入）。  
3. 未使用 learned retrieval（如可學習 relevance/embedding selection）。  
4. baseline 強度較高，導致可觀測增益上限受限。  

---

## 八、未來工作（Future Work）

1. 將 retrieval 訊號深度整合到 policy 決策流程。  
2. 引入 learned relevance / embedding-based retrieval。  
3. 在較弱 baseline 上重測，以辨識 RAG 的可擴張增益。  
4. 增加長期學習曲線分析，檢查短期效率是否能轉化為長期能力差異。  

---

## 九、結論（Conclusion）

本實驗支持以下結論：

- **RAG 在本設定下是有效的，但影響幅度有限。**
- **主要改善出現在學習效率，而非最終 mastery 的明顯提升。**
- 對於已優化之強系統，RAG 屬於 **refinement**，尚不足以視為 **game-changer**。  

---

## 十、對應輸出檔案（供查閱）

- `rag_vs_baseline_summary.csv`
- `rag_efficiency_summary.csv`
- `rag_subskill_summary.csv`
- `rag_breakpoint_shift.csv`
- `fig_rag_success_rate.png`
- `fig_rag_mastery.png`
- `fig_rag_subskill_gain.png`
- `fig_rag_breakpoint_shift.png`
- `fig_rag_efficiency.png`

---

## 十一、重現方式（Reproducibility）

在專案根目錄執行以下指令：

```bash
python scripts/run_rag_intervention_experiment.py
```
