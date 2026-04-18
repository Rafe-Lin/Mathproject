# 智學AIGC賦能平台 (Smart-Edu AIGC Platform)
## 🚀 AI 賦能的自適應內容生成引擎 (AI-Enabled Adaptive Content Generation Engine)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask-green)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%20Pro%20%2F%20Vision-orange)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"不是取代教師，而是賦予教育無限可能。"**
> **"Not replacing teachers, but empowering education with infinite possibilities."**

---

## 📖 專案執行摘要 (Executive Summary)

**智學AIGC賦能平台** 是一個專為「智慧校園」打造的教育科技解決方案，致力於解決數位教材匱乏與學習落差兩大痛點。我們運用最先進的 **Generative AI (Google Gemini)** 技術，打造了一條全自動化的內容生成流水線 (Content Pipeline)，能夠將傳統的 PDF/Word 教科書瞬間轉化為結構化的數位資產與 Python 演算法題庫。

針對高中職數學學習弱勢群體，本系統提供了一個**多模態、具備感知能力的 AI 數位家教**。它不僅能透過手寫辨識 (OCR) 看懂學生的計算過程，更能進行 **「解題三部曲 (Pedagogical Trilogy)」** 引導，幫助學生跨越及格門檻，重拾學習信心。

### 📚 完整系統文件索引

*   **[整體架構 (SECG)](docs/後臺系統分析/(平台架構)Smart-Edu%20Content%20Generator%20(SECG).md)**：全系統技術藍圖。
*   **[軟體設計文件 (SDD)](docs/軟體設計文件%20(SDD).md)**：詳細實作規格與資料庫設計。
*   **模組文件**：
    *   [模組一：教材數位化](docs/後臺系統分析/(模組一)textbook_importer.md)
    *   [模組二：題庫程式化](docs/後臺系統分析/(模組二)sync_skills_files.md)
    *   [模組三：教學引導](docs/後臺系統分析/(模組三)enrich_skills.md)
    *   [模組四：知識圖譜](docs/後臺系統分析/(模組四)auto_build_prerequisites.md)
    *   [單元-題型-技能檔架構](docs/UNIT_PATTERN_ARCHITECTURE.md)（一題型一 skill 檔、單元出題）

**🏆 競賽組別**：育秀盃 AI 應用類——AI 賦能永續未來

---

## 🌟 核心價值與痛點解決 (Value Proposition)

### 1. 對學校與教師：教材數位化不再是惡夢
*   **痛點**: 傳統題庫建置耗時費力，數位教材難以跟上課綱更新。
*   **解法**: **「AI 自動生成引擎」**。上傳課本，AI 自動拆解章節、提取例題、甚至自動撰寫出題程式碼。
*   **效益**: 備課時間減少 90%，實現「教材即程式 (Content as Code)」的永續管理。

### 2. 對學生：擁有一個 24 小時的私人家教
*   **痛點**: 數學跟不上進度，不敢問老師，刷題只有對錯沒有詳解。
*   **解法**: **「智慧適性化練習介面」**。AI 能「看見」你的手寫筆跡，分析圖形，並像真人老師一樣引導你思考，而不是直接給答案。
*   **效益**: 個別化補救教學，精準診斷學習斷點 (Learning Gaps)。

### 3. 對環境與永續：SDGs 4 優質教育
*   **痛點**: 紙張浪費，城鄉教育資源不均。
*   **解法**: 全數位化流程，無紙化測驗，且透過 AI 降低高品質教材的製作門檻，讓偏鄉也能享有頂尖的教學資源。

---

## 🏗️ 系統架構與關鍵模組 (System Architecture)

本系統由四大核心 AI 模組與一個智慧互動介面組成：

### 🔄 模組一：教材數位化引擎 (Textbook Importer)
*   **功能**: 處理非結構化文件 (PDF/Word)。
*   **技術**: **Async Pipeline** (非同步佇列) + **Retry Mechanism** (自動重試) + 混合 OCR。
*   **產出**: 結構化的章節資料庫與標準例題集。

### 💻 模組二：題庫自動程式化 (Auto-Code Sync)
*   **功能**: 將靜態題目轉化為無限變化的演算法題庫。
*   **技術**: **Strict Prompting** + **AST Self-Healing** 流水線，確保 AI 生成的 Python 程式碼 100% 可執行且零語法錯誤。
*   **產出**: 可執行的 Python 題庫腳本 (`skills/*.py`)，實現 **Code-as-Content**。

### 🎓 模組三：教學引導增強 (Pedagogical Enricher)
*   **功能**: 為每道題目生成「蘇格拉底式」引導語。
*   **技術**: **Pedagogical Trilogy** (啟動-策略-檢查) + **SQLite WAL Mode** (高併發穩定)。
*   **產出**: 具備教學靈魂的 AI 提示詞庫。

### 🕸️ 模組四：知識圖譜建構 (Knowledge Graph Builder)
*   **功能**: 分析技能間的依賴關係，建構跨學制 (國中 -> 高中) 學習地圖。
*   **技術**: **Context Injection** (閱讀詳解) + **Token Optimization**，精準挖掘隱性依賴。
*   **產出**: 適性化推薦路徑圖，支援「向下診斷 (Adaptive Remediation)」。

---

## 🎨 智慧適性化練習介面 (Intelligent Adaptive Interface)

這是學生最常接觸的核心介面，具備以下未來科技特色：

1.  **即時上下文感知 (Context Awareness)**:
    *   AI 不再盲聊，它知道你現在正在寫哪一題、圖形長什麼樣子、正確答案是什麼。
2.  **多模態輸入 (Multi-modal Input)**:
    *   **手寫辨識**: 直接在螢幕上列式，AI 看得懂你的筆跡。
    *   **作圖題判斷**: 畫出二次函數或向量，AI 能視覺化判斷圖形正確性。
3.  **深度錯誤分析 (Deep Error Analysis)**:
    *   精確指出是「計算錯誤」還是「觀念錯誤」，並定位到具體的錯誤步驟 (Node)。
4.  **跨平台無障礙 (Cross-Platform)**:
    *   Web-based 設計，無需安裝 App，平板、電腦、手機皆可流暢使用。

---

## 🛠️ 技術堆疊 (Tech Stack)

*   **Backend**: Flask 2.0+, Python 3.9+
*   **Database**: SQLite (WAL Mode enabled)
*   **Document Processing**: clean_pandoc (LaTeX Cleaning)
*   **AI Engine**: Google Gemini Pro 1.5 / Gemini Vision
*   **Frontend**: HTML5, Bootstrap 5, Vanilla JS (ES6+)
*   **Math Rendering**: MathJax 3.x
*   **Visualization**: Matplotlib, SVG Dynamic Generation

---

## 🚀 快速開始 (Getting Started)

### 1. 環境準備
請確保已安裝 Python 3.9+ 與 Git。

```bash
# Clone 專案
git clone https://github.com/your-repo/math-master.git
cd math-master

# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 設定配置
複製 `.env.example` 為 `.env` 並填入您的 API Key：
```bash
GEMINI_API_KEY=your_google_ai_studio_key
SECRET_KEY=your_flask_secret_key
```

### 3. 初始化並啟動
```bash
# 初始化資料庫
python utils/init_db.py

# 啟動應用
python app.py
```
瀏覽器打開 `http://127.0.0.1:5000` 即可開始體驗。

---

## 🗺️ 發展藍圖 (Roadmap)

*   **Phase 1 (目前階段)**: 完成四大 AI 模組開發，實現數學科自動出題與基本手寫批改。
*   **Phase 2**: 擴充至物理、化學學科 (只需替換 System Prompt)。
*   **Phase 3**: 導入語音互動 (STT/TTS)，實現真正的「口說教學」互動。
*   **Phase 4**: 商業化 API 輸出，對接現有 LMS (Moodle, Google Classroom)。

---

## 📄 授權與聯繫 (License & Contact)

本專案採用 **MIT License** 開源授權，歡迎教育工作者與開發者共同參與貢獻。

*   **專案負責人**: [Your Name/Team Name]
*   **聯繫信箱**: contact@smart-edu.ai
*   **完整文件**: 請參閱 `docs/` 目錄下的 [軟體設計文件 (SDD)](docs/軟體設計文件%20(SDD).md)

---
*Built with ❤️ for the future of education.*

---

## Simulation-Based Ablation Experiment

This repo now includes a simulation framework for comparing three teaching control strategies:

* `AB1`: always assign polynomial questions, with no remediation.
* `AB2`: after 2 consecutive polynomial failures, diagnose integer weakness, remediate with exactly 3 integer questions, then return to polynomial.
* `AB3`: after 2 consecutive polynomial failures, diagnose integer weakness, remediate on integer until return-readiness is satisfied.

### Model assumptions

* Student ability vector: `integer`, `fraction`, `radical`, `polynomial`
* IRT-style success probability: `P(correct) = 1 / (1 + exp(-6(A_eff - D)))`
* Effective ability for polynomial: `A_eff = 0.7 * A_polynomial + 0.3 * A_integer`
* Effective ability for integer: `A_eff = A_integer`
* Ability update: `Delta A_s = 0.08 * w(q,s) * (0.8 + 0.4D) * r`
* Correct reward: `r = 1.0`
* Incorrect reward: `r = 0.3`
* Same-skill weight: `w = 1.0`
* Integer to polynomial transfer: `w = 0.2`
* Other unrelated skills: `w = 0`

### Extensible interfaces

The experiment core is designed so diagnosis and decision logic can be swapped later:

* `DiagnosisStrategy`: current implementation is `FixedIntegerDiagnosis`
* `DecisionPolicy`: current implementations are rule-based `AB1Policy`, `AB2Policy`, `AB3Policy`

This keeps the simulation loop reusable when replacing the current logic with RAG-based diagnosis or PPO-based routing.

### How to run

```bash
python scripts/run_ablation_experiment.py
```

Optional flags:

```bash
python scripts/run_ablation_experiment.py --episodes 100 --max-steps 30 --seed 42 --output-dir outputs
```

### Output files

Running the script writes:

* `outputs/experiment_logs.csv`: per-step simulation logs for every controller / prototype / episode
* `outputs/summary_metrics.csv`: aggregated metrics by controller and prototype
* `outputs/config_used.json`: exact config used for the run
* `outputs/plots/success_rate.png`: success-rate comparison
* `outputs/plots/total_steps.png`: average steps comparison
* `outputs/plots/fail_streak.png`: average maximum polynomial fail streak comparison
* `outputs/plots/sample_trajectory.png`: sample polynomial ability trajectory for one episode per controller / prototype

### Metrics

* `success_rate`: share of episodes that reached the polynomial success condition before max steps
* `avg_total_steps`: average number of steps used per episode
* `avg_max_polynomial_fail_streak`: average worst consecutive polynomial failure streak within an episode
* `avg_remediation_entries`: average number of times the controller entered remediation
* `avg_integer_gain`: average final integer ability minus initial integer ability
* `avg_polynomial_gain`: average final polynomial ability minus initial polynomial ability

### Episode success condition

By default, an episode is marked successful when:

* current question is polynomial
* the answer is correct
* `A_polynomial >= 0.8`
* the student has answered at least 2 consecutive polynomial questions correctly

If success is not reached, the episode stops at `--max-steps`.

## 如何使用 Codex（最小流程）

1. 先 `audit`：先做一致性檢查，找斷點與風險，不先大改。
2. 再 `patch`：每次只做一件事，採最小修改面。
3. 每次修改後做最小驗證：確認影響範圍、關鍵輸出與 runtime 安全。
4. 全程遵守 [AGENTS.md](AGENTS.md)。

建議搭配 `docs/codex_prompts/` 的模板使用：
- `audit_prompt.md`
- `patch_prompt.md`
- `debug_prompt.md`
- `test_prompt.md`
- `safe_patch_prompt.md`
