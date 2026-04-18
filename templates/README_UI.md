# Math Master AI - V2.0 介面設計規範說明書

## 一、 核心設計宗旨
本專案 V2.0 採用「組件化」與「標準化」設計。為解決各管理頁面外觀差異問題，所有介面開發必須以 `admin_curriculum.html` 為視覺與結構之唯一基準。目標是達成在切換頁面時，導航與篩選區塊在視覺上達到「完全重合、靜止不動」的專業效果。

---

## 二、 視覺標準規範 (Visual Standards)

### 1. 全局排版
* **字體族群**：`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif`。
* **背景底色**：全站背景統一為 `#f5f7fa` (淡灰色)。
* **內容寬度**：`.container` 最大寬度設定為 `1400px`。

### 2. 精細化字型規格 (FontSize Specs)
* **篩選器標籤 (Labels)**：統一為 `0.85rem` (約 13.6px)，字重 `600`。
* **下拉選單文字 (Select Text)**：統一為 `0.9rem` (約 14.4px)，避免字體過大導致的臃腫感。
* **組件標題 (Header Text)**：如「課程篩選器」字體為 `0.95rem`，顏色 `#2c3e50`。
* **正文內容**：統一為 `1rem` (16px)。

### 3. 色彩與間距系統
* **導航欄 (Navbar)**：背景 `#2c3e50`，文字為白色。
* **功能按鈕**：
    * **新增 (Add)**：`#27ae60` (綠色)，內距 `12px 25px`。
    * **編輯 (Edit)**：`#3498db` (藍色)。
    * **刪除 (Delete)**：`#e74c3c` (紅色)。
* **選單間距 (Padding)**：下拉框內距統一設為 `6px 10px`，以維持精緻的視覺感。

---

## 三、 組件與數據規範 (Components & Data)

### 1. 課程篩選器 (`_filter_sidebar.html`)
* **外觀要求**：純白卡片背景，**絕對禁止使用深色底框**。
* **對齊方式**：「課程篩選器」標題必須**絕對靠左對齊**。
* **交互行為**：選單改變後自動觸發 `window.location.href` 跳轉，並透過 `handle_curriculum_filters` 處理狀態記憶。

### 2. 數據表格與分頁
* **表格表頭**：背景 `#34495e`，文字白色加粗。
* **分頁邏輯**：翻頁 URL 必須使用 `**dict(request.args.to_dict(), page=n)` 以覆蓋並保留所有過濾參數。

---

## 四、 已導入此規範之程式清單
1. `admin_curriculum.html` (視覺基準)
2. `admin_skills.html` (技能管理)
3. `admin_examples.html` (例題管理)
4. `admin_prerequisites.html` (前置技能管理)

---

## 五、 開發者視覺對齊 Prompt (Style Master Prompt V2.1)
若需開發新功能，請輸入此指令：

> **任務：** 開發符合 V2.0 規範的 `[功能名稱]` 模組。
> 
> **視覺對齊要求：** > * 以 `admin_curriculum.html` 為唯一基準。
> * 標籤字體 `0.85rem`，選單字體 `0.9rem`，內距 `6px 10px`。
> * 標題靠左對齊，禁用深色背景 Header。
> * 必須使用 `_filter_sidebar.html` 組件並介接 `handle_curriculum_filters`。
> 
> **數據規範：** > * 傳遞變數名稱固定為 `filters` 與 `selected_filters`。
> * 分頁翻頁必須確保攜帶 `request.args` 以維持過濾狀態。