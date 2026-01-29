# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/practice.py
功能說明 (Description): 學生練習區核心路由模組，處理題目生成 (Generator)、答案批改 (Checker) 與 Matplotlib 繪圖輔助，並管理練習 Session。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import Blueprint, request, jsonify, current_app, render_template, session, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import importlib
import sys # [修正 2] 導入 sys 以便檢查模組狀態
import numpy as np
import matplotlib
# [CRITICAL] 設定 Matplotlib 為非互動模式，避免 Server 端 GUI 錯誤
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import re
import uuid
import os
from datetime import datetime

# 引用 Blueprint
from . import practice_bp

# 資料庫模型
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum, Progress, MistakeNotebookEntry
from core.utils import get_skill_info
from core.session import get_current, set_current

# ==========================================
# Helper Functions (輔助函式)
# ==========================================

def get_skill(skill_id):
    """動態載入技能模組 (skills/xxx.py)"""
    try:
        return importlib.import_module(f"skills.{skill_id}")
    except:
        return None

def update_progress(user_id, skill_id, is_correct):
    """
    更新用戶進度 (Progress)
    V2.0 更新：不再動態調整等級，僅記錄連續答對/錯次數與練習時間
    """
    progress = db.session.query(Progress).filter_by(user_id=user_id, skill_id=skill_id).first()
    now_time = datetime.now()

    if not progress:
        progress = Progress(
            user_id=user_id,
            skill_id=skill_id,
            consecutive_correct=1 if is_correct else 0,
            consecutive_wrong=0 if is_correct else 1,
            questions_solved=1,
            current_level=1,
            last_practiced=now_time
        )
        db.session.add(progress)
    else:
        progress.questions_solved += 1
        progress.last_practiced = now_time
        if is_correct:
            progress.consecutive_correct += 1
            progress.consecutive_wrong = 0
        else:
            progress.consecutive_correct = 0
            progress.consecutive_wrong += 1
    
    db.session.commit()

# ==========================================
# Routes (路由)
# ==========================================

@practice_bp.route('/practice/<skill_id>')
def practice(skill_id):
    """進入特定技能的練習頁面"""
    skill_info = db.session.get(SkillInfo, skill_id)
    skill_ch_name = skill_info.skill_ch_name if skill_info else "未知技能"

    # 查詢前置技能
    prerequisites = db.session.query(SkillInfo).join(
        SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
    ).filter(
        SkillPrerequisites.skill_id == skill_id,
        SkillInfo.is_active.is_(True)
    ).order_by(SkillInfo.skill_ch_name).all()

    prereq_skills = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in prerequisites]

    return render_template('index.html', 
                           skill_id=skill_id,
                           skill_ch_name=skill_ch_name,
                           prereq_skills=prereq_skills)

@practice_bp.route('/get_next_question')
@login_required  # [修正 1] 強制檢查登入，解決 AnonymousUserMixin 報錯
def next_question():
    """API: 生成下一題"""
    skill_id = request.args.get('skill', 'remainder')
    requested_level = request.args.get('level', type=int) 
    
    skill_info = get_skill_info(skill_id)
    if not skill_info and skill_id != 'instant_upload':
        return jsonify({"error": f"技能 {skill_id} 不存在或未啟用"}), 404
        
    # [Feature] Instant Practice Mode (Short Loop)
    if skill_id == 'instant_upload':
        current = get_current()
        if not current or 'is_instant_upload' not in current:
             return jsonify({"error": "No instant upload session found"}), 404
        
        # Return either base64 or URL path. Frontend handles both in the 'image_base64' field logic (simplification)
        # or we add a specific field. Let's use image_base64 field as a generic image source carrier for now or add image_url.
        img_src = current.get("image_path") if current.get("image_path") else current.get("image_base64", "")
        
        return jsonify({
            "new_question_text": current.get("question_text", ""), 
            "context_string": "",
            "inequality_string": "",
            "consecutive_correct": 0, 
            "current_level": 1, 
            "image_base64": img_src, # Now carries URL or Base64
            "visual_aids": [],
            "answer_type": "text",
            "is_instant_upload": True 
        })
    
    try:
        # [修正 2] 強制重新載入模組，解決「改了沒反應」的問題
        module_path = f"skills.{skill_id}"
        if module_path in sys.modules:
            mod = importlib.reload(sys.modules[module_path])
        else:
            mod = importlib.import_module(module_path)
        
        # 決定難度等級
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

        # 準備前置技能資訊供 AI 使用
        prereq_query = db.session.query(SkillInfo).join(
            SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
        ).filter(
            SkillPrerequisites.skill_id == skill_id,
            SkillInfo.is_active.is_(True)
        ).order_by(SkillInfo.skill_ch_name).all()
        
        prereq_info_for_ai = [{'id': p.skill_id, 'name': p.skill_ch_name} for p in prereq_query]

        # [Safety] 自動重試機制 (解決偶發的 AI 生成錯誤)
        max_retries = 5
        data = None
        
        for attempt in range(max_retries):
            try:
                # [修正 3] 強化自動修復與欄位檢查
                data = mod.generate(level=difficulty_level)
                
                # [核心修正] 欄位雙重自動校正 (對齊金標準)
                if "question" in data and "question_text" not in data:
                    data["question_text"] = data["question"]
                if "answer" in data and "correct_answer" not in data:
                    data["correct_answer"] = data["answer"] # 確保批改時找得到答案

                if data and "question_text" in data and "correct_answer" in data:
                    break
            except Exception as e:
                current_app.logger.warning(f"題目生成重試 ({attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1: raise e
        
        # 準備 Session 資料
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        data['prereq_skills'] = prereq_info_for_ai
        
        # [核心防禦] 清理 Session，確保所有存入內容皆可 JSON 序列化
        session_data = data.copy()
        # 務必包含 'image' 與 'Figure' 相關鍵值
        for k in ['image', 'fig', 'figure', 'image_base64', 'visuals']:
            if k in session_data: del session_data[k]
        
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
        return jsonify({"error": f"生成題目失敗: {str(e)}"}), 500

@practice_bp.route('/check_answer', methods=['POST'])
def check_answer():
    """API: 檢查答案"""
    user_ans = request.json.get('answer', '').strip()
    current = get_current()

    # 安全檢查：Session 遺失
    if not current or 'skill' not in current:
        return jsonify({
            "correct": False,
            "result": "連線逾時或伺服器已重啟，請重新整理頁面。",
            "state_lost": True
        }), 400

    skill = current['skill']
    mod = get_skill(skill)
    if not mod:
        return jsonify({"correct": False, "result": "模組載入錯誤"})

    # 特殊處理：圖形題
    if current.get('correct_answer') == "graph":
        return jsonify({
            "correct": False,
            "result": "請畫完可行域後，點「AI 檢查」",
            "next_question": False
        })

    # 執行批改
    result = mod.check(user_ans, current['answer'])
    
    # [V10.1 Repair] 強制轉型：若模組回傳 bool，自動封裝為 dict
    if isinstance(result, bool):
        result = {
            "correct": result,
            "result": "Correct!" if result else "Incorrect."
        }
        
    is_correct = result.get('correct', False)

    # 更新進度
    update_progress(current_user.id, skill, is_correct)

    # 若答錯，自動記錄到錯題本
    if not is_correct:
        try:
            q_text = current.get('question_text')
            existing_entry = db.session.query(MistakeNotebookEntry).filter_by(
                student_id=current_user.id,
                skill_id=skill
            ).filter(MistakeNotebookEntry.question_data.contains(q_text)).first()

            if not existing_entry and q_text:
                new_entry = MistakeNotebookEntry(
                    student_id=current_user.id,
                    skill_id=skill,
                    question_data={'type': 'system_question', 'text': q_text},
                    notes='系統練習題自動記錄'
                )
                db.session.add(new_entry)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"自動記錄錯題失敗: {e}")
            db.session.rollback()
    
    return jsonify(result)

@practice_bp.route('/draw_diagram', methods=['POST'])
def draw_diagram():
    """
    API: AI 輔助繪圖功能
    機制：使用 Thread-Safe 的 Figure 物件模式，避免多執行緒繪圖衝突
    """
    try:
        import google.generativeai as genai
        data = request.get_json()
        question_text = data.get('question_text')

        if not question_text:
            return jsonify({"success": False, "message": "無題目文字"}), 400

        # 1. 呼叫 Gemini 提取方程式
        api_key = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(current_app.config.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash'))
        
        prompt = f"""
        從以下數學題目中提取出所有可以用來繪製2D圖形的方程式或不等式。
        - 請只回傳方程式/不等式，每個一行。
        - 將 '^' 轉換為 '**'。
        - 如果找不到，回傳 "No equation found"。
        題目：{question_text}
        """
        
        response = model.generate_content(prompt)
        equations_text = response.text.strip()

        if "No equation found" in equations_text or not equations_text:
            return jsonify({"success": False, "message": "AI 無法識別可繪製的方程式。"}), 400

        # 2. 開始繪圖 (Thread-Safe Pattern)
        # 關鍵：明確建立 figure 物件，而不使用全域 plt
        fig = plt.figure(figsize=(6, 6))
        
        x = np.linspace(-10, 10, 400)
        y = np.linspace(-10, 10, 400)
        x, y = np.meshgrid(x, y)

        eval_context = {
            'np': np, 'x': x, 'y': y,
            'a': 2, 'b': 3, 'c': 4 # 預設參數避免報錯
        }

        has_plot = False
        for line in equations_text.splitlines():
            line = line.strip()
            if not line: continue
            
            # 簡易清理
            line = line.strip('$').replace('sqrt', 'np.sqrt').replace('^', '**')
            
            try:
                # 等式處理
                if '=' in line and '==' not in line and '>' not in line and '<' not in line:
                    parts = line.split('=')
                    expr = f"({parts[0].strip()}) - ({parts[1].strip()})"
                    plt.contour(x, y, eval(expr, eval_context), levels=[0], colors='b')
                    has_plot = True
                # 不等式處理
                elif '>' in line or '<' in line:
                    plt.contourf(x, y, eval(line, eval_context), levels=[0, np.inf], colors=['#3498db'], alpha=0.3)
                    has_plot = True
            except Exception as e:
                continue
        
        if not has_plot:
            plt.close(fig) # 釋放資源
            return jsonify({"success": False, "message": "無法繪製任何有效圖形。"}), 400

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.gca().set_aspect('equal')

        # 3. 儲存圖片
        static_dir = os.path.join(current_app.static_folder)
        if not os.path.exists(static_dir): os.makedirs(static_dir)
            
        unique_filename = f"diagram_{uuid.uuid4().hex}.svg"
        image_path = os.path.join(static_dir, unique_filename)
        
        plt.savefig(image_path, format='svg')
        plt.close(fig) # [CRITICAL] 務必關閉 figure 以釋放記憶體

        return jsonify({
            "success": True,
            "image_path": url_for('static', filename=unique_filename)
        })

    except Exception as e:
        plt.close('all') # 發生錯誤時的保險機制
        current_app.logger.error(f"繪圖錯誤: {e}")
        return jsonify({"success": False, "message": f"伺服器錯誤: {e}"}), 500

# ==========================================
# [遺漏補齊] Advanced Practice Features (進階練習功能)
# ==========================================

@practice_bp.route('/similar-questions-page')
@login_required
def similar_questions_page():
    return render_template('similar_questions.html')

@practice_bp.route('/generate-similar-questions', methods=['POST'])
@login_required
def generate_similar_questions():
    data = request.get_json()
    problem_text = data.get('problem_text')
    if not problem_text: return jsonify({"error": "Missing problem_text"}), 400

    from core.ai_analyzer import identify_skills_from_problem
    skill_ids = identify_skills_from_problem(problem_text)

    if not skill_ids:
        return jsonify({"questions": [], "message": "AI 無法識別相關技能。"})

    generated_questions = []
    for skill_id in skill_ids:
        try:
            mod = importlib.import_module(f"skills.{skill_id}")
            if hasattr(mod, 'generate'):
                new_question = mod.generate(level=1)
                skill_info = get_skill_info(skill_id)
                new_question['skill_id'] = skill_id
                new_question['skill_ch_name'] = skill_info.skill_ch_name if skill_info else "未知"
                generated_questions.append(new_question)
        except: pass

    return jsonify({"questions": generated_questions})

@practice_bp.route('/image-quiz-generator')
@login_required
def image_quiz_generator():
    return render_template('image_quiz_generator.html')

@practice_bp.route('/generate-quiz-from-image', methods=['POST'])
@login_required
def generate_quiz_from_image():
    if 'image_file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['image_file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    try:
        from core.ai_analyzer import generate_quiz_from_image as ai_gen_quiz
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        description = request.form.get('description', '')
        questions = ai_gen_quiz(filepath, description)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@practice_bp.route('/get_suggested_prompts/<skill_id>')
@login_required
def get_suggested_prompts(skill_id):
    """取得技能的建議提問 (Suggested Prompts)"""
    skill_info = db.session.get(SkillInfo, skill_id)
    prompts = []
    if skill_info:
        prompts = [p for p in [skill_info.suggested_prompt_1, skill_info.suggested_prompt_2, skill_info.suggested_prompt_3] if p]
    return jsonify(prompts)


@practice_bp.route('/practice/upload_instant', methods=['POST'])
@login_required # Login required for now, or could be open?
def upload_instant():
    """
    Handle instant image upload for immediate practice (Short Loop).
    Stores result in session, does NOT save to DB.
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    try:
        from core.ai_analyzer import analyze_question_image
        
        # 1. Save temp file (optional, or pass stream directly if supported)
        # static/temp_uploads structure
        upload_dir = os.path.join(current_app.static_folder, 'temp_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(f"instant_{uuid.uuid4().hex}.png") # Force png or keep extension
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 2. Analyze with AI
        # Re-open file to read for AI
        with open(filepath, 'rb') as f_img:
             # Mock a FileStorage object structure or adjust analyze_question_image to take path/bytes
             # actually analyze_question_image takes a FileStorage object usually.
             # Let's adjust usage to pass the file object or just re-create a mock
             from werkzeug.datastructures import FileStorage
             f_mock = FileStorage(stream=f_img, filename=filename)
             result = analyze_question_image(f_mock)
             
        if "error" in result:
             return jsonify({'success': False, 'message': result['error']}), 500
             
        # 3. Store in Session
        session_data = {
            'skill': 'instant_upload',
            'question_text': result.get('question_text', ''),
            'correct_answer': result.get('correct_answer', ''),
            'predicted_topic': result.get('predicted_topic', 'Unclassified'),
            'image_base64': result.get('image_base64', ''), # If AI returns b64, or constructed below
            'image_path': url_for('static', filename=f'temp_uploads/{filename}'), # Use path for display
            'is_instant_upload': True
        }
        
        # If AI didn't return base64 (likely), we use the path url for frontend display
        # But for 'image_base64' field in next_question response, we might want it? 
        # Actually frontend can handle URL. Let's use image_path mainly.
        
        # CRITICAL: set_current for session management
        set_current('instant_upload', session_data)
        
        return jsonify({'success': True, 'redirect_url': url_for('practice.practice', skill_id='instant_upload')})

    except Exception as e:
        current_app.logger.error(f"Instant upload failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500