# 系統核心穩定性修復報告 (System Repair Report)

## 修復標的概述

本次修復針對目前專案中四大不穩定的潛在點進行了 Minimal Patch 修補，並遵循向前相容與防呆原則，確保主流程不再因環境變量或外部依賴影響而輕易報錯：
1. PPO 模型加載順序重建 (修復了對 joblib.load 的嚴重依賴風險)
2. Advanced RAG 機制重啟與環境驗證 (補強錯誤回報與路由切換)
3. DB Prompt 取代機制失效問題 (修復了核心的套件循覽地雷，讓 admin UI 設定能真正打通)
4. 手寫批改極端情境強化 (防禦 OCR 缺失與增強全半形/空白數學等值驗證)

## 詳細修復清單

### 1. PPO Policy Loader 修復
- **修改位置**：`core/adaptive/ppo_adapter.py`
- **問題現象**：加載模型時沒有以 `stable_baselines3.PPO` 為首選，強制跑到最後 fallback 的 joblib 造成架構不匹配。
- **修復內容**：
  在 `for strategy in (...)` 首位注入了 `stable_baselines3` 處理流程，並加入 `PPO.load` 的判斷，確保若新版模型採用標準 SB3 格式儲存，能一併被完整且正確地初始化進 `model`。
- **遺留風險**：假設 PPO 存檔類型混亂且不自帶 MetaData，依然需要手動轉化檔案，但此更新保證了系統能順利接管新版標準備份。

### 2. Advanced RAG 啟動與依賴判定修復
- **修改位置**：`core/advanced_rag_engine.py`、`core/routes/analysis.py`
- **問題現象**：`HAS_ADV_LIBS` 缺乏具體套件名稱回報，且 `/api/rag_chat` 寫死永遠不進入進階檢索。
- **修復內容**：
  1. 在 `init_adv_rag` 中加入了 array 動態判定 `chromadb, sentence_transformers, rank_bm25, jieba` 哪些不存在，並印出可視化的 Error Log 給終端人員，而不再是泛泛的 missing dependencies。
  2. 替換 `/api/rag_chat` 內的呼叫邏輯：首先偵測 `HAS_ADV_LIBS`，若通過，調用 `adv_rag_search` 拉出混合資料，並將參數引導入 `adv_rag_chat` 以落實 RRF 機制，查無模組才優雅 fallback 到 `rag_chat`。

### 3. Prompt DB 動態接管問題修復
- **修改位置**：`core/prompts/registry.py`，並新增 `scripts/migrate_prompt_templates.py`。
- **問題現象**：`rag_tutor_prompt` 和其他設定檔在 trace 的時候總是走 `default_templates`，代表 Admin UI 的調整被截斷。
- **修復內容**：
  1. 發現了一個重大的隱蔽 Bug：`registry.py` 裡的 `try ... from models import PromptTemplate` 因為在 `models.py` 內無定義而造成 `ImportError`，導致整個查表程式塊失效。已修正為 `from core.models.prompt_template import PromptTemplate` 將資料庫正式打通。
  2. 撰寫與執行了 db 推進腳本 `migrate_prompt_templates.py`，將缺漏的提示詞如 `rag_tutor_prompt` 正式建檔進入 PromptTemplate Table，確保設定面板完全接通。

### 4. 手寫批改 (Handwriting Evaluator) 防呆與正規化
- **修改位置**：`core/routes/analysis.py`
- **問題現象**：OCR 回傳空字串未被捕捉；全半形未正規化造成部分數學等值判斷陣亡。
- **修復內容**：
  在主評斷函數 `_handwriting_structured_analysis` 內加入了 `_clean_math_expr` 進行 `NFKC` 標準化以及去除繁贅的空白/全型符號。增加了 `if not recognized_expression: return status: ocr_failed` 來接管辨識失常，有效防止批改流程走到一半引發 None 或 Exception。
