# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/textbook_processor.py
功能說明 (Description): 課本處理與 AI 分析模組，負責從 PDF 或 Word 檔案中自動提取課程結構與內容，並整合 Gemini LLM 進行智能分析與資料庫匯入。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""
課本處理與 AI 分析模組 (Textbook Processor & AI Analyzer) - Final Complete Version

本模組負責從教科書（PDF 或 Word 檔案）中自動提取課程結構、章節、小節、核心觀念，
並透過 Google Gemini LLM 進行智能分析，最終將結構化資料存入資料庫。

版本特點：
1. 完整保留原有的錯誤處理、備用解析與輔助函式 (Restore full logic)。
2. 新增針對 Word/Pandoc 的清洗邏輯 (clean_pandoc_output)。
3. 更新普高龍騰版 Prompt (扁平化結構)。
"""

import json
import re
import os
# import fitz  # PyMuPDF -> Moved to inside function
import time
import io
# import pypandoc -> Moved to inside function
# from pypandoc.pandoc_download import download_pandoc
from google.api_core.exceptions import ResourceExhausted
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.ai_analyzer import get_model
from flask import current_app
import traceback
from core.code_generator import auto_generate_skill_code

# (初始化檢查已移除)

# ==============================================================================
# [保留] 您原本的 LaTeX 通用修復函式
# ==============================================================================
def fix_common_latex_errors(text):
    """
    修復 AI/Pandoc 轉換後常見的 LaTeX 語法錯誤與符號遺漏 (增強版)
    包含：三角函數正體化、希臘字母、集合符號、向量、下標處理。
    """
    if not text: return text
    
    # 0. 基礎清理
    text = text.replace('＝', '=').replace('－', '-').replace('，', ',')
    text = re.sub(r'(\S)\s*\$\$', r'\1', text)
    text = text.replace('*e*', 'e')
    text = re.sub(r'(?<!\\)->', r' \\to ', text)
    text = re.sub(r'(?<!\\)infty(?![a-zA-Z])', r'\\infty', text)

    # 1. 函數名稱正體化 (Trig & Log)
    funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp']
    pattern_funcs = r'(?<!\\)\b(' + '|'.join(funcs) + r')\b'
    text = re.sub(pattern_funcs, r'\\\1', text)
    text = re.sub(r'\\(sin|cos|tan|log|ln)\(', r'\\\1 (', text) # 修復黏連

    # 2. 希臘字母獨立修復
    greeks = ['alpha', 'beta', 'gamma', 'delta', 'theta', 'lambda', 'mu', 'pi', 'sigma', 'omega', 'phi', 'rho', 'tau', 'Delta', 'Sigma']
    pattern_greeks = r'(?<!\\)\b(' + '|'.join(greeks) + r')\b(?![a-zA-Z])'
    text = re.sub(pattern_greeks, r'\\\1', text)

    # 3. 集合與邏輯
    sets = ['subset', 'subseteq', 'cup', 'cap', 'emptyset', 'forall', 'exists']
    for s in sets: text = re.sub(rf'(?<!\\)\b{s}\b', rf'\\{s}', text)
    text = re.sub(r'\s+in\s+', r' \\in ', text)

    # 4. Lim, Sqrt, Frac (標準修復)
    text = re.sub(r'lim_\{n\s*(?:\\to|->)\s*(?:\\)?infty\}', r'\\lim_{n \\to \\infty}', text)
    text = re.sub(r'(?<!\\)lim(?![a-zA-Z])', r'\\lim', text)
    text = re.sub(r'(?:\\)?sqrt\s*(\d+|[a-zA-Z])', r'\\sqrt{\1}', text)
    text = re.sub(r'(?<![a-zA-Z\\])sqrt(?![a-zA-Z0-9\{])', r'\\sqrt', text)
    text = re.sub(r'frac(\d+)(\d+)', r'\\frac{\1}{\2}', text)

    # 5. 向量 (Vectors)
    text = re.sub(r'vec([A-Z]{2})', r'\\overrightarrow{\1}', text) # vecAB -> \overrightarrow{AB}
    text = re.sub(r'vec\s*([a-z])\b', r'\\vec{\1}', text)

    # 6. 常見符號
    text = re.sub(r'(\d+)\s*circ', r'\1^{\\circ}', text)
    text = re.sub(r'angle([A-Z0-9]{2,3})', r'\\angle \1', text)
    for op in ['pm', 'times', 'div', 'approx', 'leq', 'geq', 'neq']:
        text = re.sub(rf'(?<![a-zA-Z\\]){op}(?![a-zA-Z])', rf'\\{op}', text)

    # 7. 次方與下標 (Superscript & Subscript)
    text = re.sub(r'(?<!\$)\b((\w+|\([^)]+\))\^(\{[\w-]+\}|[\w-]+))\b(?!\$)', r'$\1$', text) # x^2 -> $x^2$
    text = re.sub(r'(?<!\$)\b([a-zA-Z])_(\{[\w-]+\}|[\w]+)\b(?!\$)', r'$\1_{\2}$', text)   # a_n -> $a_{n}$
   
    # 4. 修正常見 OCR/Pandoc 錯誤
    replacements = {
            '\\[': '$$', '\\]': '$$',  # 將 \[ \] 統一轉為 $$
            '\\(': '$', '\\)': '$',    # 將 \( \) 統一轉為 $
            '＊': '*',                 # 全形轉半形
            '＋': '+',
            '－': '-',
            '＝': '=',
            '／': '/', 
            'div ': '\\div '           # 常見錯誤：div 沒加斜線
        }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# ==============================================================================
# [NEW] 專用清洗函式：只針對 Word (Pandoc) 輸出的文字做處理
# ==============================================================================
def clean_pandoc_output(text):
    """
    【龍騰版/Word專用】針對 Pandoc 轉換 Word 檔後的特殊格式進行清洗。
    此函式只會被 .docx 流程呼叫，絕對不會影響 PDF/OCR 流程。
    """
    if not text: return text

    # 1. 修復 Pandoc 產生的雙重上標度數符號 (^{\^{\circ}} -> ^{\circ})
    text = text.replace(r'^{\^{\circ}}', r'^{\circ}')
    
    # 2. 統一將 \( ... \) 轉換為 $ ... $ (MathJax 更支援)
    # 這是 Word 轉出的標準 LaTeX 行內數式格式，但在前端顯示時 $ 比較通用
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)

    # 3. 修復 sqrt (Pandoc 有時會輸出 sqrt 2 而不是 \sqrt{2})
    # 這裡只做最保守的修復，避免誤傷文字
    text = re.sub(r'(?:\\)?sqrt\s+(\d+|[a-zA-Z])\b', r'\\sqrt{\1}', text)
    
    return text

def process_textbook_file(file_path, curriculum_info, queue, skip_code_gen=False):
    """
    主流程函式，包含完整的 try...except 錯誤處理。
    
    Args:
        file_path: 課本檔案路徑
        curriculum_info: 課綱資訊字典
        queue: 訊息佇列
        skip_code_gen: 若為 True，則跳過自動生成 Python 出題程式碼（預設 False）
    """

    try:
        # ======================================================
        # [NEW] 防呆：檢查是否為 Word 暫存鎖定檔 (以 ~$ 開頭)
        # ======================================================
        filename = os.path.basename(file_path)
        if filename.startswith("~$"):
            message = f"偵測到 Word 暫存鎖定檔 ({filename})，自動跳過不處理。"
            current_app.logger.warning(message)
            if queue:
                queue.put(f"WARN: {message}")
            return {"status": "skipped", "message": message}
        # ======================================================

        # 步驟 1: 從 PDF/Word 提取內容
        content_by_page = extract_content_from_file(file_path, queue)

        if not content_by_page:
            message = "檔案內容為空或提取失敗，終止處理。"
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {"status": "error", "message": "無法從檔案中提取任何內容。"}

        # 步驟 2: 呼叫 AI 進行分析
        ai_json_result_string = call_gemini_for_analysis(content_by_page, curriculum_info, queue)
        # 步驟 3: 解析 AI 回傳的 JSON 字串
        parsed_data = parse_ai_response(ai_json_result_string, queue)
        if not parsed_data:
            return {"status": "error", "message": "AI 回傳的資料格式有誤或為空，無法解析。"}

        # 步驟 4: 將解析後的資料存入資料庫
        result = save_to_database(parsed_data, curriculum_info, queue)

        skills_count = result.get('skills_processed', 0)
        curriculums_count = result.get('curriculums_added', 0)
        examples_count = result.get('examples_added', 0)
        processed_skill_ids = result.get('processed_skill_ids', [])

        message = (f"課本處理完成。新增/更新 {skills_count} 個技能，建立 {curriculums_count} 筆課程綱要，匯入 {examples_count} 個例題。")
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")

        # 步驟 5: 自動生成出題程式碼 (可選)
        code_gen_status = "已跳過"
        if skip_code_gen:
            message = "使用者選擇跳過程式碼生成，稍後可透過後台腳本批次生成。"
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")
        elif processed_skill_ids:
            queue.put(f"INFO: 開始自動生成 {len(processed_skill_ids)} 個技能的出題程式...")
            for idx, skill_id in enumerate(processed_skill_ids):
                queue.put(f"INFO: [{idx+1}/{len(processed_skill_ids)}] 正在生成 {skill_id}.py ...")
                try:
                    # [修正] 針對新匯入的技能，強制執行 Architect 生成最新的 Prompt
                    success, msg = auto_generate_skill_code(skill_id, queue, force_architect_refresh=True)
                    if success:
                        queue.put(f"INFO: {skill_id} 生成成功！")
                    else:
                        queue.put(f"WARN: {skill_id} 生成失敗，跳過。")
                except Exception as e:
                    queue.put(f"ERROR: 生成 {skill_id} 時發生未預期錯誤: {e}")
                    current_app.logger.error(f"Generate Error {skill_id}: {e}")
                
                time.sleep(2) # Rate Limit
            code_gen_status = f"{len(processed_skill_ids)} 個"

        return {
            "status": "success", 
            "message": (f"課本分析與匯入成功！\n"
                        f"新增/更新技能: {skills_count} 個\n"
                        f"新增課程綱要: {curriculums_count} 筆\n"
                        f"新增課本例題: {examples_count} 筆\n"
                        f"自動生成程式碼: {code_gen_status}")
        }

    except Exception as e:
        current_app.logger.error(f"處理課本時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"處理失敗: {str(e)}"}

# --- 向下相容的別名 ---
process_textbook_pdf = process_textbook_file

def extract_content_from_file(file_path, queue):
    """
    從檔案中提取內容，支援 PDF (OCR) 和 Word (Pandoc) 格式。
    (包含防崩潰處理：將所有 Import 與邏輯包覆在 try-except 中)
    """
    message = f"正在從 {file_path} 提取內容..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    content_by_page = {}
    
    try:
        # 將可能的危險 Import 移至函式內部，避免 Module Level 崩潰
        import fitz  # PyMuPDF
        import pypandoc
        from PIL import Image
        import pytesseract
        
        # Wand 是一個常見的缺失套件，特別處理
        try:
            from wand.image import Image as WandImage
        except ImportError:
            WandImage = None

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            # --- PDF 處理邏輯 (維持原樣) ---
            ocr_import_error_logged = False
            tesseract_not_found_error_logged = False
            doc = fitz.open(file_path)
            for i, page in enumerate(doc.pages()):
                page_text = page.get_text("text")

                # 偵測大字體標題
                blocks = page.get_text("blocks")
                large_font_texts = []
                large_font_threshold = 20
                for b in blocks:
                    try:
                        text = b[4]
                        first_line = page.get_text("dict", clip=b[:4])['blocks'][0]['lines'][0]
                        font_size = first_line['spans'][0]['size']
                        if font_size > large_font_threshold:
                            large_font_texts.append(text.strip())
                    except (IndexError, KeyError):
                        continue
                for large_text in large_font_texts:
                    if large_text and large_text not in page_text:
                        page_text = large_text + "\n" + page_text

                # OCR 處理
                try:
                    from pytesseract import TesseractNotFoundError

                    tesseract_path = current_app.config.get('TESSERACT_CMD')
                    if tesseract_path:
                        pytesseract.pytesseract.tesseract_cmd = tesseract_path

                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='chi_tra')
                    page_text += "\nOCR Extracted: " + ocr_text.strip()
                except ImportError:
                    if not ocr_import_error_logged:
                        message = "無法執行 OCR，缺少 'pytesseract' 或 'Pillow' 套件。"
                        current_app.logger.warning(message)
                        queue.put(f"WARN: {message}")
                        ocr_import_error_logged = True
                except TesseractNotFoundError:
                    if not tesseract_not_found_error_logged:
                        message = "無法找到 Tesseract-OCR 引擎，請確保已正確安裝。"
                        current_app.logger.error(message)
                        queue.put(f"ERROR: {message}")
                        tesseract_not_found_error_logged = True
                except Exception as ocr_e:
                    current_app.logger.warning(f"頁 {i+1} OCR 處理時發生錯誤: {ocr_e}")

                content_by_page[i + 1] = page_text
            doc.close()

        elif file_extension in ['.docx', '.doc']:
            # --- Word (.docx) 處理邏輯 (使用 Pandoc) ---
            message = "偵測到 Word (.docx) 檔案，使用 Pandoc 轉換以保留數學公式..."
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")

            try:
                # 建立一個暫存資料夾來存放從 Word 中提取的圖片
                temp_media_dir = os.path.join(os.path.dirname(file_path), "media")
                os.makedirs(temp_media_dir, exist_ok=True)

                # 設定 Pandoc 參數
                extra_args = [
                    '--wrap=none',
                    f'--extract-media={temp_media_dir}'
                ]

                # 執行轉換
                markdown_output = pypandoc.convert_file(file_path, 'markdown', extra_args=extra_args)

                # 呼叫專用清洗函式
                markdown_output = clean_pandoc_output(markdown_output)

                # --- 圖片 OCR 邏輯 ---
                # (局部函式：需要使用外層的 WandImage)
                def ocr_image_and_replace(match):
                    image_path_in_md = match.group(1)
                    from urllib.parse import unquote
                    image_path_in_md = unquote(image_path_in_md)
                    
                    full_image_path = os.path.join(os.path.dirname(file_path), image_path_in_md)

                    if os.path.exists(full_image_path):
                        try:
                            image_to_ocr_path = full_image_path
                            # 在 OCR 前先轉換 WMF/EMF 檔案
                            if full_image_path.lower().endswith(('.wmf', '.emf')):
                                if WandImage is None:
                                    queue.put(f"WARN: 略過 WMF/EMF 圖片轉換 ({image_path_in_md})，因為系統未安裝 Wand/ImageMagick。")
                                    return match.group(0) # 保持原樣

                                png_path = os.path.splitext(full_image_path)[0] + '.png'
                                try:
                                    with WandImage(filename=full_image_path) as img:
                                        img.format = 'png'
                                        img.save(filename=png_path)
                                    image_to_ocr_path = png_path
                                except Exception as wand_e:
                                    queue.put(f"WARN: 轉換圖片 {image_path_in_md} 失敗: {wand_e}")
                                    return match.group(0)

                            tesseract_path = current_app.config.get('TESSERACT_CMD')
                            if tesseract_path:
                                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                            
                            img = Image.open(image_to_ocr_path)
                            ocr_text = pytesseract.image_to_string(img, lang='chi_tra')
                            return f" {ocr_text.strip()} "
                        except Exception as ocr_e:
                            queue.put(f"WARN: OCR 辨識圖片 '{image_path_in_md}' 失敗: {ocr_e}")
                    
                    return match.group(0)

                # 使用 Regex 替換 Markdown 圖片標記
                final_output = re.sub(r'!\[.*?\]\((.*?)\)', ocr_image_and_replace, markdown_output)
                content_by_page[1] = final_output

            except (OSError, RuntimeError) as e:
                error_str = str(e)
                # 針對損壞檔案或鎖定暫存檔的特定錯誤處理 (Exit Code 63)
                if 'exitcode "63"' in error_str or 'Did not find end of central directory' in error_str:
                    warn_msg = f"WARN: 檔案似乎已損壞或非有效的 Word 檔 (Pandoc Exit 63)，已略過處理。"
                    current_app.logger.warning(warn_msg)
                    queue.put(warn_msg)
                    return {}
                
                error_msg = f"錯誤：Pandoc 執行失敗 ({e})。請確認 Pandoc 已安裝，且若需轉換圖片格式，可能需要安裝 ImageMagick。"
                current_app.logger.error(error_msg)
                queue.put(f"ERROR: {error_msg}")

        else:
            message = f"不支援的檔案類型: {file_extension}。目前僅支援 .pdf 和 .docx。"
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {}

        message = f"成功從 {file_extension} 檔案中提取了 {len(content_by_page)} 頁/區塊內容。"
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")
        return content_by_page

    except Exception as e:
        message = f"提取檔案內容時發生嚴重錯誤 (Exception): {e}"
        current_app.logger.error(message)
        import traceback
        traceback.print_exc()
        queue.put(f"ERROR: {message}")
        return {}

def _sanitize_and_parse_json(s: str, queue=None):
    """
    嘗試多種方式消毒並解析 AI 回傳的 JSON 字串。
    會回傳 (parsed_obj, used_candidate_str, original_raw_str, attempts_list)
    """
    if not s:
        return None, "", s, []

    original = s
    
    # ===== 第 0 步：先記錄原始回應的詳細資訊 =====
    current_app.logger.debug(f"[JSON_DEBUG] 原始回應長度: {len(s)} 字符")
    
    # ===== 第 1 步：移除 code fence wrapper =====
    s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s, flags=re.MULTILINE).strip()
    
    # ===== 第 2 步：移除或規範化控制字元 =====
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    
    # ===== 第 3 步：處理可能的 BOM =====
    if s.startswith('\ufeff'): s = s[1:]
    
    # ===== 第 4 步：嘗試多種反斜線修復策略 =====
    candidates = []
    
    # 策略 0: 原始（僅移除 control chars / fences）
    candidates.append(("原始無修改", s))
    
    # 策略 1: 保守性 escape - 只將後面不是合法 JSON escape 的反斜線 escape
    escaped_conservative = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    candidates.append(("保守 escape", escaped_conservative))
    
    # 策略 2: 激進 escape - 所有孤立反斜線都雙倍
    escaped_aggressive = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', s)
    candidates.append(("激進 escape", escaped_aggressive))
    
    # 策略 3: 最後保底 - 所有反斜線都雙倍
    escaped_brutal = s.replace('\\', '\\\\')
    candidates.append(("暴力 escape", escaped_brutal))
    
    # 策略 4: 嘗試找到第一個 { 和最後一個 } 的子串
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        substr = s[first_brace:last_brace + 1]
        candidates.append(("提取 {} 子串", substr))
        candidates.append(("提取 {} 子串 + 保守 escape", re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', substr)))

    attempts = []
    for strategy_name, cand in candidates:
        try:
            obj = json.loads(cand)
            current_app.logger.info(f"[JSON_SUCCESS] 使用策略 '{strategy_name}' 成功解析 JSON")
            return obj, cand, original, attempts
        except json.JSONDecodeError as e:
            snippet = (cand[:200] + '...') if len(cand) > 200 else cand
            error_detail = f"{e.msg} at line {e.lineno}, col {e.colno}"
            attempts.append((strategy_name, snippet, error_detail))
            current_app.logger.debug(f"[JSON_FAIL] 策略 '{strategy_name}' 失敗: {error_detail}")

    if queue is not None:
        queue.put(f"ERROR: JSON 解析失敗（嘗試 {len(attempts)} 種策略），詳見伺服器日誌")
    
    if candidates:
        return None, candidates[-1][1], original, [(s, e, d) for s, _, (_, _, d) in zip([c[0] for c in candidates], [], attempts)]
    else:
        return None, "", original, attempts

def _call_gemini_with_retry(model, prompt, queue, context_message="", parse_json=True, max_retries=3, initial_delay=5):
    """
    呼叫 Gemini API，並在遇到頻率限制錯誤時自動重試。
    """
    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            resp = model.generate_content(prompt)
            resp_text = ""
            if hasattr(resp, "text"):
                resp_text = resp.text or str(resp)
            else:
                resp_text = getattr(resp, "content", None) or str(resp)

            cleaned = re.sub(r'^```json\s*|\s*```$', '', resp_text.strip(), flags=re.MULTILINE)

            if parse_json:
                parsed_obj, used_candidate, original_raw, attempts = _sanitize_and_parse_json(cleaned, queue)
                if parsed_obj is not None:
                    current_app.logger.info("Gemini 回傳 JSON 解析成功。")
                    return parsed_obj
                else:
                    raise ValueError("Gemini 回傳內容無法解析為 JSON")
            else:
                return resp_text.strip()

        except ResourceExhausted as e:
            retries += 1
            if retries >= max_retries:
                raise
            retry_delay_match = re.search(r'retry_delay {\s*seconds: (\d+)\s*}', str(e))
            if retry_delay_match:
                delay = int(retry_delay_match.group(1)) + 1
            message = f"WARN: {context_message}遇到 API 頻率限制。將在 {delay} 秒後重試..."
            current_app.logger.warning(message)
            if queue is not None:
                queue.put(message)
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error(f"_call_gemini_with_retry 發生錯誤: {e}\n{tb}")
            if queue is not None:
                queue.put(f"ERROR: _call_gemini_with_retry 發生錯誤: {str(e)}")
            raise

def call_gemini_for_analysis(content_by_page, curriculum_info, queue):
    """
    使用 Gemini 分析提取出的文本 (支援 Markdown/LaTeX 格式的數學公式)。
    """
    message = "--- 開始 AI 分析流程 ---"
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    # ==========================
    # 1. 國中康軒版 Prompt (保留原樣)
    # ==========================
    prompt_jh_kangxuan = f"""
你是一位經驗豐富的數學教材編輯，你的任務是從以下課本內容中，提取出三層結構：**章節 (Chapter)**、**小節 (Section)** 和 **核心觀念 (Core Concepts)**。

請依照以下嚴格規則進行解析，並輸出為 JSON 格式：

### 1. 結構識別規則
- **章節 (Chapter)**：
    - **搜索策略**：章節大標題不一定在第一行。請在每個章 **前 5 頁**內容中尋找最顯眼的標題。
    - **識別特徵**：通常是 "Chapter X"、"第X章"、或是 **一個獨立的大數字 (如 '1') 後面緊接數學名詞**。
    - **跨行處理 (重要)**：若數字與標題分行（例如第一行是 "1"，第二行是 "二元一次聯立方程式"），請務必將其**合併**。
    - **格式強制統一**：輸出格式必須為 **"數字 章節名稱"** (去掉 "Chapter"、"第"、"章" 等贅字)。
    - **範例**：
        - 原文 "Chapter 1 整數運算" -> 輸出 "1 整數運算"
        - 原文 "1 (換行) 二元一次聯立方程式" -> 輸出 "1 二元一次聯立方程式"

- **小節 (Section)**：識別 "X-X" 格式的子標題，例如 "1-1 負數與數線"。
- **核心觀念 (Core Concept)**：**請執行以下嚴格的篩選邏輯**：
    1.  **只保留'主題 1' '主題 2' 等開頭的標題**
    2.  **不尋找「獨立標題」**
    3.  **排除規則**：忽略 "✓"、"✔"、"☑" 等符號開頭的標題，以及 "隨堂練習"、"做做看" 等。

### 2. 資料提取與格式 (JSON Key 需精準)
對於每個識別出的「核心觀念」，請生成以下欄位：
- `concept_name`: 觀念的中文標題。
- `concept_en_id`: 英文 ID，使用 **PascalCase**。
- `concept_description`: 基於內容的簡短描述(150字內)。
- `concept_paragraph`: **觀念的中文標題**
      - 絕對不允許換行
      - 絕對不允許加說明文字
      - 絕對不允許超過15個中文字
      - 如果找不到 → 填「未分類」
- **EXAMPLES (例題提取)**：
    - 務必提取「例題 X」、「隨堂練習」。
    - 每個例題包含：`source_description`, `problem_text`, `detailed_solution`, `problem_type`。

### 3. 數學與文字格式清洗
- **修復 Pandoc 上標**：`10^6^` -> `$10^{6}$`。
- **去除變數斜體**：`*c*` -> `c`。
- **保留標準公式**：保留 `$x^2$`。

輸出嚴格為 JSON 格式。
"""

    # ==========================
    # 2. 普高龍騰版 Prompt (修正版：擴大題目抓取範圍)
    # ==========================
    prompt_sh_longteng = f"""
你是一位台灣龍騰版普通高中數學教材專家，任務是從課本內容中提取資料並轉換為 JSON。

### 1. 結構識別規則 (Flatten Structure)
此版本課本結構特殊，請採用「單元 -> 觀念」的兩層式結構：

- **章節 (Chapter)**：
    - 識別標題如 "1 實數"。
    - 輸出時請標準化為 **"單元1 實數"** 。
    
- **小節 (Section) - 重要修正**：
    - **請勿輸出空字串**。
    - 請將章節名稱中的主題部分提取出來作為小節名稱。
    - 例如：若章節為 "單元1 實數"，小節名稱請設為 **"1.實數"**。

- **核心觀念 (Core Concept)**：
    - 只捕捉 **"甲"、"乙"、"丙"、"丁"**  作為觀念。
    - **排除規則**：請勿將 "綜合習題" "(一)"、"(二)" "粗體定義" "隨堂練習"、"例題"、"習題" 誤判為「觀念名稱」，但**必須提取它們的內容**放入 Examples。

### 2. 資料提取與格式
- `concept_name`: 例如 "有理數"。
- `concept_en_id`: **PascalCase** 格式 (例如 `RationalNumbers`)。
- `concept_description`: 基於內容的簡短描述(150字內)。
- `concept_paragraph`: **只能是「甲.數列」這種短標題**
      - 允許格式：甲. / 乙. / 丙.
      - 絕對不允許換行
      - 絕對不允許加說明文字
      - 絕對不允許超過15個中文字
      - 如果找不到 → 填「未分類」
### 絕對禁止事項（違反就失敗！）
- `concept_paragraph` 裡面**絕對不可以出現 $、公式、換行、完整段落說明**
- 違規範例（禁止）：
  ```json
  "concept_paragraph": "甲 數列\\n\\n一般而言，數列可以用符號..."
- **EXAMPLES (題目提取 - 關鍵修正)**：
    - **請盡可能提取所有題目**，不只是 "例題"。
    - **目標對象**：
        1. **例題** (Example): 通常有詳細解析。
        2. **隨堂練習** (Practice): 通常緊跟在例題後面。
        3. **習題** (Exercises): 位於章節末尾。
    - `source_description`: 請清楚標示來源，例如 "例題1"、"隨堂練習"、"習題 3"。
    - `problem_text`: 題目內容 (務必保留 LaTeX 格式，例如 $x^2$)。若公式遺失，標記 `[公式遺失]`。
    - `detailed_solution`: 若原文有解析則提取，若無則填 "略"。

輸出嚴格為 JSON 格式。
"""

    # ==========================
    # 3. 通用版 Prompt
    # ==========================
    prompt_generic = f"""
你是一位數學教材編輯，請從以下內容中提取：章節 (Chapter)、小節 (Section) 和核心觀念 (Concept)。
- 結構：章節 -> 小節 -> 核心觀念。
- 提取 'examples'，並保留 LaTeX 數學符號。
輸出嚴格為 JSON 格式。
"""

    curriculum = curriculum_info.get('curriculum', '').strip()
    publisher = curriculum_info.get('publisher', '').strip()

    debug_message = f"DEBUG: 接收到的課綱資訊 -> curriculum='{curriculum}', publisher='{publisher}'"
    current_app.logger.info(debug_message)
    queue.put(f"INFO: {debug_message}")
    
    if curriculum == 'junior_high' and publisher == 'kangxuan':
        base_prompt = prompt_jh_kangxuan
        queue.put("INFO: 已選擇 '國中康軒' 專用分析模型。")
    elif curriculum == 'sh_longteng' or (curriculum == 'general' and publisher == 'longteng'): 
        base_prompt = prompt_sh_longteng
        queue.put("INFO: 已選擇 '普高龍騰' 專用分析模型 (題目擴增版)。")
    else:
        base_prompt = prompt_generic
        queue.put("INFO: 未找到專用分析模型，使用通用模型。")

    model = get_model()
    full_content = "\n".join([f"--- Page {k} ---\n{v}" for k, v in content_by_page.items()])
    
    analysis_prompt = f"""
{base_prompt}

【重要提示】
1. 輸出必須是**完整、有效的 JSON**。
2. 反斜線需轉義 (例如 `\\\\sqrt`)。
3. 不要 markdown code fence。

JSON 結構範例 (注意 section_title 為空字串的情況)：
{{
  "chapters": [
    {{
      "chapter_title": "1 實數",
      "sections": [
        {{
          "section_title": "1.實數", 
          "concepts": [
            {{
              "concept_name": "有理數",
              "concept_en_id": "RationalNumbers",
              "concept_description": "...",
              "concept_paragraph": "甲.數列",
              "examples": [
                 {{
                    "source_description": "例題1",
                    "problem_text": "...",
                    "problem_type": "calculation"
                 }},
                 {{
                    "source_description": "隨堂練習",
                    "problem_text": "...",
                    "problem_type": "calculation"
                 }}
              ]
            }}
          ]
        }}
      ]
    }}
  ]
}}

課本內容：
{full_content}
"""

    try:
        ai_response = _call_gemini_with_retry(
            model, 
            analysis_prompt, 
            queue, 
            context_message="提取課本結構時，",
            parse_json=True
        )
        return ai_response
    except Exception as e:
        queue.put(f"ERROR: AI 分析失敗: {e}")
        return ""

def parse_ai_response(ai_data_or_string, queue):
    """解析 AI 回傳的資料 (JSON 字串或已解析的 dict)，並進行基本驗證。"""
    message = "正在解析 AI 回傳的 JSON..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    if isinstance(ai_data_or_string, dict):
        return ai_data_or_string

    if not isinstance(ai_data_or_string, str) or not ai_data_or_string.strip():
        message = f"錯誤：無法處理的 AI 回傳類型: {type(ai_data_or_string)}"
        current_app.logger.error(message)
        queue.put(f"ERROR: {message}")
        return None

    cleaned_string = re.sub(r'^```(?:json)?\s*|\s*```$', '', ai_data_or_string, flags=re.MULTILINE).strip()
    parsed_obj, _, _, _ = _sanitize_and_parse_json(cleaned_string, queue=None)

    if parsed_obj is not None:
        queue.put("INFO: AI 回應成功解析為標準 JSON。")
        return parsed_obj

    # --- 備用方案：逐章解析 (保留您原本的邏輯) ---
    queue.put("WARN: 標準 JSON 解析失敗，啟用備用方案：逐章節提取並解析。")
    current_app.logger.warning("標準 JSON 解析失敗，啟用備用方案：逐章節提取並解析。")

    chapter_chunks = re.findall(r'(\{\s*"chapter_title":.*?\}(?=\s*,\s*\{"chapter_title"|\s*\]\s*\}))', cleaned_string, re.DOTALL)

    if not chapter_chunks:
        queue.put("ERROR: 備用方案失敗：無法從文本中提取任何章節區塊。")
        return None

    queue.put(f"INFO: 備用方案：偵測到 {len(chapter_chunks)} 個可能的章節區塊。")
    successful_chapters = []
    for i, chunk in enumerate(chapter_chunks):
        try:
            chapter_obj, _, _, _ = _sanitize_and_parse_json(chunk, queue=None)
            if chapter_obj:
                successful_chapters.append(chapter_obj)
            else:
                queue.put(f"WARN: 無法解析章節區塊 {i+1}，已跳過。")
        except Exception as e:
            queue.put(f"WARN: 解析章節區塊 {i+1} 時發生錯誤: {e}，已跳過。")

    if not successful_chapters:
        queue.put("ERROR: 備用方案最終失敗：沒有任何章節區塊能被成功解析。")
        return None

    return {"chapters": successful_chapters}

def to_pascal_case(snake_case_string):
    """將 snake_case 或 kebab-case 字串轉換為 PascalCase。"""
    if not snake_case_string:
        return ""
    return ''.join(word.capitalize() for word in re.split('_|-', snake_case_string))

def clean_skill_en_name(raw_en_name, queue=None):
    """
    (PascalCase 策略版) 移除多餘的結構化前綴，只保留 PascalCase 部分。
    """
    if not raw_en_name:
        return ""
    match = re.search(r'[A-Z]', raw_en_name)
    if match:
        start_index = match.start()
        return raw_en_name[start_index:]
    return raw_en_name

def save_to_database(parsed_data, curriculum_info, queue):
    """
    將 AI 分析完的目錄資料寫入資料庫。
    """
    message = "正在將目錄結構寫入資料庫..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")
    skills_processed = 0
    curriculums_added = 0
    examples_added = 0
    processed_skill_ids = []

    prefix_map = {
        'junior_high': 'jh_',
        'general': 'gh_',
        'vocational': 'vh_'
    }
    prefix = prefix_map.get(curriculum_info.get('curriculum', ''), '')

    try:
        current_app.logger.info(" -> 開始寫入資料庫...")
        queue.put("INFO: -> 開始寫入資料庫...")
        chapters = parsed_data.get('chapters', [])
        
        for chapter_data in chapters:
            raw_chapter = chapter_data.get('chapter_title', '未命名章節').strip()
            
            # === 關鍵修正 1：提取數字並標準化章節名稱 ===
            match = re.search(r'(\d+)', raw_chapter)
            if match:
                chapter_num = int(match.group(1))
                # 移除開頭的「單元」「第」「章」等雜訊,留下乾淨標題
                clean_title = re.sub(r'^(?:單元|Unit|第)?\s*\d+\s*(?:單元|章)?\s*', '', raw_chapter).strip()
                chapter_title = f"單元{chapter_num} {clean_title}" if clean_title else f"單元{chapter_num}"
            else:
                chapter_title = raw_chapter
                chapter_num = 999  # 沒有數字的排最後
            
            sections = chapter_data.get('sections', [])
            
            # 國中教材專用處理 (保留原邏輯,但只在國中時執行)
            if curriculum_info.get('curriculum') == 'junior_high':
                chapter_title = chapter_title.replace('\n', ' ').strip()
                chapter_title = re.sub(r'^(?:Chapter|Unit|第)\s*(\d+)(?:\s*章)?\s*', r'\1 ', chapter_title).strip()
                if chapter_title.isdigit():
                    try:
                        existing_chapter = SkillCurriculum.query.filter_by(
                            curriculum=curriculum_info['curriculum'],
                            grade=int(curriculum_info['grade']),
                            volume=curriculum_info['volume']
                        ).filter(SkillCurriculum.chapter.like(f"{chapter_title} %")).first()
                        if existing_chapter:
                            chapter_title = existing_chapter.chapter
                    except Exception:
                        pass
            
            for section_data in sections:
                section_title = section_data.get('section_title', '') or ''  # 龍騰版很多是空字串,允許
                concepts = section_data.get('concepts', [])
                
                for concept in concepts:
                    concept_name = concept.get('concept_name', '未命名觀念').strip()
                    concept_en_id = concept.get('concept_en_id', 'Unknown')
                    concept_paragraph = concept.get('concept_paragraph', '未命名').strip()
                    
                    clean_en_id = re.sub(r'[^a-zA-Z0-9]', '', concept_en_id)
                    final_skill_id = f"{prefix}{clean_en_id}"
                    
                    # === SkillInfo 新增/更新 (維持原邏輯) ===
                    existing_skill = SkillInfo.query.get(final_skill_id)
                    if not existing_skill:
                        new_skill = SkillInfo(
                            skill_id=final_skill_id,
                            skill_en_name=clean_en_id,
                            skill_ch_name=concept_name,
                            category = section_title,
                            description=concept.get('concept_description', ''),
                            input_type='text',
                            gemini_prompt=f"Generate math problems about {concept_name}.",
                            is_active=True
                        )
                        db.session.add(new_skill)
                        skills_processed += 1
                        processed_skill_ids.append(final_skill_id)
                    
                    # === SkillCurriculum 新增 (關鍵：加入正確的 display_order) ===
                    existing_curr = SkillCurriculum.query.filter_by(
                        skill_id=final_skill_id,
                        chapter=chapter_title,
                        section=section_title
                    ).first()
                    
                    if not existing_curr:
                        new_curr = SkillCurriculum(
                            skill_id=final_skill_id,
                            curriculum=curriculum_info.get('curriculum'),
                            grade=int(curriculum_info.get('grade', 10)),
                            volume=str(curriculum_info.get('volume', 1)),
                            chapter=chapter_title,
                            section=section_title,
                            paragraph=concept_paragraph,
                            display_order=chapter_num * 10000 + skills_processed  # 10000 倍數確保單元間不會互相干擾
                        )
                        db.session.add(new_curr)
                        curriculums_added += 1

                    # === 例題處理 (維持原邏輯) ===
                    for ex in concept.get('examples', []):
                        problem_text = ex.get('problem_text')
                        if not problem_text: continue
                        
                        existing_ex = TextbookExample.query.filter_by(
                            skill_id=final_skill_id,
                            source_description=ex.get('source_description', '例題')
                        ).first()

                        if not existing_ex:
                            new_ex = TextbookExample(
                                skill_id=final_skill_id,
                                source_curriculum=curriculum_info.get('curriculum'),
                                source_volume=str(curriculum_info.get('volume')),
                                source_chapter=chapter_title,
                                source_section=section_title,
                                source_paragraph=concept_name,
                                source_description=ex.get('source_description', '例題'),
                                problem_text=problem_text,
                                problem_type=ex.get('problem_type', 'calculation'),
                                correct_answer=ex.get('correct_answer', ''),
                                detailed_solution=ex.get('detailed_solution', ''),
                                difficulty_level=int(ex.get('difficulty_level', 1))
                            )
                            db.session.add(new_ex)
                            examples_added += 1

        db.session.commit()
        return {
            'skills_processed': skills_processed, 
            'curriculums_added': curriculums_added,
            'examples_added': examples_added,
            'processed_skill_ids': processed_skill_ids
        }

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"寫入資料庫失敗: {e}")
        queue.put(f"ERROR: 寫入資料庫失敗: {e}")
        return {}