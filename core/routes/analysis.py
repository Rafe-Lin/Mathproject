# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/analysis.py
功能說明 (Description): AI 分析與診斷模組，包含 AI 聊天助手 (Chat AI)、手寫辨識分析、考卷上傳與診斷 (Exam Analysis)、錯題本與弱點分析功能。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, render_template, current_app, url_for, session
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import uuid
import traceback

from . import core_bp, practice_bp
from core.session import get_current
from core.ai_analyzer import (
    build_chat_prompt,
    get_chat_response,
    analyze,
    diagnose_error,
    diversify_follow_up_prompts,
    build_dynamic_follow_up_prompts_variant
)
from core.exam_analyzer import analyze_exam_image, save_analysis_result
from core.diagnosis_analyzer import perform_weakness_analysis
from core.rag_engine import rag_search, rag_chat
from models import db, MistakeNotebookEntry, ExamAnalysis, SkillInfo

ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_exam_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS

# ==========================================
# AI Chat & Handwriting (AI 互動)
# ==========================================

@practice_bp.route('/chat_ai', methods=['POST'])
def chat_ai():
    """AI 助教對話 API"""
    data = request.get_json()
    user_question = data.get('question', '').strip()
    context = data.get('context', '')
    question_text = data.get('question_text', '')

    if not user_question:
        return jsonify({"reply": "請輸入問題！"}), 400

    current = get_current()
    skill_id = current.get("skill")
    prereq_skills = current.get('prereq_skills', [])
    
    full_question_context = question_text if question_text else (current.get("question") or context)
    
    if not skill_id and context:
        # 簡單推測 skill_id (Fallback)
        if '餘式' in context: skill_id = 'remainder'
        elif '因式' in context: skill_id = 'factor_theorem'

    full_prompt = build_chat_prompt(
        skill_id=skill_id,
        user_question=user_question,
        full_question_context=full_question_context,
        context=context,
        prereq_skills=prereq_skills
    )

    current_app.logger.info(
        "[chat_ai] received question='%s' context_head='%s'",
        user_question[:120],
        (full_question_context or '')[:120]
    )
    
    result = get_chat_response(
        full_prompt,
        user_question=user_question,
        question_context=full_question_context
    )

    # 每輪根據學生當前提問重整紅色追問按鈕，避免固定模板重複出現
    chat_state = session.get('chat_followup_state', {}) if isinstance(session.get('chat_followup_state', {}), dict) else {}
    last_prompts = chat_state.get('last_prompts', [])
    turn_index = int(chat_state.get('turn_index', 0))
    last_context = chat_state.get('last_context', '')

    if last_context != full_question_context:
        last_prompts = []
        turn_index = 0

    # 以本輪學生提問為核心產生紅色提示詞，再做跨輪去重，確保每輪都會跟提問變化。
    per_turn_prompts = build_dynamic_follow_up_prompts_variant(
        user_question=user_question,
        question_context=full_question_context,
        ai_reply=result.get('reply', ''),
        variant=turn_index
    )
    result['follow_up_prompts'] = diversify_follow_up_prompts(
        per_turn_prompts,
        last_prompts,
        user_question=user_question,
        question_context=full_question_context,
        ai_reply=result.get('reply', ''),
        turn_index=turn_index
    )

    current_app.logger.info(
        "[chat_ai] generated follow_up_prompts=%s",
        result.get('follow_up_prompts', [])
    )

    session['chat_followup_state'] = {
        'last_prompts': result.get('follow_up_prompts', [])[:3],
        'turn_index': turn_index + 1,
        'last_question': user_question[:120],
        'last_context': full_question_context
    }

    focus_points = []
    for item in state.get('subskill_nodes', []) or []:
        label = subskill_map.get(str(item), str(item).replace('_', ' '))
        if label and label not in focus_points:
            focus_points.append(label)
    if not focus_points:
        focus_points.append('看清楚數字、符號和運算順序')
    result['subskill_labels'] = focus_points

    result['question_text'] = question_text
    result['family_id'] = family_id
    result['question_context'] = question_context or question_text

    return jsonify(result)

@practice_bp.route('/analyze_handwriting', methods=['POST'])
@login_required
def analyze_handwriting():
    """手寫數學算式辨識與分析"""
    data = request.get_json()
    img = data.get('image_data_url')
    if not img: return jsonify({"reply": "缺少圖片"}), 400
    
    state = get_current()
    api_key = current_app.config['GEMINI_API_KEY']
    prereq_skills = state.get('prereq_skills', [])
    question_text = (data.get('question_text') or state.get('question_text') or state.get('question') or "").strip()
    question_context = (data.get('question_context') or state.get('question') or "").strip()
    family_id = (data.get('family_id') or state.get('family_id') or state.get('skill') or "").strip()
    subskill_map = {
        'sign_handling': '正負號判讀',
        'add_sub': '整數加減',
        'mul_div': '整數乘除',
        'mixed_ops': '四則混合運算',
        'absolute_value': '絕對值',
        'parentheses': '括號運算',
        'divide_terms': '分項整理',
        'conjugate_rationalize': '分母有理化',
    }
    
    result = analyze(image_data_url=img, context=question_context or question_text, 
                     api_key=api_key, 
                     prerequisite_skills=prereq_skills)

    # [Start of modification] Diagnosis for handwriting
    if result.get('correct') is False:
        try:
            current_app.logger.info(f"[Handwriting Check] Incorrect answer detected, diagnosing...")
            question_text = state.get('question_text', '')
            correct_answer = state.get('correct_answer', '')
            student_answer = f"手寫答案分析: {result.get('reply', '')}"
            
            # [Phase 6] Diagnosis
            diagnosis = diagnose_error(
                question_text=question_text,
                correct_answer=correct_answer,
                student_answer=student_answer,
                prerequisite_units=prereq_skills
            )
            
            if diagnosis.get('related_prerequisite_id'):
                prereq_id = diagnosis['related_prerequisite_id']
                # Find name
                prereq_name = "基礎單元"
                if prereq_skills:
                    for p in prereq_skills:
                        # prereq_skills structure: [{'id':..., 'name':...}]
                        if str(p.get('id')) == str(prereq_id) or str(p.get('skill_id')) == str(prereq_id):
                            prereq_name = p.get('name') or p.get('skill_ch_name')
                            break
                
                result['suggested_prerequisite'] = {
                    'id': prereq_id,
                    'name': prereq_name,
                    'reason': diagnosis.get('prerequisite_explanation', '建議複習')
                }
        except Exception as e:
            current_app.logger.error(f"Handwriting diagnosis failed: {e}")
    # [End of modification]
    
    # 這裡的 update_progress 邏輯若有需要可在此處呼叫 helper
    
    return jsonify(result)



# ==========================================
# Mistake Notebook & Diagnosis (錯題本與診斷)
# ==========================================

@core_bp.route('/mistake-notebook')
@login_required
def mistake_notebook():
    return render_template('mistake_notebook.html', username=current_user.username)

@core_bp.route('/api/mistake-notebook', methods=['GET'])
@login_required
def api_mistake_notebook():
    entries = db.session.query(MistakeNotebookEntry).filter_by(student_id=current_user.id).order_by(MistakeNotebookEntry.created_at.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])

@core_bp.route('/mistake-notebook/add', methods=['POST'])
@login_required
def add_mistake_entry():
    try:
        data = request.get_json()
        db.session.add(MistakeNotebookEntry(
            student_id=current_user.id,
            exam_image_path=data.get('exam_image_path'),
            question_data=data.get('question_data'),
            notes=data.get('notes'),
            skill_id=data.get('skill_id')
        ))
        db.session.commit()
        return jsonify({'success': True, 'message': '已記錄'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/student/analyze_weakness', methods=['POST'])
@login_required
def analyze_weakness():
    """學生學習弱點分析 (Radar Chart Data)"""
    try:
        force_refresh = request.json.get('force_refresh', False) if request.json else False
        result = perform_weakness_analysis(current_user.id, force_refresh)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"弱點分析錯誤: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# [遺漏補齊] Mistake Notebook Helpers
# ==========================================

@core_bp.route('/add_mistake_page')
@login_required
def add_mistake_page():
    """顯示手動新增錯題的頁面"""
    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()
    return render_template('add_mistake.html', skills=skills, username=current_user.username)

@core_bp.route('/mistake-notebook/upload-image', methods=['POST'])
@login_required
def upload_mistake_image():
    """處理錯題圖片上傳"""
    if 'file' not in request.files: return jsonify({'success': False, 'message': '沒有檔案'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_exam_file(file.filename):
        return jsonify({'success': False, 'message': '檔案無效'}), 400

    try:
        upload_dir = os.path.join(current_app.static_folder, 'mistake_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(upload_dir, unique_filename)
        file.save(path)
        
        rel_path = os.path.join('mistake_uploads', str(current_user.id), unique_filename).replace('\\', '/')
        return jsonify({'success': True, 'path': rel_path})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Student Diagnosis (學生學習診斷頁面)
# ==========================================

@core_bp.route('/student/diagnosis')
@login_required
def student_diagnosis():
    """
    顯示學生學習診斷頁面
    """
    return render_template('student_diagnosis.html', username=current_user.username)

# ==========================================
# Naive RAG (RAG 檢索 + LLM 回答)
# ==========================================

@practice_bp.route('/api/rag_search', methods=['POST'])
def api_rag_search():
    """RAG 語意檢索 API：回傳 Top-5 最相似的國中練習技能"""
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"results": [], "error": "請輸入搜尋文字"}), 400

    # 所有結果都是系統中存在的練習技能，可直接跳轉
    results = rag_search(query, top_k=5)
    return jsonify({"results": results})


@practice_bp.route('/api/rag_chat', methods=['POST'])
def api_rag_chat():
    """RAG + LLM API：使用 Top-1 檢索結果 + Gemini 回答學生問題"""
    data = request.get_json()
    query = data.get('query', '').strip()
    top_skill_id = data.get('top_skill_id', '').strip()

    if not query or not top_skill_id:
        return jsonify({"reply": "缺少必要參數"}), 400

    result = rag_chat(query, top_skill_id)
    return jsonify(result)
