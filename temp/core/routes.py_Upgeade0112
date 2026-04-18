# core/routes.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash, send_file
from markupsafe import Markup
from datetime import datetime
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import io
import json
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import traceback
import os
import re
import importlib
import pandas as pd
import google.generativeai as genai
import random
import string
from sqlalchemy.orm import aliased
from flask import session, jsonify
from config import Config
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum, Progress, Class, ClassStudent, User, ExamAnalysis, init_db
from sqlalchemy.exc import IntegrityError
from core.utils import get_skill_info
from core.session import get_current, set_current
from core.ai_analyzer import get_model, analyze, build_chat_prompt, get_chat_response
from core.exam_analyzer import analyze_exam_image, save_analysis_result, get_flattened_unit_paths
from core.data_importer import import_excel_to_db
from . import textbook_processor
from werkzeug.utils import secure_filename
from sqlalchemy import distinct, text
from sqlalchemy.exc import OperationalError
import time
import uuid
import threading
import queue
from flask import Response, stream_with_context
import glob

# 用於暫存正在執行的任務佇列 (簡易版 In-memory store)
# Key: task_id, Value: queue.Queue
TASK_QUEUES = {}


core_bp = Blueprint('core', __name__, template_folder='../templates')
practice_bp = Blueprint('practice', __name__) # 新增：練習專用的 Blueprint


@core_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

# 練習相關的路由也需要登入
@practice_bp.before_request
@login_required
def practice_require_login():
    pass

# --- Helper Function for Threading ---
# --- Helper Function for Threading ---
def background_processing(file_paths, task_queue, app_context, curriculum_info, skip_code_gen):
    """
    背景處理函式 (支援單檔或多檔)
    :param file_paths: list, 包含絕對路徑的字串列表
    """
    with app_context:
        try:
            total_skills = 0
            total_examples = 0
            total_files = len(file_paths)
            
            task_queue.put(f"INFO: 開始處理任務，共 {total_files} 個檔案...")

            for idx, file_path in enumerate(file_paths, 1):
                filename = os.path.basename(file_path)
                
                # [新增] 暫存檔/隱藏檔過濾機制
                if filename.startswith('~$') or filename.startswith('.'):
                    task_queue.put(f"INFO: 跳過暫存/隱藏檔案: {filename}")
                    continue

                task_queue.put(f"INFO: [{idx}/{total_files}] 正在分析: {filename} ...")
                
                try:
                    # 呼叫核心處理邏輯，並傳入 queue
                    result = textbook_processor.process_textbook_file(
                        file_path, 
                        curriculum_info=curriculum_info, 
                        queue=task_queue,
                        skip_code_gen=skip_code_gen
                    )
                    
                    if result:
                        total_skills += result.get('skills_processed', 0)
                        total_examples += result.get('examples_added', 0)
                except Exception as e:
                    task_queue.put(f"ERROR: 檔案 {filename} 處理失敗: {e}")
                    print(f"Background Error processing {filename}: {e}")
                
                # 如果是暫存檔 (上傳的)，處理完後刪除；如果是本機資料夾的檔，則保留
                # 這裡透過判斷路徑是否在 uploads 資料夾來決定
                if 'uploads' in file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass

            task_queue.put(f"SUCCESS: 所有作業完成！總計新增技能: {total_skills}, 例題: {total_examples}")

        except Exception as e:
            task_queue.put(f"ERROR: 任務執行發生例外: {str(e)}")
            print(f"Background Task Error: {e}")
        finally:
            task_queue.put("END_OF_STREAM")

def get_skill(skill_id):
    try:
        return importlib.import_module(f"skills.{skill_id}")
    except:
        return None

def update_progress(user_id, skill_id, is_correct):
    """
    更新用戶進度（功文式教育理論）
    核心精神：在學生感到舒適的難度下進行大量練習，達到精熟後才晉級。若遇到困難，則退回一個等級鞏固基礎，避免挫折感。
    **新邏輯**：由於題目難度已由課綱靜態決定，此函式不再處理升降級，僅記錄練習次數與連續答對/錯次數。
    """
    # 使用 ORM 查詢進度記錄
    progress = db.session.query(Progress).filter_by(user_id=user_id, skill_id=skill_id).first()

    # [Fix] 確保取得當前時間物件
    now_time = datetime.now()

    if not progress:
        # 如果沒有記錄，建立新的 Progress 物件
        progress = Progress(
            user_id=user_id,
            skill_id=skill_id,
            consecutive_correct=1 if is_correct else 0,
            consecutive_wrong=0 if is_correct else 1,
            questions_solved=1,
            current_level=1, # 此欄位已不再用於決定題目難度，僅為保留欄位
            last_practiced=now_time  # [Fix] 明確賦值時間物件
        )
        db.session.add(progress)
    else:
        # 如果有記錄，更新現有物件
        progress.questions_solved += 1
        progress.last_practiced = now_time # [Fix] 更新最後練習時間
        
        # 讀取技能的晉級/降級門檻
        skill_info = db.session.get(SkillInfo, skill_id)
        required = skill_info.consecutive_correct_required if skill_info else 10
        
        # 更新連續答對/錯次數
        if is_correct:
            progress.consecutive_correct += 1
            progress.consecutive_wrong = 0 # 答對，連續錯誤歸零
        else:
            progress.consecutive_correct = 0 # 只要錯了，連續答對就中斷
            progress.consecutive_wrong += 1
    
    # 提交變更到資料庫
    db.session.commit()

@core_bp.route('/admin/import_skills', methods=['POST'])
@login_required
def import_skills():
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "Permission denied."}), 403
    
    try:
        from . import data_importer 
        count = data_importer.import_skills_from_json()
        
        return jsonify({"success": True, "message": f"成功匯入 {count} 個技能單元！"})

    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"Batch import skills failed: {e}\n{error_details}")
        
        return jsonify({
            "success": False, 
            "message": f"批次匯入技能失敗！\n\n錯誤原因：\n{str(e)}\n\n請檢查伺服器日誌以獲取詳細資訊。"
        }), 500

@core_bp.route('/admin/import_curriculum', methods=['POST'])
@login_required
def import_curriculum():
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "Permission denied."}), 403

    try:
        from . import data_importer
        count = data_importer.import_curriculum_from_json()
        
        return jsonify({"success": True, "message": f"成功匯入 {count} 個課程綱要項目！"})

    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"Batch import curriculum failed: {e}\n{error_details}")
        
        return jsonify({
            "success": False, 
            "message": f"批次匯入課程綱要失敗！\n\n錯誤原因：\n{str(e)}\n\n請檢查伺服器日誌以獲取詳細資訊。"
        }), 500


@practice_bp.route('/practice/<skill_id>')
@login_required
def practice(skill_id):
    # 查詢當前技能的資訊
    skill_info = db.session.get(SkillInfo, skill_id)
    skill_ch_name = skill_info.skill_ch_name if skill_info else "未知技能"

    # 查詢與此技能相關的前置基礎技能
    # 我們 JOIN SkillPrerequisites 和 SkillInfo 來找到所有 prerequisite_id 對應的技能名稱
    prerequisites = db.session.query(SkillInfo).join(
        SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
    ).filter(
        SkillPrerequisites.skill_id == skill_id,
        SkillInfo.is_active.is_(True)  # [Fix] 使用 .is_(True)
    ).order_by(SkillInfo.skill_ch_name).all()

    # 將查詢結果轉換為字典列表，方便模板使用
    prereq_skills = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in prerequisites]

    return render_template('index.html', 
                           skill_id=skill_id,
                           skill_ch_name=skill_ch_name,
                           prereq_skills=prereq_skills) # 將前置技能列表傳遞給模板

@practice_bp.route('/get_next_question')
def next_question():
    skill_id = request.args.get('skill', 'remainder')
    requested_level = request.args.get('level', type=int) # 新增：從前端獲取請求的難度等級

    # === 特殊處理：自訂上傳題目 ===
    # 如果是 custom_upload 且 session 中已經有非預設的題目，則直接回傳 Session 中的資料，不重新生成
    if skill_id == 'custom_upload':
        current_data = get_current()
        # 檢查是否為有效的自訂題目 (排除預設 placeholder)
        if current_data and current_data.get('skill') == 'custom_upload' and "請上傳題目" not in current_data.get('question_text', ''):
            # 補上 context_string 與前置技能資訊 (如果缺失)
            current_data['context_string'] = current_data.get('context_string', '')
            current_data['prereq_skills'] = [] # 自訂題目無關聯前置技能
            # 關鍵修正: 前端 loadQuestion 預期欄位是 new_question_text
            current_data['new_question_text'] = current_data.get('question_text', '')
            # 確保 current_level 存在
            current_data['current_level'] = current_data.get('level', '自訂')
            return jsonify(current_data)
    
    # 從 DB 驗證 skill 是否存在 (custom_upload 除外)
    if skill_id != 'custom_upload':
        skill_info = get_skill_info(skill_id)
        if not skill_info:
            return jsonify({"error": f"技能 {skill_id} 不存在或未啟用"}), 404
    else:
        # custom_upload 虛擬技能，使用預設值
        skill_info = None 
    
    try:
        mod = importlib.import_module(f"skills.{skill_id}")
        
        # 1. 課綱與難度判斷邏輯
        current_curriculum_context = session.get('current_curriculum', 'general')
        curriculum_entry = db.session.query(SkillCurriculum).filter_by(
            skill_id=skill_id,
            curriculum=current_curriculum_context
        ).first()

        if requested_level: 
            difficulty_level = requested_level
        elif curriculum_entry and curriculum_entry.difficulty_level: 
            difficulty_level = curriculum_entry.difficulty_level
        else:
            difficulty_level = 1 

        progress = db.session.query(Progress).filter_by(user_id=current_user.id, skill_id=skill_id).first()
        consecutive = progress.consecutive_correct if progress else 0

        # 前置技能查詢
        prereq_query = db.session.query(SkillInfo).join(
            SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
        ).filter(
            SkillPrerequisites.skill_id == skill_id,
            SkillInfo.is_active.is_(True) # [Fix] 使用 .is_(True)
        ).order_by(SkillInfo.skill_ch_name).all()
        
        prereq_info_for_ai = [{'id': p.skill_id, 'name': p.skill_ch_name} for p in prereq_query]

        # ★★★ [新增] 自動重試機制 (Retry Logic) ★★★
        # 這是為了解決 1.5B 模型偶爾發生 IndexError 的避震器
        max_retries = 5
        data = None
        last_error = None

        for attempt in range(max_retries):
            try:
                # 嘗試生成題目
                data = mod.generate(level=difficulty_level)
                
                # 簡單驗證格式，避免生成空題目
                if not data or "question_text" not in data or "correct_answer" not in data:
                    raise ValueError("生成的題目格式不完整")
                
                # 如果成功，就跳出迴圈
                break
            except Exception as e:
                last_error = e
                # 在後台記錄錯誤，但不回傳給使用者，而是默默重試
                current_app.logger.warning(f"⚠️ 題目生成失敗 (嘗試 {attempt+1}/{max_retries}): {skill_id} - {e}")
                if attempt == max_retries - 1:
                    # 如果試了 5 次都失敗，才真的放棄
                    raise e
        
        # ----------------------------------------------

        # ----------------------------------------------

        # 加入 context_string 給 AI
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        data['prereq_skills'] = prereq_info_for_ai
        
        # [Fix] 防止 Session 撐爆：過濾掉巨大的圖片資料
        session_data = data.copy()
        if 'image_base64' in session_data:
            del session_data['image_base64']
        if 'visuals' in session_data:
            del session_data['visuals']
        # 額外過濾 visual_aids (因為它也可能包含圖片路徑或資料)
        if 'visual_aids' in session_data:
            del session_data['visual_aids']
            
        set_current(skill_id, session_data)
        
        return jsonify({
            "new_question_text": data["question_text"],
            "context_string": data.get("context_string", ""),
            "inequality_string": data.get("inequality_string", ""),
            "consecutive_correct": consecutive, 
            "current_level": difficulty_level, 
            "image_base64": data.get("image_base64", ""), 
            "visual_aids": data.get("visual_aids", []),
            "answer_type": skill_info.get("input_type", "text") 
        })
    except Exception as e:
        # 真的全部失敗了，才會顯示這個錯誤
        return jsonify({"error": f"生成題目失敗，請稍後再試: {str(e)}"}), 500

@practice_bp.route('/check_answer', methods=['POST'])
def check_answer():
    user = request.json.get('answer', '').strip()
    current = get_current()

    # [Fix] 安全檢查：如果伺服器重啟導致 Session 遺失
    if not current or 'skill' not in current:
        return jsonify({
            "correct": False,
            "result": "連線逾時或伺服器已重啟，請重新整理頁面再試。",
            "state_lost": True  # 讓前端知道是狀態遺失
        }), 400

    skill = current['skill']
    correct_answer = current.get('correct_answer') # 使用 .get 避免錯誤

    mod = get_skill(skill)
    if not mod:
        return jsonify({"correct": False, "result": "單元錯誤"})

    # 圖形題：不批改，直接提示用 AI
    if correct_answer == "graph":
        return jsonify({
            "correct": False,
            "result": "請畫完可行域後，點「AI 檢查」",
            "next_question": False
        })

    # 文字題：正常批改
    result = mod.check(user, current['answer'])
    
    # 安全地獲取批改結果，避免 KeyError
    is_correct = result.get('correct', False)
    if not isinstance(is_correct, bool):
        is_correct = False

    # 更新進度
    update_progress(current_user.id, skill, is_correct)

    # 如果答錯，自動記錄到錯題本
    if not is_correct:
        try:
            question_text = current.get('question_text')
            # 檢查是否已存在相同的錯題記錄 (基於問題內容)
            existing_entry = db.session.query(MistakeNotebookEntry).filter_by(
                student_id=current_user.id,
                skill_id=skill
            ).filter(MistakeNotebookEntry.question_data.contains(question_text)).first()

            if not existing_entry and question_text:
                new_entry = MistakeNotebookEntry(
                    student_id=current_user.id,
                    skill_id=skill,
                    question_data={'type': 'system_question', 'text': question_text},
                    notes='系統練習題自動記錄'
                )
                db.session.add(new_entry)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"自動記錄錯題失敗: {e}")
            db.session.rollback() # Rollback on error
    
    return jsonify(result)

@practice_bp.route('/upload_question_image', methods=['POST'])
@login_required # Ensure user is logged in
def upload_question_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            from core.ai_analyzer import analyze_question_image
            result = analyze_question_image(file)
            
            if "error" in result:
                return jsonify({"error": result["error"]}), 500

            # Store in session so check_answer can verify it
            # We use a special skill ID 'custom_upload'
            set_current("custom_upload", 
                        {"question_text": result["question_text"], 
                         "correct_answer": result["correct_answer"],
                         "answer": result["correct_answer"], # Store answer for check_answer
                         "answer_type": "text",
                         "level": 1})

            return jsonify({
                "question_text": result["question_text"],
                "success": True
            })

        except Exception as e:
            current_app.logger.error(f"Image upload failed: {e}")
            return jsonify({"error": str(e)}), 500

@practice_bp.route('/analyze_handwriting', methods=['POST'])
@login_required
def analyze_handwriting():
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: 
        return jsonify({"reply": "缺少圖片"}), 400
    
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    # 新增：從 session 讀取前置技能資訊並傳遞給 analyze 函式
    prereq_skills = state.get('prereq_skills', [])
    result = analyze(image_data_url=img, context=state['question'], 
                     api_key=api_key, 
                     prerequisite_skills=prereq_skills)
    
    # 更新進度
    if result.get('correct') or result.get('is_process_correct'):
        update_progress(current_user.id, state['skill'], True)
    else:
        update_progress(current_user.id, state['skill'], False)

        # 記錄錯誤到資料庫
        try:
            from models import MistakeLog
            
            mistake_log = MistakeLog(
                user_id=current_user.id,
                skill_id=state['skill'],
                question_content=state['question'],
                user_answer="手寫作答(圖片)",
                correct_answer=state.get('correct_answer', '未知'),
                error_type=result.get('error_type'),
                error_description=result.get('error_description'),
                improvement_suggestion=result.get('improvement_suggestion')
            )
            db.session.add(mistake_log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"記錄錯誤失敗: {e}")
            db.session.rollback()
            # 不影響主流程,繼續執行
    
    return jsonify(result)

@practice_bp.route('/chat_ai', methods=['POST'])
def chat_ai():
    data = request.get_json()
    user_question = data.get('question', '').strip()
    context = data.get('context', '')
    question_text = data.get('question_text', '')  # 接收完整題目文字

    if not user_question:
        return jsonify({"reply": "請輸入問題！"}), 400

    # 安全取得當前題目
    current = get_current()
    skill_id = current.get("skill")
    prereq_skills = current.get('prereq_skills', []) # 新增：從 session 讀取前置技能資訊
    
    # 優先使用傳入的題目文字，否則使用 session 中的，最後使用 context
    if question_text:
        full_question_context = question_text
    elif current.get("question"):
        full_question_context = current.get("question")
    else:
        full_question_context = context or "（無題目資訊）"
    
    # 如果 session 沒資料，從 context 猜測 skill
    if not skill_id:
        if any(kw in context for kw in ['餘式', 'remainder', 'f(x)', '除']):
            skill_id = 'remainder'
        elif any(kw in context for kw in ['因式', 'factor', '(x -', '是否為']):
            skill_id = 'factor_theorem'
        elif any(kw in context for kw in ['不等式', 'inequality', '可行域', '≥', '≤']):
            skill_id = 'inequality_graph'
        else:
            skill_id = 'remainder'

    # Remove direct DB prompt reading and logic from here
    
    # Call AI Analyzer to build prompt and get response
    full_prompt = build_chat_prompt(
        skill_id=skill_id,
        user_question=user_question,
        full_question_context=full_question_context,
        context=context,
        prereq_skills=prereq_skills
    )
    
    # 處理圖片 (如果有的話)
    image_obj = None
    image_data = data.get('image_data')  # 預期是 base64 string
    if image_data and 'base64,' in image_data:
        try:
            from PIL import Image
            import io
            import base64
            
            header, encoded = image_data.split('base64,', 1)
            image_bytes = base64.b64decode(encoded)
            image_obj = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            print(f"Chat AI Image Decode Error: {e}")
            # fall through, just don't use image

    result = get_chat_response(full_prompt, image=image_obj)
    return jsonify(result)

@practice_bp.route('/draw_diagram', methods=['POST'])
@login_required
def draw_diagram():
    try:
        data = request.get_json()
        question_text = data.get('question_text')

        if not question_text:
            return jsonify({"success": False, "message": "沒有收到題目文字。"}), 400

        # 1. Call Gemini API to get equations
        api_key = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=api_key)
        
        # Use the model from app config for consistency
        model_name = current_app.config.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash')
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        從以下數學題目中提取出所有可以用來繪製2D圖形的方程式或不等式。
        - 請只回傳方程式/不等式，每個一行。
        - 例如，如果題目是 "y = 2x + 1 和 x^2 + y^2 = 9"，你就回傳：
          y = 2x + 1
          x**2 + y**2 = 9
        - 請將 '^' 符號轉換為 '**' 以利 Python 運算。
        - 如果找不到任何可繪製的方程式或不等式，請回傳 "No equation found"。

        題目：
        {question_text}
        """
        
        response = model.generate_content(prompt)
        equations_text = response.text.strip()

        if "No equation found" in equations_text or not equations_text:
            return jsonify({"success": False, "message": "AI 無法從題目中找到可繪製的方程式。"}), 400

        # 2. Use Matplotlib to plot
        plt.figure(figsize=(6, 6))
        x = np.linspace(-10, 10, 400)
        y = np.linspace(-10, 10, 400)
        x, y = np.meshgrid(x, y)

        # Define a context for eval() to prevent NameError for common variables
        eval_context = {
            'np': np,
            'x': x,
            'y': y,
            'a': 2,  # Default value for 'a'
            'b': 3,  # Default value for 'b'
            'c': 4   # Default value for 'c'
        }

        has_plot = False
        for line in equations_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Strip '$' characters used for math formatting
            line = line.strip('$')

            # Pre-process function names to be numpy-compatible
            # Order is important for log, log10, log2
            line = line.replace('sqrt', 'np.sqrt')
            line = line.replace('sin', 'np.sin')
            line = line.replace('cos', 'np.cos')
            line = line.replace('tan', 'np.tan')
            line = line.replace('log10', 'np.log10')
            line = line.replace('log2', 'np.log2')
            line = line.replace('ln', 'np.log') # ln is natural log
            line = line.replace('log', 'np.log')   # base e log (natural log)

            # Sanitize equation string for safer evaluation
            line = line.replace('^', '**')
            line = line.replace('+ -', '-')
            
            # Add multiplication signs for implicit multiplication
            # e.g., 2x -> 2*x, 3(x+1) -> 3*(x+1), (x+1)y -> (x+1)*y
            # Use negative lookbehind to prevent changing 'log2(x)' to 'log2*(x)'
            line = re.sub(r'(?<![a-zA-Z])(\d)([a-zA-Z(])', r'\1*\2', line)
            line = re.sub(r'(\))([a-zA-Z\d(])', r'\1*\2', line)
            line = re.sub(r'([xy])([xy])', r'\1*\2', line)
            
            # Handle cases like 'x' or '-x' becoming '1*x' or '-1*x'
            # Look for x or y that is not preceded by a digit, letter, or '*' or '.'
            line = re.sub(r'(?<![\d\w*.])([xy])', r'1*\1', line)
            # Look for -x or -y that is not preceded by a digit, letter, or '*' or '.'
            line = re.sub(r'(?<![\d\w*.])(-)([xy])', r'\g<1>1*\2', line)
            
            try:
                # This is a simplified and somewhat unsafe way to plot.
                # It assumes the AI returns valid Python boolean expressions.
                if '=' in line and '==' not in line and '>' not in line and '<' not in line:
                    # Likely an equation like y = 2*x + 1 or x**2 + y**2 = 9
                    parts = line.split('=')
                    expr = f"({parts[0].strip()}) - ({parts[1].strip()})"
                    # Plot contour where expression is zero
                    plt.contour(x, y, eval(expr, eval_context), levels=[0], colors='b')
                    has_plot = True
                elif '>' in line or '<' in line:
                    # Likely an inequality like y > 2*x or x + y <= 5
                    plt.contourf(x, y, eval(line, eval_context), levels=[0, np.inf], colors=['#3498db'], alpha=0.3)
                    has_plot = True

            except Exception as e:
                current_app.logger.error(f"無法繪製方程式 '{line}': {e}")
                # Don't stop, try to plot other equations
                continue
        
        if not has_plot:
            return jsonify({"success": False, "message": "成功提取方程式，但無法繪製任何有效的圖形。"}), 400

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.title("Equation Diagram")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.gca().set_aspect('equal', adjustable='box')

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

    except Exception as e:
        current_app.logger.error(f"繪製示意圖時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": f"伺服器內部錯誤: {e}"}), 500


@core_bp.route('/api/get_grades')
@login_required
def api_get_grades():
    curriculum = request.args.get('curriculum')
    query = db.session.query(distinct(SkillCurriculum.grade)).filter_by(curriculum=curriculum)
    # 過濾 None 並排序
    grades = sorted([row[0] for row in query.filter(SkillCurriculum.grade != None).all()])
    return jsonify(grades)

@core_bp.route('/api/get_volumes')
@login_required
def api_get_volumes():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    query = db.session.query(distinct(SkillCurriculum.volume)).filter_by(curriculum=curriculum, grade=grade)
    volumes = [row[0] for row in query.all()]
    return jsonify(volumes)

@core_bp.route('/api/get_chapters')
@login_required
def api_get_chapters():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    query = db.session.query(distinct(SkillCurriculum.chapter)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume
    )
    chapters = [row[0] for row in query.all()]
    return jsonify(chapters)

@core_bp.route('/api/get_sections')
@login_required
def api_get_sections():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    query = db.session.query(distinct(SkillCurriculum.section)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume, chapter=chapter
    )
    sections = [row[0] for row in query.all()]
    return jsonify(sections)
# === API 路由：用於連動式下拉選單 ===
# 這些路由註冊在 core_bp 上，會自動受到 before_request 的登入保護
@core_bp.route('/api/curriculum/grades')
def api_get_grades_legacy():
    # 允許管理員 OR 老師
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify([])
    curriculum = request.args.get('curriculum')
    if not curriculum:
        return jsonify([])
    grades = db.session.query(SkillCurriculum.grade).filter_by(curriculum=curriculum).distinct().order_by(SkillCurriculum.grade).all()
    return jsonify([g[0] for g in grades])

@core_bp.route('/api/curriculum/volumes')
def api_get_volumes_legacy():
    # 允許管理員 OR 老師
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify([])
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    if not curriculum or not grade:
        return jsonify([])
    volumes = db.session.query(SkillCurriculum.volume).filter_by(curriculum=curriculum, grade=int(grade)).distinct().order_by(SkillCurriculum.volume).all()
    return jsonify([v[0] for v in volumes])

@core_bp.route('/api/curriculum/chapters')
def api_get_chapters_legacy():
    curriculum = request.args.get('curriculum')
    # 允許管理員 OR 老師
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify([])
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    if not curriculum or not grade or not volume:
        return jsonify([])
    chapters = db.session.query(SkillCurriculum.chapter).filter_by(
        curriculum=curriculum, 
        grade=int(grade),
        volume=volume
    ).distinct().order_by(SkillCurriculum.chapter).all()
    return jsonify([c[0] for c in chapters])

@core_bp.route('/api/curriculum/sections')
def api_get_sections_legacy():
    curriculum = request.args.get('curriculum')
    # 允許管理員 OR 老師
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify([])
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    if not all([curriculum, grade, volume, chapter]):
        return jsonify([])
    sections = db.session.query(SkillCurriculum.section).filter_by(
        curriculum=curriculum, 
        grade=int(grade),
        volume=volume,
        chapter=chapter
    ).distinct().order_by(SkillCurriculum.section).all()
    return jsonify([s[0] for s in sections])

# === 檢查幽靈技能 API ===
@core_bp.route('/skills/check_ghosts')
def check_ghost_skills():
    if not current_user.is_admin: # 確保只有管理員能執行
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 1. 獲取檔案系統中的所有技能檔案
        skills_dir = os.path.join(current_app.root_path, 'skills')
        skill_files = {f.replace('.py', '') for f in os.listdir(skills_dir) 
                       if f.endswith('.py') and f not in ['__init__.py', 'utils.py']}

        # 2. 獲取資料庫中所有已註冊的 skill_id
        registered_skills_query = db.session.query(SkillInfo.skill_id).all()
        registered_skill_ids = {row[0] for row in registered_skills_query}

        # 3. 找出差異：存在於檔案系統但不存在於資料庫中的檔案
        ghost_files = sorted(list(skill_files - registered_skill_ids))

        return jsonify({"success": True, "ghost_files": ghost_files})
    except Exception as e:
        # 使用 current_app.logger 記錄詳細錯誤
        current_app.logger.error(f"檢查幽靈技能時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": f"檢查時發生錯誤: {str(e)}"}), 500

# ==========================================
# 技能前置依賴管理 (Prerequisites Management)
# ==========================================

@core_bp.route('/prerequisites')
@core_bp.route('/admin/prerequisites')
def admin_prerequisites():
    """
    前置技能管理主頁面 - 支援階層式篩選
    """
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('您沒有權限存取此頁面。', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # 1. 讀取篩選參數
        f_curriculum = request.args.get('f_curriculum', 'all')
        f_grade = request.args.get('f_grade', 'all')
        f_volume = request.args.get('f_volume', 'all')
        f_chapter = request.args.get('f_chapter', 'all')
        
        # 2. 建構查詢 - Join SkillInfo 與 SkillCurriculum
        query = db.session.query(SkillInfo, SkillCurriculum).join(
            SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id
        ).filter(SkillInfo.is_active.is_(True))
        
        # 3. 應用篩選條件
        if f_curriculum != 'all':
            query = query.filter(SkillCurriculum.curriculum == f_curriculum)
        if f_grade != 'all':
            query = query.filter(SkillCurriculum.grade == int(f_grade))
        if f_volume != 'all':
            query = query.filter(SkillCurriculum.volume == f_volume)
        if f_chapter != 'all':
            query = query.filter(SkillCurriculum.chapter == f_chapter)
        
        # 4. 執行查詢並處理結果
        results = query.order_by(SkillCurriculum.display_order).all()
        
        # 5. 準備技能列表 (關鍵：附加 grade, volume, chapter, prereq_count)
        skills_list = []
        seen_skill_ids = set()
        
        for skill_info, skill_curriculum in results:
            # 避免重複 (同一技能可能出現在多個課綱中)
            if skill_info.skill_id in seen_skill_ids:
                continue
            seen_skill_ids.add(skill_info.skill_id)
            
            # 附加課綱資訊到 skill_info 物件
            skill_info.grade = skill_curriculum.grade
            skill_info.volume = skill_curriculum.volume
            skill_info.chapter = skill_curriculum.chapter
            
            # 計算前置技能數量 (關鍵！前端需要此資料)
            skill_info.prereq_count = len(skill_info.prerequisites)
            
            skills_list.append(skill_info)
        
        # 6. 準備篩選器選項 (動態查詢)
        # 基礎查詢
        base_query = db.session.query(SkillCurriculum).filter(
            SkillCurriculum.skill_id.in_(
                db.session.query(SkillInfo.skill_id).filter(SkillInfo.is_active.is_(True))
            )
        )
        
        # Curriculum 選項
        curriculums = [r[0] for r in base_query.with_entities(
            distinct(SkillCurriculum.curriculum)
        ).order_by(SkillCurriculum.curriculum).all()]
        
        # Grade 選項 (基於已選 curriculum)
        grade_query = base_query
        if f_curriculum != 'all':
            grade_query = grade_query.filter(SkillCurriculum.curriculum == f_curriculum)
        grades = [r[0] for r in grade_query.with_entities(
            distinct(SkillCurriculum.grade)
        ).order_by(SkillCurriculum.grade).all()]
        
        # Volume 選項 (基於已選 curriculum + grade)
        volume_query = grade_query
        if f_grade != 'all':
            volume_query = volume_query.filter(SkillCurriculum.grade == int(f_grade))
        volumes = [r[0] for r in volume_query.with_entities(
            distinct(SkillCurriculum.volume)
        ).order_by(SkillCurriculum.volume).all()]
        
        # Chapter 選項 (基於已選 curriculum + grade + volume)
        chapter_query = volume_query
        if f_volume != 'all':
            chapter_query = chapter_query.filter(SkillCurriculum.volume == f_volume)
        chapters = [r[0] for r in chapter_query.with_entities(
            distinct(SkillCurriculum.chapter)
        ).order_by(SkillCurriculum.chapter).all()]
        
        # 7. 準備模板資料
        filters = {
            'curriculums': curriculums,
            'grades': grades,
            'volumes': volumes,
            'chapters': chapters
        }
        
        selected = {
            'f_curriculum': f_curriculum,
            'f_grade': f_grade,
            'f_volume': f_volume,
            'f_chapter': f_chapter
        }
        
        return render_template('admin_prerequisites.html',
                               skills=skills_list,
                               filters=filters,
                               selected=selected,
                               username=current_user.username)
    
    except Exception as e:
        current_app.logger.error(f"Error in admin_prerequisites: {e}\n{traceback.format_exc()}")
        flash(f'載入技能關聯頁面時發生錯誤：{e}', 'danger')
        return redirect(url_for('dashboard'))


# ==========================================
# API: 取得前置技能列表
# ==========================================
@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['GET'])
@login_required
def api_get_prerequisites(skill_id):
    """
    取得指定技能的所有前置技能
    """
    if not (current_user.is_admin or current_user.role == "teacher"):
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        skill = db.session.get(SkillInfo, skill_id)
        if not skill:
            return jsonify({"success": False, "message": "技能不存在"}), 404
        
        # 使用 relationship 取得前置技能
        prerequisites_data = [
            {
                'skill_id': prereq.skill_id,
                'skill_ch_name': prereq.skill_ch_name
            }
            for prereq in skill.prerequisites
        ]
        
        return jsonify({"success": True, "data": prerequisites_data})
    
    except Exception as e:
        current_app.logger.error(f"Error fetching prerequisites for {skill_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# API: 新增前置技能
# ==========================================
@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['POST'])
@login_required
def api_add_prerequisite(skill_id):
    """
    為指定技能新增前置技能
    """
    if not (current_user.is_admin or current_user.role == "teacher"):
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        data = request.get_json()
        prereq_id = data.get('prereq_id')
        
        if not prereq_id:
            return jsonify({"success": False, "message": "缺少 prereq_id 參數"}), 400
        
        # 檢查技能是否存在
        target_skill = db.session.get(SkillInfo, skill_id)
        prereq_skill = db.session.get(SkillInfo, prereq_id)
        
        if not target_skill:
            return jsonify({"success": False, "message": f"目標技能 {skill_id} 不存在"}), 404
        if not prereq_skill:
            return jsonify({"success": False, "message": f"前置技能 {prereq_id} 不存在"}), 404
        
        # 檢查自我依賴
        if skill_id == prereq_id:
            return jsonify({"success": False, "message": "技能不能將自己設為前置技能"}), 400
        
        # 檢查是否已存在
        if prereq_skill in target_skill.prerequisites:
            return jsonify({"success": False, "message": "此前置技能已存在"}), 400
        
        # 新增關聯
        target_skill.prerequisites.append(prereq_skill)
        db.session.commit()
        
        return jsonify({"success": True, "message": "前置技能新增成功"})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding prerequisite: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# API: 移除前置技能
# ==========================================
@core_bp.route('/api/skills/<string:skill_id>/prerequisites/<string:prereq_id>', methods=['DELETE'])
@login_required
def api_remove_prerequisite(skill_id, prereq_id):
    """
    移除指定技能的前置技能
    """
    if not (current_user.is_admin or current_user.role == "teacher"):
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        target_skill = db.session.get(SkillInfo, skill_id)
        prereq_skill = db.session.get(SkillInfo, prereq_id)
        
        if not target_skill:
            return jsonify({"success": False, "message": f"目標技能 {skill_id} 不存在"}), 404
        if not prereq_skill:
            return jsonify({"success": False, "message": f"前置技能 {prereq_id} 不存在"}), 404
        
        # 檢查關聯是否存在
        if prereq_skill not in target_skill.prerequisites:
            return jsonify({"success": False, "message": "此前置技能不存在於關聯中"}), 400
        
        # 移除關聯
        target_skill.prerequisites.remove(prereq_skill)
        db.session.commit()
        
        return jsonify({"success": True, "message": "前置技能移除成功"})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing prerequisite: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# API: 搜尋技能 (for Select2)
# ==========================================
@core_bp.route('/api/skills/search', methods=['GET'])
@login_required
def api_search_skills():
    """
    搜尋技能 - 供 Select2 下拉選單使用
    """
    if not (current_user.is_admin or current_user.role == "teacher"):
        return jsonify({"results": []}), 403
    
    try:
        term = request.args.get('term', '').strip()
        
        if not term:
            return jsonify({"results": []})
        
        # 模糊搜尋 skill_id 或 skill_ch_name
        query = db.session.query(SkillInfo).filter(
            SkillInfo.is_active.is_(True),
            db.or_(
                SkillInfo.skill_id.like(f'%{term}%'),
                SkillInfo.skill_ch_name.like(f'%{term}%')
            )
        ).order_by(SkillInfo.skill_ch_name).limit(20)
        
        results = [
            {
                'id': skill.skill_id,
                'text': f"{skill.skill_ch_name} ({skill.skill_id})"
            }
            for skill in query.all()
        ]
        
        return jsonify({"results": results})
    
    except Exception as e:
        current_app.logger.error(f"Error searching skills: {e}")
        return jsonify({"results": []})

@core_bp.route('/examples', methods=['GET'])
@login_required
def admin_examples():
    """
    課本例題管理頁面 - 支援多層篩選與分頁
    """
    # 權限檢查
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))

    # 讀取篩選參數
    f_curriculum = request.args.get('f_curriculum')
    f_grade = request.args.get('f_grade')
    f_volume = request.args.get('f_volume')
    f_chapter = request.args.get('f_chapter')
    f_section = request.args.get('f_section')
    f_paragraph = request.args.get('f_paragraph')
    f_skill_id = request.args.get('f_skill_id')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # 建構查詢 - Join SkillInfo (必要) 和 SkillCurriculum (用於篩選)
    from models import TextbookExample
    query = db.session.query(TextbookExample).join(
        SkillInfo, TextbookExample.skill_id == SkillInfo.skill_id
    )

    # 如果有課綱篩選條件,才 join SkillCurriculum
    if any([f_curriculum, f_grade, f_volume, f_chapter, f_section, f_paragraph]):
        query = query.outerjoin(
            SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id
        )
        
        # 應用篩選條件
        if f_curriculum:
            query = query.filter(SkillCurriculum.curriculum == f_curriculum)
        if f_grade:
            query = query.filter(SkillCurriculum.grade == int(f_grade))
        if f_volume:
            query = query.filter(SkillCurriculum.volume == f_volume)
        if f_chapter:
            query = query.filter(SkillCurriculum.chapter == f_chapter)
        if f_section:
            query = query.filter(SkillCurriculum.section == f_section)
        if f_paragraph:
            query = query.filter(SkillCurriculum.paragraph == f_paragraph)

    # 技能 ID 篩選 (直接在 TextbookExample 上)
    if f_skill_id:
        query = query.filter(TextbookExample.skill_id == f_skill_id)

    # 排序並分頁
    query = query.distinct().order_by(TextbookExample.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 準備篩選器下拉選單資料
    curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).all()]
    
    q_grades = db.session.query(distinct(SkillCurriculum.grade))
    if f_curriculum: q_grades = q_grades.filter_by(curriculum=f_curriculum)
    grades = sorted([r[0] for r in q_grades.filter(SkillCurriculum.grade != None).all()])

    q_vols = db.session.query(distinct(SkillCurriculum.volume))
    if f_curriculum: q_vols = q_vols.filter_by(curriculum=f_curriculum)
    if f_grade: q_vols = q_vols.filter_by(grade=int(f_grade))
    volumes = [r[0] for r in q_vols.all()]

    q_chaps = db.session.query(distinct(SkillCurriculum.chapter))
    if f_curriculum: q_chaps = q_chaps.filter_by(curriculum=f_curriculum)
    if f_grade: q_chaps = q_chaps.filter_by(grade=int(f_grade))
    if f_volume: q_chaps = q_chaps.filter_by(volume=f_volume)
    chapters = [r[0] for r in q_chaps.all()]

    q_secs = db.session.query(distinct(SkillCurriculum.section))
    if f_curriculum: q_secs = q_secs.filter_by(curriculum=f_curriculum)
    if f_grade: q_secs = q_secs.filter_by(grade=int(f_grade))
    if f_volume: q_secs = q_secs.filter_by(volume=f_volume)
    if f_chapter: q_secs = q_secs.filter_by(chapter=f_chapter)
    sections = [r[0] for r in q_secs.all()]

    q_paras = db.session.query(distinct(SkillCurriculum.paragraph))
    if f_curriculum: q_paras = q_paras.filter_by(curriculum=f_curriculum)
    if f_grade: q_paras = q_paras.filter_by(grade=int(f_grade))
    if f_volume: q_paras = q_paras.filter_by(volume=f_volume)
    if f_chapter: q_paras = q_paras.filter_by(chapter=f_chapter)
    if f_section: q_paras = q_paras.filter_by(section=f_section)
    paragraphs = [r[0] for r in q_paras.filter(SkillCurriculum.paragraph != None).all()]

    # 準備課綱對照表
    curriculum_map = {
        'junior_high': '國中',
        'general': '普高',
        'technical': '技高',
        'elementary': '國小',
        'sh': '普高 (舊碼)',
        'jh': '國中 (舊碼)',
        'vhs': '技高 (舊碼)',
        'elem': '國小 (舊碼)'
    }

    all_grades = db.session.query(distinct(SkillCurriculum.grade)).all()
    grade_map = {str(g[0]): str(g[0]) for g in all_grades if g[0] is not None}

    # 準備技能列表 (供新增/編輯 Modal 使用)
    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()

    # 包裝變數
    filters = {
        'curriculums': curriculums,
        'grades': grades,
        'volumes': volumes,
        'chapters': chapters,
        'sections': sections,
        'paragraphs': paragraphs
    }

    selected_filters = {
        'f_curriculum': f_curriculum,
        'f_grade': f_grade,
        'f_volume': f_volume,
        'f_chapter': f_chapter,
        'f_section': f_section,
        'f_paragraph': f_paragraph,
        'f_skill_id': f_skill_id
    }

    return render_template('admin_examples.html',
                           pagination=pagination,
                           filters=filters,
                           selected_filters=selected_filters,
                           curriculum_map=curriculum_map,
                           grade_map=grade_map,
                           skills=skills,
                           username=current_user.username)

@core_bp.route('/examples/add', methods=['POST'])
@login_required
def admin_add_example():
    """
    新增課本例題
    """
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('core.admin_examples'))
    
    try:
        from models import TextbookExample
        
        new_example = TextbookExample(
            skill_id=request.form.get('skill_id'),
            problem_text=request.form.get('problem_text'),
            correct_answer=request.form.get('correct_answer', ''),
            detailed_solution=request.form.get('detailed_solution', ''),
            source_curriculum=request.form.get('source_curriculum', ''),
            source_volume=request.form.get('source_volume', ''),
            source_chapter=request.form.get('source_chapter', ''),
            source_section=request.form.get('source_section', ''),
            source_description=request.form.get('source_description', ''),
            source_paragraph=request.form.get('source_paragraph'),
            problem_type=request.form.get('problem_type'),
            difficulty_level=int(request.form.get('difficulty_level', 1))
        )
        
        db.session.add(new_example)
        db.session.commit()
        flash('例題新增成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')
        current_app.logger.error(f"Add example error: {e}")
    
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/edit/<int:example_id>', methods=['POST'])
@login_required
def admin_edit_example(example_id):
    """
    編輯課本例題
    """
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('core.admin_examples'))
    
    try:
        from models import TextbookExample
        example = db.session.get(TextbookExample, example_id)
        
        if not example:
            flash('找不到該例題', 'warning')
            return redirect(url_for('core.admin_examples'))
        
        # 更新欄位
        example.skill_id = request.form.get('skill_id')
        example.problem_text = request.form.get('problem_text')
        example.correct_answer = request.form.get('correct_answer', '')
        example.detailed_solution = request.form.get('detailed_solution', '')
        example.source_curriculum = request.form.get('source_curriculum', '')
        example.source_volume = request.form.get('source_volume', '')
        example.source_chapter = request.form.get('source_chapter', '')
        example.source_section = request.form.get('source_section', '')
        example.source_description = request.form.get('source_description', '')
        example.source_paragraph = request.form.get('source_paragraph')
        example.problem_type = request.form.get('problem_type')
        example.difficulty_level = int(request.form.get('difficulty_level', 1))
        
        db.session.commit()
        flash('例題更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗：{str(e)}', 'danger')
        current_app.logger.error(f"Edit example error: {e}")
    
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/delete/<int:example_id>', methods=['POST'])
@login_required
def admin_delete_example(example_id):
    """
    刪除課本例題
    """
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('core.admin_examples'))
    
    try:
        from models import TextbookExample
        example = db.session.get(TextbookExample, example_id)
        
        if not example:
            flash('找不到該例題', 'warning')
            return redirect(url_for('core.admin_examples'))
        
        db.session.delete(example)
        db.session.commit()
        flash('例題刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
        current_app.logger.error(f"Delete example error: {e}")
    
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/<int:example_id>/details', methods=['GET'])
@login_required
def admin_get_example_details(example_id):
    """
    API: 獲取單一例題的詳細資料 (供編輯 Modal 使用)
    """
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        from models import TextbookExample
        ex = db.session.get(TextbookExample, example_id)
        
        if not ex:
            return jsonify({'success': False, 'message': '找不到該例題'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': ex.id,
                'skill_id': ex.skill_id,
                'problem_text': ex.problem_text or '',
                'correct_answer': ex.correct_answer or '',
                'detailed_solution': ex.detailed_solution or '',
                'source_curriculum': ex.source_curriculum or '',
                'source_volume': ex.source_volume or '',
                'source_chapter': ex.source_chapter or '',
                'source_section': ex.source_section or '',
                'source_description': ex.source_description or '',
                'source_paragraph': ex.source_paragraph or '',
                'problem_type': ex.problem_type or '',
                'difficulty_level': ex.difficulty_level or 1
            }
        })
    except Exception as e:
        current_app.logger.error(f"Get Example Details Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/textbook_importer', methods=['GET', 'POST'])
@login_required
def admin_textbook_importer():
    # 1. 權限檢查
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # --- Debug Logs ---
        # print(f"DEBUG: Files Data: {request.files}") # 除錯用
        
        target_files = []
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # 1. 嘗試取得單一檔案
        single_file = request.files.get('textbook_pdf')
        
        # 2. 嘗試取得批次資料夾檔案 (這是關鍵修正!)
        # 前端若是 <input type="file" name="textbook_folder" webkitdirectory>，會傳送檔案列表
        batch_files = request.files.getlist('textbook_folder')

        # Extract curriculum info (Common for both modes)
        curriculum_info = {
            'curriculum': request.form.get('curriculum'),
            'publisher': request.form.get('publisher'),
            'grade': request.form.get('grade'),
            'volume': request.form.get('volume')
        }
        skip_code_gen = request.form.get('skip_code_gen') == 'on'

        # --- 邏輯分支 ---

        # Case A: 單一檔案有效
        if single_file and single_file.filename != '':
            print(f"DEBUG: Mode A - Single File: {single_file.filename}")
            try:
                filename = secure_filename(single_file.filename)
                file_path = os.path.join(upload_dir, filename)
                single_file.save(file_path)
                target_files.append(file_path)
            except Exception as e:
                flash(f'單檔儲存失敗: {e}', 'error')
                return redirect(request.url)

        # Case B: 批次檔案有效 (檢查列表是否非空，且第一個檔案有名稱)
        elif batch_files and len(batch_files) > 0 and batch_files[0].filename != '':
            print(f"DEBUG: Mode B - Batch Upload: {len(batch_files)} files received")
            
            saved_count = 0
            for f in batch_files:
                # 過濾掉空檔名或非 PDF/Word 檔
                if f.filename == '' or not (f.filename.lower().endswith('.pdf') or f.filename.lower().endswith('.docx') or f.filename.lower().endswith('.doc')):
                    continue
                
                try:
                    # secure_filename 會把 "folder/file.pdf" 變成 "folder_file.pdf" 或 "file.pdf"
                    # 這邊我們只求存下來能分析即可
                    safe_name = secure_filename(os.path.basename(f.filename))
                    # 避免檔名重複覆蓋，加個 uuid 前綴 (可選，這裡先維持簡單)
                    save_path = os.path.join(upload_dir, safe_name)
                    
                    f.save(save_path)
                    target_files.append(save_path)
                    saved_count += 1
                except Exception as e:
                    print(f"DEBUG: Skipped file {f.filename} due to error: {e}")

            if saved_count == 0:
                flash('上傳的資料夾中沒有有效的 PDF 或 Word 檔案。', 'warning')
                return redirect(request.url)

        # Case C: 無有效輸入
        else:
            print("DEBUG: Mode C - No Input Provided")
            flash('請選擇「PDF 檔案」或「資料夾」。', 'warning')
            return redirect(request.url)

        # --- 啟動背景任務 ---
        if target_files:
            try:
                # TASK_QUEUES 已於全域定義，直接使用
                task_id = str(uuid.uuid4())
                q = queue.Queue()
                
                # 存入全域字典 - 務必在 Thread Start 前完成
                TASK_QUEUES[task_id] = q

                app = current_app._get_current_object()
                app_context = app.app_context()

                thread = threading.Thread(
                    target=background_processing,
                    args=(target_files, q, app_context, curriculum_info, skip_code_gen)
                )
                thread.start()

                flash(f'分析啟動！共 {len(target_files)} 個檔案排程中...', 'success')
                return redirect(url_for('core.importer_status', task_id=task_id))
            except Exception as e:
                current_app.logger.error(f"Task Start Error: {e}")
                flash(f"任務啟動失敗: {e}", 'error')
                return redirect(request.url)
                
    return render_template('textbook_importer.html')

@core_bp.route('/importer/status/<task_id>')
@login_required
def importer_status(task_id):
    # 確認任務是否存在 (簡單檢查)
    if task_id not in TASK_QUEUES:
        flash('找不到該任務或任務已過期', 'warning')
        return redirect(url_for('core.admin_textbook_importer'))
    return render_template('importer_status.html', task_id=task_id)

@core_bp.route('/importer/stream/<task_id>')
@login_required
def importer_stream(task_id):
    def event_stream():
        q = TASK_QUEUES.get(task_id)
        if not q:
            yield "data: END_OF_STREAM\n\n"
            return

        while True:
            # 阻塞式讀取，直到有訊息
            msg = q.get()
            yield f"data: {msg}\n\n"
            
            if msg == "END_OF_STREAM":
                # 清理 Queue 以釋放記憶體
                TASK_QUEUES.pop(task_id, None)
                break

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

# === 資料庫管理 (從主應用程式移入) ===


@core_bp.route('/db_maintenance', methods=['GET', 'POST'])
@login_required
def db_maintenance():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('您沒有權限存取此頁面。', 'danger')
        return redirect(url_for('dashboard'))

    try:
        if request.method == 'POST':
            action = request.form.get('action')
            table_name = request.form.get('table_name')

            # === 全域操作 ===
            if action == 'export_db':
                # 匯出整個資料庫為 Excel
                output = io.BytesIO()
                # [Optimization] 使用更穩定的引擎
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                
                inspector = db.inspect(db.engine)
                all_tables = inspector.get_table_names()
                
                for table_name in all_tables:
                    try:
                        # 1. 嘗試讀取原始資料
                        df = pd.read_sql_table(table_name, db.engine)
                        
                        # 2. 強制安全性處理：針對每一欄
                        for col in df.columns:
                            # 如果這一欄看起來應該是文字，或導致匯出出錯，我們強制將其轉為字串
                            try:
                                # 先轉為字串，避免 int() 轉換失敗
                                df[col] = df[col].astype(str)
                                
                                # 移除 Excel 不支援的控制字元
                                df[col] = df[col].apply(lambda x: re.sub(r'[\x00-\x1f\x7f-\x9f]', '', x) if x != 'None' else "")
                                
                                # 針對長文本進行 200 字截斷，保護 Excel 儲存格
                                if any(key in col.lower() for key in ['prompt', 'template', 'log', 'plan']):
                                    df[col] = df[col].apply(lambda x: x[:200] + "..." if len(x) > 200 else x)
                            except:
                                continue # 如果某一欄真的壞了，跳過該欄處理
                        
                        # 3. 寫入 Excel
                        df.to_excel(writer, sheet_name=table_name[:31], index=False)
                        current_app.logger.info(f"成功匯出表格（已強制轉型）: {table_name}")
                        
                    except Exception as e:
                        # 最終防線：如果連表格都讀不出來
                        current_app.logger.error(f"匯出 {table_name} 失敗: {str(e)}")
                        pd.DataFrame({"Fatal_Error": [str(e)]}).to_excel(writer, sheet_name=f"ERR_{table_name[:20]}", index=False)
                
                writer.close()
                output.seek(0)
                
                filename = f"kumon_math_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=filename
                )

            elif action == 'import_db':
                # 還原資料庫 (Upsert 模式 - 更新或插入)
                file = request.files.get('file')
                if file and file.filename != '':
                    try:
                        xls = pd.ExcelFile(file)
                        total_inserted = 0
                        total_updated = 0
                        
                        for sheet_name in xls.sheet_names:
                            if sheet_name in db.metadata.tables:
                                df = pd.read_excel(file, sheet_name=sheet_name)
                                
                                # Filter columns and clean NaN values thoroughly
                                inspector = db.inspect(db.engine)
                                table_columns = [c['name'] for c in inspector.get_columns(sheet_name)]
                                df_filtered = df[[col for col in df.columns if col in table_columns]]
                                
                                # Clean NaN values: convert to None for proper NULL handling
                                df_filtered = df_filtered.where(pd.notnull(df_filtered), None)
                                # Also replace any remaining NaN, inf, -inf with None
                                df_filtered = df_filtered.replace([float('inf'), float('-inf')], None)
                                
                                # Get primary key columns for this table
                                pk_columns = inspector.get_pk_constraint(sheet_name)['constrained_columns']
                                
                                # Use INSERT OR REPLACE for SQLite (simpler and more efficient)
                                for _, row in df_filtered.iterrows():
                                    row_dict = row.to_dict()
                                    
                                    # Clean the row_dict: ensure no NaN values
                                    cleaned_dict = {}
                                    for key, value in row_dict.items():
                                        if pd.isna(value):
                                            cleaned_dict[key] = None
                                        else:
                                            cleaned_dict[key] = value
                                    
                                    # Use INSERT OR REPLACE (SQLite specific)
                                    # This will update if PK exists, insert if not
                                    cols = ', '.join(cleaned_dict.keys())
                                    placeholders = ', '.join([f":{col}" for col in cleaned_dict.keys()])
                                    
                                    # INSERT OR REPLACE is SQLite's upsert
                                    upsert_query = f"INSERT OR REPLACE INTO {sheet_name} ({cols}) VALUES ({placeholders})"
                                    
                                    try:
                                        with db.engine.connect() as conn:
                                            result = conn.execute(db.text(upsert_query), cleaned_dict)
                                            conn.commit()
                                            
                                            # Check if it was an insert or update
                                            # In SQLite, rowcount > 0 means operation succeeded
                                            if result.rowcount > 0:
                                                # Check if record existed before
                                                if pk_columns:
                                                    pk_values = {col: cleaned_dict[col] for col in pk_columns if col in cleaned_dict}
                                                    check_query = f"SELECT COUNT(*) as cnt FROM {sheet_name} WHERE "
                                                    conditions = [f"{col} = :{col}" for col in pk_values.keys()]
                                                    check_query += " AND ".join(conditions)
                                                    
                                                    # Simple heuristic: if we have all PK values, assume update
                                                    if all(v is not None for v in pk_values.values()):
                                                        total_updated += 1
                                                    else:
                                                        total_inserted += 1
                                                else:
                                                    total_inserted += 1
                                    except Exception as e:
                                        current_app.logger.warning(f"Failed to upsert row in {sheet_name}: {e}")
                                        # Continue with next row
                                        pass
                        
                        db.session.commit()
                        flash(f'資料庫還原成功！新增 {total_inserted} 筆，更新 {total_updated} 筆', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash(f'還原失敗: {str(e)}', 'danger')
                        current_app.logger.error(f"Import DB error: {e}\n{traceback.format_exc()}")
                else:
                    flash('未選擇檔案', 'warning')
                return redirect(url_for('core.db_maintenance'))

            elif action == 'clear_all_data':
                # 清空所有資料（保留 admin 帳號）
                db.session.remove()
                
                meta = db.metadata
                success_count = 0
                skipped_count = 0
                
                # 遍歷所有表格
                for table in reversed(meta.sorted_tables):
                    table_name = table.name
                    try:
                        # 特殊處理 users 表
                        if table_name == 'users':
                            db.session.query(User).filter(User.username != 'admin').delete(synchronize_session=False)
                            current_app.logger.info("Cleared non-admin users from 'users' table.")
                        else:
                            # [Safe Clear] 使用 text() 執行 SQL，並捕捉錯誤
                            db.session.execute(text(f"DELETE FROM {table_name}"))
                            current_app.logger.info(f"Cleared all data from '{table_name}' table.")
                        
                        # [關鍵] 每個表刪除後立即提交，隔離錯誤
                        db.session.commit()
                        success_count += 1
                        
                    except Exception as e:
                        db.session.rollback()
                        # 優雅地處理表不存在的情況
                        if "no such table" in str(e):
                            skipped_count += 1
                            current_app.logger.warning(f"Skipped {table_name} (Table not found)")
                        else:
                            current_app.logger.error(f"Failed to clear {table_name}: {e}")

                flash(f'全站資料清空完成！(成功: {success_count}, 跳過: {skipped_count})，Admin 帳號已保留。', 'success')

            # === 批次匯入操作 ===
            elif action == 'batch_import_folder':
                # 批次匯入課程綱要 (SkillCurriculum)
                files = request.files.getlist('files')
                if not files or files[0].filename == '':
                    flash('未選擇檔案', 'warning')
                    return redirect(url_for('core.db_maintenance'))
                
                success_count = 0
                error_count = 0
                
                for file in files:
                    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                        try:
                            if file.filename.endswith('.csv'):
                                df = pd.read_csv(file)
                            else:
                                df = pd.read_excel(file)
                            
                            # 標準化欄位
                            df.columns = [str(c).lower().strip() for c in df.columns]
                            
                            # 預期欄位: curriculum, grade, volume, chapter, section, skill_id
                            for _, row in df.iterrows():
                                if pd.isna(row.get('skill_id')): continue
                                
                                item = SkillCurriculum(
                                    curriculum=row.get('curriculum', 'general'),
                                    grade=int(row.get('grade', 10)),
                                    volume=row.get('volume', ''),
                                    chapter=row.get('chapter', ''),
                                    section=row.get('section', ''),
                                    paragraph=row.get('paragraph', '') if 'paragraph' in row and not pd.isna(row['paragraph']) else None,
                                    skill_id=str(row['skill_id']).strip(),
                                    display_order=int(row.get('display_order', 0)) if 'display_order' in row else 0,
                                    difficulty_level=int(row.get('difficulty_level', 1)) if 'difficulty_level' in row else 1
                                )
                                db.session.add(item)
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            current_app.logger.error(f"Error importing file {file.filename}: {e}")
                
                db.session.commit()
                flash(f'批次匯入完成：成功 {success_count} 個檔案，失敗 {error_count} 個檔案。', 'success')
                return redirect(url_for('core.db_maintenance'))

            elif action == 'batch_upsert_skills_info':
                # 批次更新/新增技能資訊 (SkillInfo)
                files = request.files.getlist('files')
                if not files or files[0].filename == '':
                    flash('未選擇檔案', 'warning')
                    return redirect(url_for('core.db_maintenance'))
                
                count = 0
                for file in files:
                    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                        try:
                            if file.filename.endswith('.csv'):
                                df = pd.read_csv(file)
                            else:
                                df = pd.read_excel(file)
                            
                            df.columns = [str(c).lower().strip() for c in df.columns]
                            
                            for _, row in df.iterrows():
                                if pd.isna(row.get('skill_id')): continue
                                skill_id = str(row['skill_id']).strip()
                                
                                skill = db.session.get(SkillInfo, skill_id)
                                if not skill:
                                    skill = SkillInfo(skill_id=skill_id)
                                    db.session.add(skill)
                                
                                # Update fields if present
                                if 'skill_en_name' in row: skill.skill_en_name = row['skill_en_name']
                                if 'skill_ch_name' in row: skill.skill_ch_name = row['skill_ch_name']
                                if 'category' in row: skill.category = row['category']
                                if 'description' in row: skill.description = row['description']
                                if 'gemini_prompt' in row: skill.gemini_prompt = row['gemini_prompt']
                                if 'consecutive_correct_required' in row: 
                                    skill.consecutive_correct_required = int(row['consecutive_correct_required'])
                                
                                count += 1
                        except Exception as e:
                            current_app.logger.error(f"Error processing skill file {file.filename}: {e}")
                
                db.session.commit()
                flash(f'批次處理完成，共處理 {count} 筆技能資料。', 'success')
                return redirect(url_for('core.db_maintenance'))


            # === 單一表格操作 (既有功能) ===
            table = db.metadata.tables.get(table_name)
            if table is None and action in ['clear_data', 'drop_table', 'upload_excel']:
                flash(f'表格 "{table_name}" 不存在。', 'danger')
                return redirect(url_for('core.db_maintenance'))

            if action == 'clear_data':
                try:
                    # [Safe Clear] 使用安全寫法
                    db.session.execute(text(f"DELETE FROM {table_name}"))
                    db.session.commit()
                    flash(f'表格 "{table_name}" 的資料已成功清除。', 'success')
                except Exception as e:
                    db.session.rollback()
                    if "no such table" in str(e):
                        flash(f'清除失敗：表格 "{table_name}" 尚未建立。', 'warning')
                    else:
                        flash(f'清除失敗: {str(e)}', 'danger')
            elif action == 'drop_table':
                table.drop(db.engine)
                flash(f'表格 "{table_name}" 已成功刪除。', 'success')
            elif action == 'upload_excel':
                file = request.files.get('file')
                if file and file.filename != '':
                    inspector = db.inspect(db.engine)
                    table_columns = [c['name'] for c in inspector.get_columns(table_name)]
                    df = pd.read_excel(file)
                    df_filtered = df[[col for col in df.columns if col in table_columns]]
                    df_filtered = df_filtered.where(pd.notnull(df_filtered), None)
                    df_filtered.to_sql(table_name, db.engine, if_exists='append', index=False)
                    flash(f'成功將資料從 Excel 匯入到表格 "{table_name}"。', 'success')
                else:
                    flash('沒有選擇檔案或檔案無效。', 'warning')
            
            return redirect(url_for('core.db_maintenance'))

        # GET request
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        
        # 修改：不再過濾，直接顯示資料庫內所有表格，並按字母排序
        tables = sorted(all_tables)
        
        return render_template('db_maintenance.html', tables=tables)
    except Exception as e:
        current_app.logger.error(f"Error in db_maintenance: {e}\n{traceback.format_exc()}")
        flash(f'載入資料庫管理頁面時發生錯誤，請檢查伺服器日誌。錯誤：{e}', 'danger')
        return redirect(url_for('dashboard'))

@core_bp.route('/upload_db', methods=['POST'])
@login_required
def upload_db():
    # 權限檢查：僅管理員可執行
    if not current_user.is_admin:
        flash('您沒有權限執行此操作', 'danger')
        return redirect(url_for('core.db_maintenance'))

    if 'file' not in request.files:
        flash('沒有檔案被上傳', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    file = request.files['file']
    if file.filename == '':
        flash('未選擇檔案', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if file and (file.filename.endswith('.xlsx')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            success, message = import_excel_to_db(filepath)

            if success:
                # 把換行符號轉成 HTML 的 <br> 顯示在 Flash 訊息
                flash(Markup(message.replace('\n', '<br>')), 'success')
            else:
                flash(message, 'danger')
                
        except Exception as e:
            flash(f'處理檔案時發生錯誤: {str(e)}', 'danger')
            
        # 處理完後刪除暫存檔
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return redirect(url_for('core.db_maintenance'))
    else:
        flash('不支援的檔案格式，請上傳 .xlsx', 'danger')
        return redirect(url_for('core.db_maintenance'))

@core_bp.route('/admin/import_textbook_examples', methods=['POST'])
@login_required
def import_textbook_examples():
    """處理課本例題匯入"""
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('您沒有權限執行此操作。', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if 'file' not in request.files:
        flash('沒有選擇檔案', 'error')
        return redirect(url_for('core.db_maintenance'))
        
    file = request.files['file']
    if file.filename == '':
        flash('未選擇檔案', 'error')
        return redirect(url_for('core.db_maintenance'))
        
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # 執行匯入
            # 現在統一使用支援多 Sheet 的 Excel 匯入器
            success, message = import_excel_to_db(filepath)
            
            # 清理暫存檔
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if success:
                flash(Markup(message.replace('\n', '<br>')), 'success')
            else:
                flash(message, 'danger')
            
        except Exception as e:
            current_app.logger.error(f"Import textbook examples failed: {e}\n{traceback.format_exc()}")
            flash(f'匯入失敗: {str(e)}', 'error')
            
    return redirect(url_for('core.db_maintenance'))

# === 課程分類管理 (從 app.py 移入) ===

@core_bp.route('/curriculum', methods=['GET', 'POST'])
@login_required
def admin_curriculum():
    # 1. 權限檢查
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))

    # 2. POST: 新增邏輯 (維持不變)
    if request.method == 'POST':
        try:
            # 這裡保留你原本的新增程式碼...
            # (簡略範例，請保留原有的詳細實作)
            new_curr = SkillCurriculum(
                skill_id=request.form.get('skill_id'),
                curriculum=request.form.get('curriculum'),
                grade=int(request.form.get('grade')) if request.form.get('grade') and request.form.get('grade').isdigit() else 0,
                volume=request.form.get('volume'),
                chapter=request.form.get('chapter'),
                section=request.form.get('section'),
                paragraph=request.form.get('paragraph'),
                difficulty_level=int(request.form.get('difficulty_level', 1)),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(new_curr)
            db.session.commit()
            flash('新增成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'新增失敗: {str(e)}', 'error')
        return redirect(url_for('core.admin_curriculum'))

    # 3. GET: 處理篩選與顯示
    
    # [Fix 2] 增加讀取 section 參數
    sel_curr = request.args.get('curriculum')
    sel_grade = request.args.get('grade')
    sel_vol = request.args.get('volume')
    sel_chap = request.args.get('chapter')
    sel_sec = request.args.get('section') # 新增

    # 建構查詢
    query = SkillCurriculum.query.join(SkillInfo)
    if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
    if sel_grade: query = query.filter(SkillCurriculum.grade == int(sel_grade))
    if sel_vol: query = query.filter(SkillCurriculum.volume == sel_vol)
    if sel_chap: query = query.filter(SkillCurriculum.chapter == sel_chap)
    if sel_sec: query = query.filter(SkillCurriculum.section == sel_sec) # [Fix 2] 新增篩選
    
    items = query.order_by(SkillCurriculum.id.desc()).limit(200).all()

    # [Fix] Python-side Natural Sorting
    def natural_keys(text):
        if not text: return []
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]

    items.sort(key=lambda x: (
        x.grade if x.grade is not None else 999,
        x.volume or '',
        x.display_order if x.display_order and x.display_order > 0 else 999999,
        natural_keys(x.chapter),
        natural_keys(x.section)
    ))

    # 準備下拉選單資料
    curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).all()]
    
    q_grades = db.session.query(distinct(SkillCurriculum.grade))
    if sel_curr: q_grades = q_grades.filter_by(curriculum=sel_curr)
    grades = sorted([r[0] for r in q_grades.filter(SkillCurriculum.grade != None).all()])

    q_vols = db.session.query(distinct(SkillCurriculum.volume))
    if sel_curr: q_vols = q_vols.filter_by(curriculum=sel_curr)
    if sel_grade: q_vols = q_vols.filter_by(grade=sel_grade)
    volumes = [r[0] for r in q_vols.all()]

    q_chaps = db.session.query(distinct(SkillCurriculum.chapter))
    if sel_curr: q_chaps = q_chaps.filter_by(curriculum=sel_curr)
    if sel_grade: q_chaps = q_chaps.filter_by(grade=sel_grade)
    if sel_vol: q_chaps = q_chaps.filter_by(volume=sel_vol)
    chapters = [r[0] for r in q_chaps.all()]

    # [Fix 2] Level 5: 小節 (Section) - 新增這一段
    q_secs = db.session.query(distinct(SkillCurriculum.section))
    if sel_curr: q_secs = q_secs.filter_by(curriculum=sel_curr)
    if sel_grade: q_secs = q_secs.filter_by(grade=sel_grade)
    if sel_vol: q_secs = q_secs.filter_by(volume=sel_vol)
    if sel_chap: q_secs = q_secs.filter_by(chapter=sel_chap)
    sections = [r[0] for r in q_secs.all()]

    # 準備對照表
    all_grades = db.session.query(distinct(SkillCurriculum.grade)).all()
    grade_map = {str(g[0]): str(g[0]) for g in all_grades if g[0] is not None}
    
    # [Fix 1] 擴充 Curriculum Map 對應表
    curriculum_map = {
        'junior_high': '國中',
        'general': '普高',
        'technical': '技高',
        'elementary': '國小',
        'sh': '普高 (舊碼)', # 保留舊碼相容
        'jh': '國中 (舊碼)',
        'vhs': '技高 (舊碼)',
        'elem': '國小 (舊碼)'
    }

    # 包裝變數
    filters = {
        'curriculums': curriculums,
        'grades': grades,
        'volumes': volumes,
        'chapters': chapters,
        'sections': sections # [Fix 2] 加入 sections
    }
    
    selected_filters = {
        'f_curriculum': sel_curr,
        'f_grade': sel_grade,
        'f_volume': sel_vol,
        'f_chapter': sel_chap,
        'f_section': sel_sec # [Fix 2] 加入 section
    }

    return render_template('admin_curriculum.html', 
                           items=items,
                           filters=filters,
                           selected_filters=selected_filters,
                           grade_map=grade_map,
                           curriculum_map=curriculum_map, # <--- 這次一定要加上這個！
                           
                           # 相容性變數
                           curriculums=curriculums,
                           grades=grades,
                           volumes=volumes,
                           chapters=chapters,
                           sections=sections, # [Fix 2]
                           skills=SkillInfo.query.all()
                           )

@core_bp.route('/curriculum/add', methods=['POST'])
@login_required
def admin_add_curriculum():
    data = request.form
    try:
        new_item = SkillCurriculum(
            curriculum=data['curriculum'],
            grade=int(data['grade']),
            volume=data['volume'],
            chapter=data['chapter'],
            section=data.get('section', ''),
            skill_id=data['skill_id'],
            display_order=int(data.get('display_order', 99)),
            difficulty_level=int(data.get('difficulty_level', 1)),
        )
        db.session.add(new_item)
        db.session.commit()
        flash('課程分類新增成功！', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('新增失敗：該課程分類項目已存在（唯一性約束衝突）。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_curriculum(id):  # 函式名稱必須是 admin_edit_curriculum
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        curr = SkillCurriculum.query.get_or_404(id)
        # 更新欄位
        curr.curriculum = request.form.get('curriculum')
        curr.grade = request.form.get('grade')
        curr.volume = request.form.get('volume')
        curr.chapter = request.form.get('chapter')
        curr.section = request.form.get('section')
        # 如果有其他欄位如 display_order 也可在此更新
        curr.skill_id = request.form.get('skill_id')
        curr.display_order = request.form.get('display_order')
        curr.difficulty_level = request.form.get('difficulty_level')
        
        db.session.commit()
        flash('課程更新成功', 'success')
        return redirect(url_for('core.admin_curriculum')) # 為了配合 Form submit 重整頁面
        
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗: {str(e)}', 'error')
        return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_curriculum(id): # 函式名稱必須是 admin_delete_curriculum
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403

    try:
        curr = SkillCurriculum.query.get_or_404(id)
        db.session.delete(curr)
        db.session.commit()
        return jsonify({'success': True, 'message': '刪除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/skills')
@login_required
def admin_skills():
    # 權限檢查
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))

    # 讀取篩選參數 (支援課綱篩選)
    sel_curr = request.args.get('f_curriculum')
    sel_grade = request.args.get('f_grade')
    sel_vol = request.args.get('f_volume')
    sel_chap = request.args.get('f_chapter')
    sel_sec = request.args.get('f_section')

    # 建構查詢 - 透過 SkillCurriculum 關聯來篩選
    if any([sel_curr, sel_grade, sel_vol, sel_chap, sel_sec]):
        # 有課綱篩選條件時，透過 SkillCurriculum 查詢
        query = db.session.query(SkillInfo).join(SkillCurriculum)
        if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: query = query.filter(SkillCurriculum.grade == int(sel_grade))
        if sel_vol: query = query.filter(SkillCurriculum.volume == sel_vol)
        if sel_chap: query = query.filter(SkillCurriculum.chapter == sel_chap)
        if sel_sec: query = query.filter(SkillCurriculum.section == sel_sec)
        query = query.distinct()
    else:
        # 無篩選條件時，顯示所有技能
        query = db.session.query(SkillInfo)

    skills = query.order_by(SkillInfo.order_index, SkillInfo.skill_id).all()

    # 準備篩選器資料 (與 admin_curriculum 相同邏輯)
    curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).all()]
    
    q_grades = db.session.query(distinct(SkillCurriculum.grade))
    if sel_curr: q_grades = q_grades.filter_by(curriculum=sel_curr)
    grades = sorted([r[0] for r in q_grades.filter(SkillCurriculum.grade != None).all()])

    q_vols = db.session.query(distinct(SkillCurriculum.volume))
    if sel_curr: q_vols = q_vols.filter_by(curriculum=sel_curr)
    if sel_grade: q_vols = q_vols.filter_by(grade=sel_grade)
    volumes = [r[0] for r in q_vols.all()]

    q_chaps = db.session.query(distinct(SkillCurriculum.chapter))
    if sel_curr: q_chaps = q_chaps.filter_by(curriculum=sel_curr)
    if sel_grade: q_chaps = q_chaps.filter_by(grade=sel_grade)
    if sel_vol: q_chaps = q_chaps.filter_by(volume=sel_vol)
    chapters = [r[0] for r in q_chaps.all()]

    q_secs = db.session.query(distinct(SkillCurriculum.section))
    if sel_curr: q_secs = q_secs.filter_by(curriculum=sel_curr)
    if sel_grade: q_secs = q_secs.filter_by(grade=sel_grade)
    if sel_vol: q_secs = q_secs.filter_by(volume=sel_vol)
    if sel_chap: q_secs = q_secs.filter_by(chapter=sel_chap)
    sections = [r[0] for r in q_secs.all()]

    # Grade Map & Curriculum Map
    all_grades = db.session.query(distinct(SkillCurriculum.grade)).all()
    grade_map = {str(g[0]): str(g[0]) for g in all_grades if g[0] is not None}
    
    curriculum_map = {
        'junior_high': '國中',
        'general': '普高',
        'technical': '技高',
        'elementary': '國小',
        'sh': '普高 (舊碼)',
        'jh': '國中 (舊碼)',
        'vhs': '技高 (舊碼)',
        'elem': '國小 (舊碼)'
    }

    filters = {
        'curriculums': curriculums,
        'grades': grades,
        'volumes': volumes,
        'chapters': chapters,
        'sections': sections
    }
    
    selected_filters = {
        'f_curriculum': sel_curr,
        'f_grade': sel_grade,
        'f_volume': sel_vol,
        'f_chapter': sel_chap,
        'f_section': sel_sec
    }

    return render_template('admin_skills.html', 
                           skills=skills,
                           filters=filters,
                           selected_filters=selected_filters,
                           grade_map=grade_map,
                           curriculum_map=curriculum_map,
                           username=current_user.username)

@core_bp.route('/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    
    if db.session.get(SkillInfo, data['skill_id']):
        flash('技能 ID 已存在！', 'danger')
        return redirect(url_for('core.admin_skills'))

    try:
        new_skill = SkillInfo(
            skill_id=data['skill_id'],
            skill_en_name=data['skill_en_name'],
            skill_ch_name=data['skill_ch_name'],
            category=data['category'],
            description=data['description'],
            input_type=data.get('input_type', 'text'),
            gemini_prompt=data['gemini_prompt'],
            consecutive_correct_required=int(data['consecutive_correct_required']),
            is_active=data.get('is_active') == 'on',
            order_index=int(data.get('order_index', 999))
        )
        db.session.add(new_skill)
        db.session.commit()
        flash('技能新增成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'新增失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/edit/<skill_id>', methods=['POST'])
@login_required
def admin_edit_skill(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))
        
    skill = db.get_or_404(SkillInfo, skill_id)
    data = request.form
    
    try:
        skill.skill_en_name = data['skill_en_name']
        skill.skill_ch_name = data['skill_ch_name']
        skill.category = data['category']
        skill.description = data['description']
        skill.input_type = data.get('input_type', 'text')
        skill.gemini_prompt = data['gemini_prompt']
        skill.consecutive_correct_required = int(data['consecutive_correct_required'])
        skill.is_active = data.get('is_active') == 'on'
        skill.order_index = int(data.get('order_index', 999))
        
        # 新增：支援 suggested_prompts
        skill.suggested_prompt_1 = data.get('suggested_prompt_1', '')
        skill.suggested_prompt_2 = data.get('suggested_prompt_2', '')
        skill.suggested_prompt_3 = data.get('suggested_prompt_3', '')
        
        db.session.commit()
        flash('技能更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    
    try:
        count = db.session.query(Progress).filter_by(skill_id=skill_id).count()
        
        if count > 0:
            flash(f'無法刪除：目前有 {count} 位使用者正在練習此技能！建議改為「停用」', 'warning')
        else:
            db.session.delete(skill)
            db.session.commit()
            flash('技能刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))
        
    skill = db.get_or_404(SkillInfo, skill_id)
    try:
        skill.is_active = not skill.is_active
        db.session.commit()
        flash(f'技能已{"啟用" if skill.is_active else "停用"}！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'操作失敗：{str(e)}', 'danger')

    return redirect(url_for('core.admin_skills'))

# API: 取得技能詳細資料 (for AJAX edit modal)
@core_bp.route('/skills/<skill_id>/details', methods=['GET'])
@login_required
def admin_get_skill_details(skill_id):
    """
    API: 回傳單一技能的 JSON 資料,供前端編輯視窗使用
    """
    try:
        skill = SkillInfo.query.get(skill_id)
        if not skill:
            return jsonify({'success': False, 'message': '找不到該技能'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'skill_id': skill.skill_id,
                'skill_ch_name': skill.skill_ch_name,
                'skill_en_name': skill.skill_en_name,
                'category': skill.category,
                'description': skill.description,
                'input_type': skill.input_type,
                'consecutive_correct_required': skill.consecutive_correct_required,
                'order_index': skill.order_index,
                'gemini_prompt': skill.gemini_prompt,
                'suggested_prompt_1': skill.suggested_prompt_1,
                'suggested_prompt_2': skill.suggested_prompt_2,
                'suggested_prompt_3': skill.suggested_prompt_3
            }
        })
    except Exception as e:
        current_app.logger.error(f"Get Skill Details Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# API: 重新生成技能程式碼
@core_bp.route('/skills/<skill_id>/regenerate', methods=['POST'])
@login_required
def admin_regenerate_skill_code(skill_id):
    """
    手動重新生成單一技能的 Python 程式碼 (AJAX JSON 版本)
    """
    try:
        # 延遲匯入，避免與 app.py 循環參照
        from core.code_generator import auto_generate_skill_code
        
        current_app.logger.info(f"收到重新生成請求: {skill_id}")
        
        # 呼叫生成邏輯 (同步執行，不使用 queue)
        # result 可能是 bool 或 (bool, message)
        result = auto_generate_skill_code(skill_id, queue=None)
        
        success = False
        message = ""
        
        if isinstance(result, tuple):
            success, message = result
        else:
            success = result
            message = "生成成功" if success else "生成失敗"
        
        if success:
            return jsonify({
                "success": True, 
                "message": f"技能 {skill_id} 生成成功！"
            })
        else:
            return jsonify({
                "success": False, 
                "message": f"生成失敗: {message}"
            }), 500

    except Exception as e:
        current_app.logger.error(f"Regenerate Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# API: 檢查幽靈技能檔案
@core_bp.route('/api/check_ghost_skills', methods=['GET'])
@login_required
def api_check_ghost_skills():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
        
    try:
        import os
        skills_dir = os.path.join(current_app.root_path, 'skills')
        
        if not os.path.exists(skills_dir):
            return jsonify([])
            
        # 取得所有 .py 檔案 (排除 __init__.py)
        py_files = [f[:-3] for f in os.listdir(skills_dir) 
                   if f.endswith('.py') and f != '__init__.py']
        
        # 取得資料庫中的所有 skill_id
        db_skills = [s.skill_id for s in SkillInfo.query.all()]
        
        # 找出幽靈檔案 (檔案存在但資料庫沒有)
        ghost_skills = [f for f in py_files if f not in db_skills]
        
        return jsonify(ghost_skills)
        
    except Exception as e:
        current_app.logger.error(f"Check ghost skills error: {e}")
        return jsonify({'error': str(e)}), 500

@practice_bp.route('/similar-questions-page')
@login_required
def similar_questions_page():
    return render_template('similar_questions.html')

@practice_bp.route('/generate-similar-questions', methods=['POST'])
@login_required
def generate_similar_questions():
    data = request.get_json()
    problem_text = data.get('problem_text')

    if not problem_text:
        return jsonify({"error": "Missing problem_text"}), 400

    # Import the function from the analyzer
    from .ai_analyzer import identify_skills_from_problem
    
    # Get skill IDs from the AI
    skill_ids = identify_skills_from_problem(problem_text)

    if not skill_ids:
        return jsonify({"questions": [], "message": "AI 無法從您的問題中識別出相關的數學技能，請嘗試更具體地描述您的問題。"
})

    generated_questions = []
    for skill_id in skill_ids:
        try:
            # Dynamically import the skill module
            mod = importlib.import_module(f"skills.{skill_id}")
            
            # Check if the module has a 'generate' function
            if hasattr(mod, 'generate') and callable(mod.generate):
                # Generate a question with a default level (e.g., 1)
                new_question = mod.generate(level=1)
                
                # Add skill info for context
                skill_info = get_skill_info(skill_id)
                new_question['skill_id'] = skill_id
                new_question['skill_ch_name'] = skill_info.skill_ch_name if skill_info else "未知技能"
                
                generated_questions.append(new_question)
            else:
                current_app.logger.warning(f"Skill module {skill_id} does not have a 'generate' function.")

        except ImportError:
            current_app.logger.error(f"Could not import skill module: {skill_id}")
        except Exception as e:
            current_app.logger.error(f"Error generating question for skill {skill_id}: {e}")

    return jsonify({"questions": generated_questions})


@practice_bp.route('/image-quiz-generator')
@login_required
def image_quiz_generator():
    return render_template('image_quiz_generator.html')

@practice_bp.route('/generate-quiz-from-image', methods=['POST'])
@login_required
def generate_quiz_from_image():
    if 'image_file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image_file']
    description = request.form.get('description', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        questions = generate_quiz_from_image(filepath, description) # Pass filepath instead of file object
        return jsonify({"questions": questions})
    except Exception as e:
        current_app.logger.error(f"Error in generate_quiz_from_image route: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


# 預設的建議問題，當資料庫中沒有設定時使用
DEFAULT_PROMPTS = [
    "這題的解題思路是什麼？",
    "可以給我一個相關的例子嗎？",
    "這個概念在生活中有什麼應用？"
]

@practice_bp.route('/get_suggested_prompts/<skill_id>')
@login_required
def get_suggested_prompts(skill_id):
    skill_info = db.session.get(SkillInfo, skill_id)
    prompts = []
    if skill_info:
        # 假設您的 SkillInfo 模型中有 suggested_prompt_1, suggested_prompt_2, suggested_prompt_3 欄位
        # 請根據您 Excel 中 K, L, M 欄對應的實際欄位名稱修改
        prompts = [p for p in [getattr(skill_info, 'suggested_prompt_1', None), 
                               getattr(skill_info, 'suggested_prompt_2', None), 
                               getattr(skill_info, 'suggested_prompt_3', None)] if p]
    return jsonify(prompts)

# === 班級管理功能 ===

@core_bp.route('/classes/create', methods=['POST'])
@login_required
def create_class():
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        data = request.get_json()
        class_name = data.get('name')
        
        if not class_name:
            return jsonify({"success": False, "message": "請輸入班級名稱"}), 400
            
        # class_code is now generated automatically by the model's default
        new_class = Class(
            name=class_name,
            teacher_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "班級建立成功",
            "class": new_class.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"建立班級失敗: {e}")
        return jsonify({"success": False, "message": "建立班級失敗"}), 500

@core_bp.route('/classes/regenerate_code/<int:class_id>', methods=['POST'])
@login_required
def regenerate_class_code(class_id):
    """重新產生班級代碼"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        from models import generate_invitation_code
        target_class.class_code = generate_invitation_code()
        db.session.commit()
        
        return jsonify({"success": True, "new_code": target_class.class_code})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"重新產生代碼失敗: {e}")
        return jsonify({"success": False, "message": "產生新代碼失敗"}), 500

@core_bp.route('/class/join', methods=['POST'])
@login_required
def join_class():
    """學生使用代碼加入班級"""
    if current_user.role != 'student':
        flash('只有學生才能加入班級。', 'warning')
        return redirect(url_for('core.dashboard'))

    class_code = request.form.get('class_code', '').strip()
    if not class_code:
        flash('請輸入班級代碼。', 'warning')
        return redirect(url_for('core.dashboard'))

    target_class = db.session.query(Class).filter_by(class_code=class_code).first()

    if not target_class:
        flash('無效的班級代碼。', 'danger')
        return redirect(url_for('core.dashboard'))

    # 檢查是否已在班級中
    is_member = db.session.query(ClassStudent).filter_by(class_id=target_class.id, student_id=current_user.id).first()
    if is_member:
        flash(f'您已經在「{target_class.name}」班級中了。', 'info')
        return redirect(url_for('core.dashboard'))

    # 加入班級
    try:
        new_membership = ClassStudent(class_id=target_class.id, student_id=current_user.id)
        db.session.add(new_membership)
        db.session.commit()
        flash(f'成功加入班級：「{target_class.name}」！', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"加入班級失敗: {e}")
        flash('加入班級時發生錯誤，請稍後再試。', 'danger')

    return redirect(url_for('core.dashboard'))


@core_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        # 確保只能刪除自己的班級
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限刪除"}), 404
            
        db.session.delete(target_class)
        db.session.commit()
        
        return jsonify({"success": True, "message": "班級已刪除"})
    except Exception as e:
        current_app.logger.error(f"刪除班級失敗: {e}")
        return jsonify({"success": False, "message": "刪除班級失敗"}), 500

@core_bp.route('/api/teacher/classes')
@login_required
def get_teacher_classes():
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        classes = db.session.query(Class).filter_by(teacher_id=current_user.id).order_by(Class.created_at.desc()).all()
        return jsonify({
            "success": True,
            "classes": [c.to_dict() for c in classes]
        })
    except Exception as e:
        current_app.logger.error(f"獲取班級列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取班級列表失敗"}), 500

# === 學生帳號管理路由 ===

@core_bp.route('/api/classes/<int:class_id>/students', methods=['GET'])
@login_required
def get_class_students(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        # 查詢班級學生
        students = db.session.query(User).join(ClassStudent).filter(ClassStudent.class_id == class_id).all()
        
        return jsonify({
            "success": True,
            "students": [{
                "id": s.id,
                "username": s.username,
                "role": s.role,
                "created_at": s.created_at.strftime('%Y-%m-%d')
            } for s in students]
        })

    except Exception as e:
        current_app.logger.error(f"獲取學生列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取學生列表失敗"}), 500

@core_bp.route('/api/classes/<int:class_id>/students', methods=['POST'])
@login_required
def add_student_to_class(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "請輸入帳號與密碼"}), 400

        # 檢查帳號是否已存在
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"success": False, "message": "此帳號已存在,請更換使用者名稱"}), 400

        # 建立新學生帳號
        new_student = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='student'
        )
        db.session.add(new_student)
        db.session.flush() # 取得 new_student.id

        # 將學生加入班級
        class_student = ClassStudent(
            class_id=class_id,
            student_id=new_student.id
        )
        db.session.add(class_student)
        
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "學生帳號建立成功",
            "student": {
                "id": new_student.id,
                "username": new_student.username,
                "role": new_student.role,
                "created_at": new_student.created_at.strftime('%Y-%m-%d')
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"建立學生帳號失敗: {e}")
        return jsonify({"success": False, "message": "建立學生帳號失敗"}), 500

@core_bp.route('/api/classes/<int:class_id>/students/upload', methods=['POST'])
@login_required
def upload_students_excel(class_id):
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        # 確保是該老師的班級
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        if 'file' not in request.files:
            return jsonify({"success": False, "message": "未上傳檔案"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "未選擇檔案"}), 400

        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({"success": False, "message": "請上傳 Excel 檔案 (.xlsx, .xls)"}), 400

        # 讀取 Excel，不預設標題，以便我們自己判斷
        df = pd.read_excel(file, header=None)
        
        if df.shape[1] < 2:
            return jsonify({"success": False, "message": "Excel 檔案格式錯誤：至少需要兩欄 (帳號, 密碼)"}), 400

        stats = {
            "total": 0,
            "added": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }

        # 開始處理每一列
        for index, row in df.iterrows():
            try:
                username = str(row[0]).strip()
                password = str(row[1]).strip()

                # 簡單判斷是否為標題列 (如果第一欄包含 'account' 或 'username' 或 '帳號')
                if index == 0 and any(x in username.lower() for x in ['account', 'username', '帳號']):
                    continue
                
                if not username or not password or pd.isna(row[0]) or pd.isna(row[1]):
                    continue

                stats["total"] += 1

                # 檢查帳號是否已存在
                existing_user = db.session.query(User).filter_by(username=username).first()
                
                if existing_user:
                    # 如果使用者已存在，檢查是否已在班級中
                    in_class = db.session.query(ClassStudent).filter_by(class_id=class_id, student_id=existing_user.id).first()
                    if not in_class:
                        # 加入班級
                        new_class_student = ClassStudent(class_id=class_id, student_id=existing_user.id)
                        db.session.add(new_class_student)
                        stats["added"] += 1
                    else:
                        stats["skipped"] += 1 # 已經在班級中
                else:
                    # 建立新使用者
                    new_student = User(
                        username=username,
                        password_hash=generate_password_hash(password),
                        role='student'
                    )
                    db.session.add(new_student)
                    db.session.flush() # 取得 ID

                    # 加入班級
                    new_class_student = ClassStudent(class_id=class_id, student_id=new_student.id)
                    db.session.add(new_class_student)
                    stats["added"] += 1

            except Exception as row_error:
                stats["failed"] += 1
                stats["errors"].append(f"Row {index+1}: {str(row_error)}")
                continue

        db.session.commit()
        
        message = f"處理完成。共 {stats['total']} 筆資料，新增 {stats['added']} 位學生，略過 {stats['skipped']} 位 (已存在)，失敗 {stats['failed']} 筆。"
        if stats['errors']:
            message += f" 錯誤詳情: {'; '.join(stats['errors'][:3])}..."

        return jsonify({
            "success": True, 
            "message": message,
            "stats": stats
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批次匯入學生失敗: {e}")
        return jsonify({"success": False, "message": f"匯入失敗: {str(e)}"}), 500

# === 考卷診斷與分析 API ===

# 允許的圖片格式
ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_exam_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS

@core_bp.route('/upload_exam', methods=['POST'])
@login_required
def upload_exam():
    """
    上傳考卷圖片並進行分析
    
    接收參數:
    - file: 圖片檔案
    - grade: 年級 (7, 10, 11, 12)
    - curriculum: 課程類型 ('general', 'vocational', 'junior_high')
    """
    try:
        # 1. 驗證檔案
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '沒有上傳檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '沒有選擇檔案'}), 400
        
        if not allowed_exam_file(file.filename):
            return jsonify({'success': False, 'message': '不支援的檔案格式,請上傳 jpg, png 或 gif'}), 400
        
        # 2. 取得參數
        grade = request.form.get('grade', type=int)
        curriculum = request.form.get('curriculum', 'general')
        
        if not grade:
            return jsonify({'success': False, 'message': '請選擇年級'}), 400
        
        # 3. 儲存圖片
        upload_dir = os.path.join(current_app.static_folder, 'exam_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        file.save(file_path)
        
        # 4. 分析圖片
        analysis_response = analyze_exam_image(file_path, grade, curriculum)
        
        if not analysis_response['success']:
            return jsonify({
                'success': False,
                'message': f"分析失敗: {analysis_response['error']}"
            }), 500
        
        # 5. 儲存結果
        relative_path = f"exam_uploads/{current_user.id}/{unique_filename}"
        
        save_response = save_analysis_result(
            user_id=current_user.id,
            analysis_result=analysis_response['result'],
            image_path=relative_path
        )
        
        if not save_response['success']:
            return jsonify({
                'success': False,
                'message': f"儲存結果失敗: {save_response['error']}"
            }), 500
        
        # 6. 回傳結果
        result = analysis_response['result'].get('analysis_result', {})
        
        return jsonify({
            'success': True,
            'message': '分析完成!',
            'data': {
                'exam_analysis_id': save_response['exam_analysis_id'],
                'is_correct': result.get('is_correct'),
                'matched_unit': result.get('matched_unit'),
                'error_analysis': result.get('error_analysis'),
                'image_url': url_for('static', filename=relative_path)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"上傳考卷時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'伺服器錯誤: {str(e)}'
        }), 500


@core_bp.route('/exam_history')
@login_required
def exam_history():
    """
    查詢當前使用者的考卷分析歷史記錄
    """
    try:
        analyses = db.session.query(ExamAnalysis).filter_by(
            user_id=current_user.id
        ).order_by(ExamAnalysis.created_at.desc()).all()
        
        history = [analysis.to_dict() for analysis in analyses]
        
        for item in history:
            item['image_url'] = url_for('static', filename=item['image_path'])
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        current_app.logger.error(f"查詢考卷歷史時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'查詢失敗: {str(e)}'
        }), 500


@core_bp.route('/exam_upload_page')
@login_required
def exam_upload_page():
    """
    顯示試卷上傳頁面
    """
    return render_template('exam_upload.html', username=current_user.username)

@core_bp.route('/student/diagnosis')
@login_required
def student_diagnosis():
    """
    顯示學生學習診斷頁面
    """
    return render_template('student_diagnosis.html', username=current_user.username)

@core_bp.route('/admin/init_db', methods=['POST'])
@login_required
def init_db_route():
    """執行資料庫初始化"""
    try:
        # 使用 current_app 取得 engine
        from models import init_db
        init_db(db.engine)
        flash('資料庫初始化成功！', 'success')
    except Exception as e:
        flash(f'初始化失敗: {str(e)}', 'error')
        current_app.logger.error(f"Init DB Error: {e}")
    return redirect(url_for('core.db_maintenance'))


# ==========================================
# AI Prompt 參數設定 API
# ==========================================

@core_bp.route('/admin/ai_prompt_settings')
@login_required
def ai_prompt_settings_page():
    """顯示 AI Prompt 設定頁面"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('權限不足', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('ai_prompt_settings.html', username=current_user.username)

@core_bp.route('/admin/ai_prompt_settings/get')
@login_required
def get_ai_prompt_setting():
    """取得當前的 AI Prompt 設定"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        from models import SystemSetting
        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        
        if setting:
            return jsonify({
                'success': True,
                'prompt': setting.value,
                'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S') if setting.updated_at else None
            })
        else:
            # 如果資料庫中沒有，觸發一次 get_ai_prompt 來建立預設值
            from core.ai_analyzer import get_ai_prompt
            default_prompt = get_ai_prompt()
            
            # 重新查詢（應該已經被 get_ai_prompt 寫入）
            setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
            
            return jsonify({
                'success': True,
                'prompt': setting.value if setting else default_prompt,
                'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S') if setting and setting.updated_at else None
            })
    except Exception as e:
        current_app.logger.error(f"Get AI Prompt Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/admin/ai_prompt_settings/update', methods=['POST'])
@login_required
def update_ai_prompt_setting():
    """更新 AI Prompt 設定"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        data = request.get_json()
        new_prompt = data.get('prompt', '').strip()
        
        if not new_prompt:
            return jsonify({'success': False, 'message': 'Prompt 不能為空'}), 400
        
        # 驗證必要變數
        if '{context}' not in new_prompt or '{prereq_text}' not in new_prompt:
            return jsonify({
                'success': False, 
                'message': 'Prompt 必須包含 {context} 和 {prereq_text} 變數'
            }), 400
        
        from models import SystemSetting
        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        
        if setting:
            setting.value = new_prompt
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key='ai_analyzer_prompt',
                value=new_prompt,
                description='AI 分析學生手寫答案時使用的 Prompt 模板。必須保留 {context} 和 {prereq_text} 變數。'
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '儲存成功',
            'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update AI Prompt Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/admin/ai_prompt_settings/reset', methods=['POST'])
@login_required
def reset_ai_prompt_setting():
    """恢復 AI Prompt 為預設值"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        from models import SystemSetting
        from core.ai_analyzer import DEFAULT_PROMPT
        
        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        
        if setting:
            setting.value = DEFAULT_PROMPT
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key='ai_analyzer_prompt',
                value=DEFAULT_PROMPT,
                description='AI 分析學生手寫答案時使用的 Prompt 模板。必須保留 {context} 和 {prereq_text} 變數。'
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已恢復為預設值',
            'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset AI Prompt Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# 錯題本功能 (Mistake Notebook)
# ==========================================
from models import MistakeNotebookEntry

@core_bp.route('/mistake-notebook')
@login_required
def mistake_notebook():
    """顯示錯題本主頁面"""
    return render_template('mistake_notebook.html', username=current_user.username)

@core_bp.route('/add_mistake_page')
@login_required
def add_mistake_page():
    """顯示手動新增錯題的頁面"""
    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()
    return render_template('add_mistake.html', skills=skills, username=current_user.username)

@core_bp.route('/api/mistake-notebook', methods=['GET'])
@login_required
def api_mistake_notebook():
    """獲取當前使用者的所有錯題記錄"""
    entries = db.session.query(MistakeNotebookEntry).filter_by(student_id=current_user.id).order_by(MistakeNotebookEntry.created_at.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])

@core_bp.route('/mistake-notebook/upload-image', methods=['POST'])
@login_required
def upload_mistake_image():
    """處理錯題圖片上傳"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '沒有檔案'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未選擇檔案'}), 400

    if file and allowed_exam_file(file.filename):
        # 建立專屬該使用者的資料夾
        upload_dir = os.path.join(current_app.static_folder, 'mistake_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        # 加上 UUID 避免檔名衝突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 回傳相對路徑
        relative_path = os.path.join('mistake_uploads', str(current_user.id), unique_filename).replace('\\', '/')
        return jsonify({'success': True, 'path': relative_path})
    
    return jsonify({'success': False, 'message': '檔案格式不符'}), 400

@core_bp.route('/mistake-notebook/add', methods=['POST'])
@login_required
def add_mistake_entry():
    """新增一筆錯題記錄到資料庫"""
    try:
        data = request.get_json()
        
        new_entry = MistakeNotebookEntry(
            student_id=current_user.id,
            exam_image_path=data.get('exam_image_path'),
            question_data=data.get('question_data'), # Can be JSON
            notes=data.get('notes'),
            skill_id=data.get('skill_id')
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '錯題已成功記錄！'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"新增錯題失敗: {e}")
        return jsonify({'success': False, 'message': f'伺服器錯誤: {str(e)}'}), 500


# ==========================================
# 學生學習診斷 API
# ==========================================

@core_bp.route('/student/analyze_weakness', methods=['POST'])
@login_required
def analyze_weakness():
    """
    學生學習弱點分析 API
    - 分析 MistakeLog 和 ExamAnalysis 資料
    - 使用質性分析方式推估各單元熟練度 (0-100)
    - 實作 24 小時快取機制
    """
    from core.diagnosis_analyzer import perform_weakness_analysis
    
    try:
        # 安全性：使用 current_user.id，不從前端接收 student_id
        student_id = current_user.id
        
        # 檢查是否需要強制刷新
        force_refresh = request.json.get('force_refresh', False) if request.json else False
        
        result = perform_weakness_analysis(student_id, force_refresh)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
            
    except Exception as e:
        current_app.logger.error(f"分析弱點時發生未預期錯誤: {e}")
        return jsonify({
            'success': False,
            'error': f'系統發生錯誤: {str(e)}'
        }), 500

# ==========================================
# [新增] V9 Prompt 管理 API (routes.py)
# ==========================================

@core_bp.route('/api/skills/<skill_id>/prompts', methods=['GET'])
@login_required
def api_get_skill_prompts(skill_id):
    """取得指定技能的所有 Prompt 設定"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    try:
        from models import SkillGenCodePrompt
        prompts = SkillGenCodePrompt.query.filter_by(skill_id=skill_id).order_by(SkillGenCodePrompt.model_tag).all()
        
        data = []
        for p in prompts:
            data.append({
                'id': p.id,
                'model_tag': p.model_tag,
                'system_prompt': p.system_prompt,
                'user_prompt_template': p.user_prompt_template,
                'version': p.version,
                'is_active': p.is_active,
                'updated_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else ''
            })
            
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        current_app.logger.error(f"Get Prompts Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/api/skills/<skill_id>/prompts/save', methods=['POST'])
@login_required
def api_save_skill_prompt(skill_id):
    """新增或更新 Prompt (Upsert 邏輯)"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
        
    try:
        from models import SkillGenCodePrompt
        data = request.get_json()
        model_tag = data.get('model_tag')
        
        if not model_tag:
            return jsonify({'success': False, 'message': '缺少 Model Tag'}), 400

        # Upsert Logic: 尋找既有的
        prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=model_tag).first()
        
        if prompt:
            # 更新
            prompt.user_prompt_template = data.get('user_prompt_template')
            prompt.system_prompt = data.get('system_prompt')
            prompt.is_active = data.get('is_active', True)
            prompt.version += 1 # 版本號 +1
            action = "updated"
        else:
            # 新增
            prompt = SkillGenCodePrompt(
                skill_id=skill_id,
                model_tag=model_tag,
                user_prompt_template=data.get('user_prompt_template'),
                system_prompt=data.get('system_prompt'),
                is_active=data.get('is_active', True),
                version=1,
                architect_model='admin_ui'
            )
            db.session.add(prompt)
            action = "created"
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'Prompt {action} successfully!', 'version': prompt.version})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Save Prompt Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
@login_required
def api_delete_skill_prompt(prompt_id):
    """刪除指定的 Prompt"""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
        
    try:
        from models import SkillGenCodePrompt
        prompt = db.session.get(SkillGenCodePrompt, prompt_id)
        if prompt:
            db.session.delete(prompt)
            db.session.commit()
        return jsonify({'success': True, 'message': '刪除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500