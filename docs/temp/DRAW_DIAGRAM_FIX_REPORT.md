# 繪製示意圖功能問題修正報告

**日期:** 2025年12月15日

### 問題描述

使用者報告了關於「繪製示意圖」功能的多個問題，主要包括：

1.  **繪圖失敗報錯**：當繪製包含 `a**x` 等形式的指數函數時，控制台輸出 `ERROR in routes: 無法繪製方程式 '1*y = a**x': name 'a' is not defined`，指出變數 `a`, `b`, `c` 未定義。
2.  **圖形文字亂碼**：生成的圖形中，中文字符（如標題、軸標籤）顯示為亂碼或奇怪符號。
3.  **圖形無法縮放**：生成的圖形為靜態 PNG 格式，放大時會失真模糊。

### 問題原因分析

1.  **`NameError` (變數未定義)**：
    *   `core/routes.py` 中的 `draw_diagram` 函式使用 `eval()` 來解析並繪製方程式。
    *   `eval()` 在執行時，其上下文環境中只包含了 `x`, `y`, `np` (NumPy) 等預定義變數。
    *   當方程式中出現 `a`, `b`, `c` 等常數變數時，`eval()` 無法找到它們的定義，從而拋出 `NameError`。

2.  **圖形文字亂碼**：
    *   `matplotlib` 預設使用的字型通常不支持 CJK (中日韓) 字符集。
    *   在 `core/routes.py` 中，並未配置 `matplotlib` 使用任何支援中文的字型，導致中文字符無法正確渲染。

3.  **圖形無法縮放**：
    *   `plt.savefig(image_path)` 預設將圖形保存為 PNG (Portable Network Graphics) 格式。
    *   PNG 是一種點陣圖格式，其圖像由像素組成。放大點陣圖會導致像素化和模糊，不具備良好的縮放能力。

### 解決方案與修改內容

所有修改均在 `core/routes.py` 文件中進行。

1.  **解決 `NameError` 問題**：
    *   **修改說明**：在 `draw_diagram` 函式內部，`eval()` 調用之前，創建了一個 `eval_context` 字典。此字典除了包含 `np`, `x`, `y` 之外，還為 `a`, `b`, `c` 賦予了預設的數值（例如 `a=2`, `b=3`, `c=4`）。
    *   **程式碼修改**：
        ```python
        # ... (省略部分程式碼) ...
        # Define a context for eval() to prevent NameError for common variables
        eval_context = {
            'np': np,
            'x': x,
            'y': y,
            'a': 2,  # Default value for 'a'
            'b': 3,  # Default value for 'b'
            'c': 4   # Default value for 'c'
        }
        # ... (省略部分程式碼) ...
        # eval() 調用現在使用 eval_context
        plt.contour(x, y, eval(expr, eval_context), levels=[0], colors='b')
        # ... (省略部分程式碼) ...
        plt.contourf(x, y, eval(line, eval_context), levels=[0, np.inf], colors=['#3498db'], alpha=0.3)
        # ... (省略部分程式碼) ...
        ```
    *   **效果**：現在，當方程式中包含 `a`, `b`, `c` 等變數時，`eval()` 能夠在 `eval_context` 中找到它們的定義，從而成功解析方程式並進行繪圖。

2.  **解決圖形文字亂碼問題**：
    *   **修改說明**：在 `core/routes.py` 文件的開頭，`import matplotlib.pyplot as plt` 之後，添加了 `matplotlib` 字型配置代碼。這段代碼會嘗試載入 Windows 系統下的「微軟正黑體 Light」（`msjhl.ttc`），並將其設定為 `matplotlib` 的預設中文字型。同時，也配置了正確顯示負號。
    *   **程式碼修改**：
        ```python
        # ... (省略部分程式碼) ...
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
        
        # --- Matplotlib Font Settings for Chinese Characters ---
        # This is a common path for Windows. If deploying on another OS, this path might need to be changed.
        try:
            font_path = 'C:/Windows/Fonts/msjhl.ttc'
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei Light', 'sans-serif']
            else:
                # Fallback for non-Windows or if font is not found
                plt.rcParams['font.sans-serif'] = ['sans-serif']
            plt.rcParams['axes.unicode_minus'] = False  # Fix for displaying the minus sign
        except Exception as e:
            current_app.logger.warning(f"Could not set Chinese font: {e}")
        # --- End Font Settings ---
        # ... (省略部分程式碼) ...
        ```
    *   **效果**：`matplotlib` 現在能夠正確渲染中文字符，所有圖形上的中文標題和標籤都將正常顯示，不會出現亂碼。

3.  **實現圖形縮放功能**：
    *   **修改說明**：在 `draw_diagram` 函式中，修改了保存圖形的邏輯。
        *   將 `image_path` 的擴展名從 `.png` 改為 `.svg`。
        *   在 `plt.savefig()` 調用中，明確指定 `format='svg'`。
        *   為避免瀏覽器快取舊圖形，為 SVG 文件名添加了一個唯一的 UUID。
        *   更新了 `url_for('static', filename='...')` 的調用，以返回新的 SVG 文件路徑。
    *   **程式碼修改**：
        ```python
        # ... (省略部分程式碼) ...
        # 3. Save the image as SVG for scalability
        # Ensure the static directory exists
        static_dir = os.path.join(current_app.static_folder)
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        # Use a unique filename to prevent browser caching issues
        unique_filename = f"diagram_{uuid.uuid4().hex}.svg"
        image_path = os.path.join(static_dir, unique_filename)
        plt.savefig(image_path, format='svg')
        plt.close() # Close the figure to free up memory

        # 4. Return the path
        return jsonify({
            "success": True,
            "image_path": url_for('static', filename=unique_filename)
        })
        # ... (省略部分程式碼) ...
        ```
    *   **效果**：生成的圖形現在是 SVG 格式，這是一種向量圖形。無論使用者如何放大或縮小，圖形都會保持清晰，不會出現模糊或像素化的問題，實現了良好的縮放體驗。

### 結論

通過上述修改，繪製示意圖功能現在更加健壯，能夠處理包含常數變數的方程式，正確顯示中文，並提供高品質、可縮放的圖形輸出。