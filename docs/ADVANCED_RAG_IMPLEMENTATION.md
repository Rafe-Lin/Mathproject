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

## 可以用來測試的學生提問建議 (3題)

建議可以複製以下文字至介面右下方的「Advanced RAG 模式」內進行搜尋測試：

> **測試題 1（針對多項式長除法的觀念）：**
> 「我不懂多項式除法的時候，如果遇到缺項該怎麼辦？為什麼除出來餘式的次數好像怪怪的？」
> *預期：系統能截取出長除法、缺項等字眼，並推斷包含「多項式長除法（商與餘式）」知識點。*

> **測試題 2（針對括號開展與乘法公式的綜合應用）：**
> 「為什麼我算 $(2x-3)^2$ 的時候，不能直接把平方丟進去變成 $4x^2 - 9$？中間的東西怎麼來的？」
> *預期：系統能夠精準打中乘法公式（和的平方 / 差的平方）、多項式展開等教材。*

> **測試題 3（針對文字敘述轉代數式的應用）：**
> 「如果有一個梯形，上底是 $3x+2$，下底是 $x-4$，高是 $4x$，這樣它的面積要怎麼展開？我不知道什麼時候要加括號。」
> *預期：這會測試系統對「幾何/複合圖形」與「單項式乘多項式」在自然語言情境的提取準確度。*
> (測試整數負數觀念)：「在做整數運算的時候，括號前面如果是負號，打開括號要怎麼變號？」
> (測試一元一次方程式)：「我要怎麼解一元一次方程式？把數字移到等號另一邊的時候是不是要變號？」
> (測試分數運算通分)：「分數相加減如果兩張牌的分母不一樣，要怎麼算？是不是要先通分？」