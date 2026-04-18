# Adaptive Strategy Study — 實驗產出目錄

本目錄集中存放「適應性策略（AB1／AB2／AB3）」模擬實驗之正式輸出，與程式碼目錄 `scripts/adaptive_strategy_study/` 對齊；路徑解析見該處之 `study_paths.study_reports_root()`。

## 子目錄與研究問題

| 子目錄 | 對應實驗 | 研究問題（簡稱） |
|--------|----------|------------------|
| `experiment_1_ablation/` | Exp1 | RQ1 — 策略有效性（effectiveness） |
| `experiment_2_ab3_student_types/` | Exp2 | RQ2 — 運作機制（mechanism） |
| `experiment_3_weak_foundation_support/` | Exp3 | RQ3 — 減 C／弱基學生支援（reduce C） |

## 研究總覽文件

- **`research_design_overview.md`**：研究背景、RQ、模擬設定、結論與附錄（含程式路徑與重現指令）。

## 建議重現指令（於專案根目錄執行）

```bash
python scripts/adaptive_strategy_study/exp1_effectiveness/run_experiment1_multisteps.py
python scripts/adaptive_strategy_study/exp2_mechanism/simulate_student.py
python scripts/adaptive_strategy_study/exp3_reduce_c/run_weak_foundation_support_strategy_comparison.py
```

亦可使用 `scripts/` 根目錄之轉發腳本（行為等同上述新路徑）。

新產出之 CSV、MD、PNG、`runs/`、`latest/` 等均寫入本目錄下對應子資料夾，不寫回 `reports/experiment_*` 舊路徑。

## Freeze point（封版註記）

- **Freeze point**: 2026-04-15
- **scripts structure frozen**: `scripts/adaptive_strategy_study/` 視為穩定版結構
- **reports structure frozen**: `reports/adaptive_strategy_study/` 視為穩定版結構
- **experiment assumptions frozen**: 研究假設／門檻／固定設定以 `research_design_overview.md` 與程式現況為準
- **current branch**: `demo-prep baseline`
