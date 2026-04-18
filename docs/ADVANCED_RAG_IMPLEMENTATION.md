# Advanced RAG 混合檢索系統實作紀錄

## 實作目標
在 `adaptive_summative` (自適應評量與教學頁面) 中，加入具備 RRF 混合檢索 (Hybrid Retrieval) 且會利用 LLM 自動從使用者提問抓取關鍵字的 **Advanced RAG** 輔助功能。這個系統結合了快速通道 (Naive RAG) 與救援通道 (Advanced RAG)。

## 詳細修改過程

### 1. 安裝必要套件
為了賦能 Advanced RAG 需要用到 Hybrid Search (稀疏與稠密檢索結合)，因此利用 pip 安裝了以下套件：
- `sentence-transformers` (用於載入 text2vec-base-chinese 進行中文語義編碼)
- `jieba` (中文斷詞處理，作為 BM25 計算頻率的基礎)
- `rank_bm25` (實作 BM25Okapi 演算法，捕捉確切關鍵字詞)

### 2. 環境與管理員參數設定
**檔案：** `config.py`
加入了 `ADVANCED_RAG_NAIVE_THRESHOLD`（預設 `0.85`）。此參數供管理員調整系統引流走向：數字越小，越容易落入救援通道（進階 RAG）；數字越大，越寬鬆且傾向使用原始快速通道（這將有助於 A/B Testing 確認流量與滿意度）。

### 3. 實作 Core Engine 核心邏輯
**新增檔案：** `core/advanced_rag_engine.py`
實作了進階檢索引擎引擎：
- **`init_adv_rag(app)`**: 使用 `shibing624/text2vec-base-chinese` 完成向量建立獨立的 `ChromaDB` (名稱為 `math_skills_adv`)，並同時針對所有的文檔建構 `BM25Okapi` 的索引。
- **`get_llm_keywords(query)`**: 利用設定好的 Google Gemini 或是預設本地 LLM 引擎，對學生的提問捕捉 3 到 5 個數學專用詞彙，供 Hybrid Retrieval 增強。
- **`extract_advanced_rag()`**: 利用實驗得出的最佳 `K=42` 作為基礎，使用 Reciprocal Rank Fusion (RRF) 來加權稠密檢索以及稀疏檢索的分數，返回更精準的 Top-5 內容。
- **`adv_rag_search()`**: 融合路由機制，當一般檢索 (Naive RAG) 距離分數超過定義的門檻 (即不太相關) 時，觸發進階檢索 (Advanced RAG)，同時附上 Routing 路徑於回傳值中。
- **`adv_rag_chat()`**: 將提取出的五份相關教學對交給 LLM，讓模型依據學生的問題總結為「簡短的小提示與教學」。

### 4. API 路由端點
**修改檔案：** `app.py`、`core/routes/adaptive_api.py`
- 在 `app.py` 底部初始化時掛載 `init_adv_rag(app)`。
- 在 `adaptive_api.py` 處開放了兩個前端可直接使用的接口：`/api/adaptive/adv_rag_search` 與 `/api/adaptive/adv_rag_chat`。

### 5. 前端整合介面
**修改檔案：** `templates/adaptive_practice_v2.html`
在 `ai-assistant-panel` 內注入了 **Advanced RAG** 功能面板。設計樣式為類似原本系統中的 RAG 面板但加強了視覺獨立性。提供一個可自行輸入查詢問題的視窗、點擊檢索時透過 Loading 動畫引導，成功回傳時除了給予可點擊並跳轉至該練習關卡的 5 顆相關推薦按鈕，也會將教學與 AI 微縮課程直接呈現，並能看見當時這組檢索所經過的路由（例如 Fast-Path 或 Advanced Path）。

---

## 🔍 提供給開發者測試用的有效提問範例 (Valid Testing Queries)

因為目前的系統有雙軌介面（基礎練習 `/practice` 與 進階自適應測驗 `/adaptive_summative`），如果你想準確測試點擊單元按鈕後的行為，以下準備了兩組**保證存在於系統中必定能正確載入**的提問情境，請在介面中直接複製貼上測試：

### ✅ 測試組 1：會導向【自適應介面】的進階整合型問題
這類問題觸發的功能單元隸屬於 `adaptive_summative` 專屬題庫（包含動態生成的微技能：如加減法、長除法等）。當你點擊檢索結果時，系統會自動在「目前分頁」前往自適應測驗面版。

*   **提問 A（多項式四則運算）：** 「我不懂多項式除法的時候，如果遇到缺項該怎麼辦？為什麼除出來餘式的次數好像怪怪的？」
*   **提問 B（根式四則運算）：** 「根式在做加減法的時候，裡面的數字跟外面的數字好像都會搞混，什麼時候才能相加？」
*   **提問 C（整數的四則運算）：** 「計算時括號裡面又有括號，到底要先算哪一個？正負號很容易跟著變錯怎麼辦？」

### ✅ 測試組 2：會導向【基礎練習介面】的標準單元問題
這類問題對應的是資料庫中擁有單一獨立考卷的單元（擁有獨自的單一檔案 generators）。如果你將管理員設定為 `practice` 介面並提出以下問題，推薦出的單元點擊後將會順利於規定的 `/practice/` 單一練習中載入完整題目而不會報錯。

*   **提問 D（平方根的意義）：** 「什麼是平方根？我分不清楚正負平方根的差別在哪耶？」
*   **提問 E（分數的乘法）：** 「為什麼分數相乘的時候，分子跟分母要分開乘？可以直接約分嗎？」
*   **提問 F（多項式的加減法）：** 「多項式在相加或相減的時候，要怎麼把同類項合併？常數項跟一次項可以加在一起嗎？」