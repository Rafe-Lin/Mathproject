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
from core.adaptive_engine import recommend_question, update_student_ability, apply_error_penalty, get_all_prerequisites
from core.ai_analyzer import diagnose_error
from config import Config

# ==========================================
# Helper Functions (輔助函式)
# ==========================================

def get_skill(skill_id):
    """動態載入技能模組 (skills/xxx.py)"""
    try:
        return importlib.import_module(f"skills.{skill_id}")
    except:
        return None


def _resolve_adaptive_unit_name(skill_id, requested_unit_name=""):
    requested = str(requested_unit_name or "").strip()
    if requested and requested != "本單元自適應學習（總結性診斷）":
        return requested
    skill_map = {
        "jh_數學1上_FourArithmeticOperationsOfIntegers": "整數四則運算",
        "jh_數學1上_FourArithmeticOperationsOfNumbers": "分數四則運算",
        "jh_數學2上_FourOperationsOfRadicals": "根式四則運算",
        "jh_數學1上_OperationsOnLinearExpressions": "一元一次式",
        "jh_數學2上_FourArithmeticOperationsOfPolynomial": "多項式四則運算",
    }
    return skill_map.get(str(skill_id or "").strip(), requested or "未指定單元")

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

@practice_bp.route('/adaptive_selection')
@login_required
def adaptive_selection_page():
    """顯示多單元自選組合的頁面。"""
    curriculum = request.args.get('curriculum', 'general')
    curriculum_map = {'general': '普通高中', 'vocational': '技術型高中', 'junior_high': '國民中學'}
    
    # 查詢該學程下的所有章節
    chapters = db.session.query(SkillCurriculum.chapter).filter_by(curriculum=curriculum).distinct().order_by(SkillCurriculum.chapter).all()
    chapter_list = [c[0] for c in chapters]

    return render_template('adaptive_selection.html', 
                           chapters=chapter_list, 
                           curriculum=curriculum,
                           curriculum_name=curriculum_map.get(curriculum, '未知'))

@practice_bp.route('/adaptive_practice')
@login_required
def adaptive_practice_page():
    """自適應練習的主頁面。"""
    mode = request.args.get('mode', 'single')
    skill_ids = request.args.get('skill_ids', '')
    curriculum = request.args.get('curriculum', '')
    
    unit_name = "自適應練習"
    if mode == 'single':
        # 在單一模式下，skill_ids 就是章節名稱
        unit_name = f"單元練習：{skill_ids}"
    elif mode == 'multiple':
        unit_name = "自選組合練習"
    elif mode == 'review':
        curriculum_map = {'general': '普高', 'vocational': '技高', 'junior_high': '國中'}
        unit_name = f"{curriculum_map.get(curriculum, '')} 總複習"

    return render_template('adaptive_practice.html', 
                           unit_name=unit_name,
                           mode=mode,
                           skill_ids=skill_ids,
                           curriculum=curriculum)


@practice_bp.route('/adaptive_summative')
@login_required
def adaptive_summative_page():
    """
    v1.1 PoC entrance for paper-aligned summative adaptive diagnosis.
    """
    skill_id = request.args.get('skill_id', '').strip()
    mode = request.args.get('mode', 'teaching').strip().lower()
    if mode not in {'assessment', 'teaching'}:
        mode = 'teaching'
    unit_name = _resolve_adaptive_unit_name(
        skill_id,
        request.args.get('unit_name', '本單元自適應學習（總結性診斷）').strip(),
    )
    return render_template(
        'adaptive_practice_v2.html',
        unit_name=unit_name,
        skill_id=skill_id,
        mode=mode,
        student_id=current_user.id,
    )


@practice_bp.route('/adaptive_learning_entry')
@login_required
def adaptive_learning_entry_page():
    """學生端「自適應評量與教學」入口頁。"""
    units = [
        {"label": "整數四則運算", "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers"},
        {"label": "分數四則運算", "skill_id": "jh_數學1上_FourArithmeticOperationsOfNumbers"},
        {"label": "根式四則運算", "skill_id": "jh_數學2上_FourOperationsOfRadicals"},
        {"label": "一元一次式", "skill_id": "jh_數學1上_OperationsOnLinearExpressions"},
        {"label": "多項式四則運算", "skill_id": "jh_數學2上_FourArithmeticOperationsOfPolynomial"},
    ]
    return render_template('adaptive_learning_entry.html', units=units)


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
    tutor_config = Config.MODEL_ROLES.get('tutor', {})
    tutor_model_name = tutor_config.get('model', 'unknown')

    return render_template('index.html', 
                           skill_id=skill_id,
                           skill_ch_name=skill_ch_name,
                           prereq_skills=prereq_skills,
                           tutor_model_name=tutor_model_name,
                           practice_mode='standard')


@practice_bp.route('/practice/similar_questions')
@login_required
def similar_questions():
    """進入類題練習模式，保留既有 index 版型與聊天/手寫互動。"""
    tutor_config = Config.MODEL_ROLES.get('tutor', {})
    tutor_model_name = tutor_config.get('model', 'unknown')

    return render_template(
        'index.html',
        skill_id='similar_questions',
        skill_ch_name='類題練習',
        prereq_skills=[],
        tutor_model_name=tutor_model_name,
        practice_mode='similar_practice',
    )

@practice_bp.route('/get_adaptive_question', methods=['GET'])
@login_required
def get_adaptive_question():
    """
    API: [Phase 4] 獲取下一道自適應推薦題目
    支援三種模式：
    - single: 單一章節練習 (需要 skill_ids 參數，為章節名稱)
    - multiple: 多章節組合練習 (需要 skill_ids 參數，為逗號分隔的章節列表)
    - review: 課程總複習 (需要 curriculum 參數)
    """
    mode = request.args.get('mode', 'single')
    
    # 根據不同模式獲取技能列表
    target_skill_ids = []
    
    # 調試信息
    current_app.logger.info(f"[Adaptive Question] Mode: {mode}")
    current_app.logger.info(f"[Adaptive Question] Request args: {request.args}")
    
    try:
        if mode == 'review':
            # 總複習模式：獲取整個課程的所有技能
            curriculum = request.args.get('curriculum')
            if not curriculum:
                return jsonify({"error": "總複習模式需要 curriculum 參數"}), 400
            
            current_app.logger.info(f"[Review Mode] Curriculum: {curriculum}")
            from models import SkillCurriculum
            skills = db.session.query(SkillCurriculum.skill_id).filter_by(
                curriculum=curriculum
            ).distinct().all()
            target_skill_ids = [s.skill_id for s in skills]
            current_app.logger.info(f"[Review Mode] Found {len(target_skill_ids)} skills")
            
        elif mode in ['single', 'multiple']:
            # 單一或多章節模式：根據章節名稱獲取技能
            skill_ids_param = request.args.get('skill_ids', '')
            if not skill_ids_param:
                return jsonify({"error": f"{mode} 模式需要 skill_ids 參數"}), 400
            
            # skill_ids 可能是單一章節名或逗號分隔的章節列表
            chapter_names = [ch.strip() for ch in skill_ids_param.split(',')]
            current_app.logger.info(f"[{mode.upper()} Mode] Chapter names: {chapter_names}")
            
            from models import SkillCurriculum
            skills = db.session.query(SkillCurriculum.skill_id).filter(
                SkillCurriculum.chapter.in_(chapter_names)
            ).distinct().all()
            target_skill_ids = [s.skill_id for s in skills]
            current_app.logger.info(f"[{mode.upper()} Mode] Found {len(target_skill_ids)} skills: {target_skill_ids[:5]}")
        
        else:
            return jsonify({"error": f"不支援的模式: {mode}"}), 400
        
        if not target_skill_ids:
            current_app.logger.error(f"[Adaptive Question] No skills found for mode={mode}")
            return jsonify({"error": "找不到符合條件的技能單元"}), 404
        
        # 呼叫推薦引擎獲取最佳題目模板
        question_template = recommend_question(current_user.id, target_skill_ids)
        if not question_template:
            return jsonify({"error": "題庫中已無合適的題目可供推薦。"}), 404
            
        # 使用 skill.generate() 動態生成具體題目
        mod = get_skill(question_template.skill_id)
        if not mod:
            return jsonify({"error": f"無法載入技能模組 {question_template.skill_id}"}), 500

        data = mod.generate(level=question_template.difficulty_level)

        # 準備 Session 資料 (與 next_question 邏輯類似)
        session_data = data.copy()
        for k in ['image', 'fig', 'figure', 'image_base64', 'visuals']:
            if k in session_data: del session_data[k]
        
        set_current(question_template.skill_id, session_data)

        # 回傳包含 mode 和 question_id 的 JSON 給前端
        return jsonify({
            "question_id": question_template.id, # 重要：回傳 DB 中的題目 ID
            "skill_id": question_template.skill_id,
            "mode": "adaptive",
            "new_question_text": data.get("question_text"),
            "correct_answer": data.get("correct_answer"),
            "context_string": data.get("context_string", ""),
            "image_base64": data.get("image_base64", ""), 
            "visual_aids": data.get("visual_aids", []),
            "answer_type": "text" # 假設自適應模式皆為文字輸入
        })
    except Exception as e:
        current_app.logger.error(f"生成自適應題目失敗: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"生成自適應題目時發生內部錯誤: {str(e)}"}), 500


@practice_bp.route('/get_next_question')
@login_required
def next_question():
    """API: 生成下一題
    
    支援 mode 參數：
    - 未帶 mode 或 mode≠unit：沿用舊行為，skill 指定單一 skill_id 出題
    - mode=unit：以單元出題，依 (curriculum, volume, chapter) 選擇 pattern skill 後出題。
      需傳 chapter，可選 volume、curriculum；缺省時 curriculum 用 session，volume 可用空字串由 selector 推斷。
    """
    mode = request.args.get('mode', '')
    skill_id = request.args.get('skill', 'remainder')
    requested_level = request.args.get('level', type=int)

    # [單元出題] mode=unit：依單元選 pattern skill
    if mode == 'unit':
        chapter = request.args.get('chapter', '').strip()
        volume = request.args.get('volume', '').strip()
        curriculum = request.args.get('curriculum') or session.get('current_curriculum', 'junior_high')
        if not chapter:
            return jsonify({"error": "單元模式需傳 chapter 參數"}), 400
        if not volume:
            vols = db.session.query(SkillCurriculum.volume).filter(
                SkillCurriculum.curriculum == curriculum,
                SkillCurriculum.chapter == chapter
            ).distinct().all()
            vols = [v[0] for v in vols if v[0]]
            if len(vols) != 1:
                return jsonify({"error": "單元模式需傳 volume 參數（該 chapter 對應多個或無 volume）"}), 400
            volume = vols[0]
        try:
            from core.unit_selector import select_pattern_skill_for_unit
            skill_id = select_pattern_skill_for_unit(curriculum, volume, chapter)
        except Exception as e:
            current_app.logger.error(f"單元 selector 失敗: {e}")
            return jsonify({"error": f"無法取得該單元的題型: {str(e)}"}), 500
        if not skill_id:
            return jsonify({"error": "該單元下無可用的題型技能"}), 404

    skill_info = get_skill_info(skill_id)
    # [單元模式] 允許 pattern skill 僅有檔案、尚無 DB 註冊時仍可出題
    if not skill_info and skill_id != 'instant_upload':
        if mode == 'unit':
            skill_info = {"input_type": "text", "skill_id": skill_id}
        else:
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

    skill_id = current['skill']
    
    # [Fix] Instant Upload Special Handling
    if skill_id == 'instant_upload':
        # Simple string comparison for instant upload
        correct_ans = str(current.get('correct_answer', '')).strip()
        user_ans_clean = user_ans.strip()
        is_correct = (user_ans_clean == correct_ans)
        
        result = {
            "correct": is_correct,
            "result": "正確！" if is_correct else f"答案錯誤。正確答案為：{correct_ans}"
        }
        return jsonify(result)

    mod = get_skill(skill_id)
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

    # --- [Phase 2 & 5] 自適應學習模式整合 ---
    is_adaptive_mode = request.json.get('mode') == 'adaptive'
    if is_adaptive_mode:
        try:
            question_id = request.json.get('question_id')
            time_taken = request.json.get('time_taken', 60.0) # 預設 60 秒
            
            if question_id:
                # 不論對錯，先更新能力（答對會加分，答錯在此階段不變）
                update_student_ability(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    question_id=question_id,
                    is_correct=is_correct,
                    time_taken_seconds=float(time_taken)
                )

                # 如果答錯，啟動錯誤分析與懲罰（僅限自適應模式）
                if not is_correct:
                    question_text = current.get('question_text', '')
                    correct_answer = current.get('correct_answer', '')
                    
                    # 收集前置單元資訊
                    from models import SkillInfo
                    skill_info = db.session.get(SkillInfo, skill_id)
                    prerequisite_units = []
                    if skill_info and skill_info.prerequisites:
                        prerequisite_units = [
                            {"id": prereq.skill_id, "name": prereq.skill_ch_name}
                            for prereq in skill_info.prerequisites
                        ]
                    
                    # 收集對話歷史（如果有的話）
                    conversation_history = session.get('conversation_history', [])
                    
                    # 呼叫增強版 AI 診斷
                    error_diagnosis = diagnose_error(
                        question_text, 
                        correct_answer, 
                        user_ans,
                        prerequisite_units=prerequisite_units,
                        conversation_history=conversation_history
                    )
                    
                    error_type = error_diagnosis.get("error_type", "unknown")
                    
                    # 應用懲罰（僅自適應模式）
                    if error_type != "unknown":
                        apply_error_penalty(
                            user_id=current_user.id,
                            skill_id=skill_id,
                            question_id=question_id,
                            error_type=error_type
                        )
                    
                    # [Phase 6] 如果有相關的前置單元推薦，加入回應中
                    if error_diagnosis.get("related_prerequisite_id"):
                        prereq_id = error_diagnosis["related_prerequisite_id"]
                        prereq_skill = db.session.get(SkillInfo, prereq_id)
                        if prereq_skill:
                            result["suggested_prerequisite"] = {
                                "id": prereq_id,
                                "name": prereq_skill.skill_ch_name,
                                "reason": error_diagnosis.get("prerequisite_explanation", "建議複習此單元")
                            }

        except Exception as e:
            current_app.logger.error(f"自適應引擎處理失敗: {e}")
    
    # [Phase 6] 普通模式的錯誤診斷與前置單元推薦
    if not is_adaptive_mode and not is_correct:
        try:
            question_text = current.get('question_text', '')
            correct_answer = current.get('correct_answer', '')
            
            current_app.logger.info(f"[前置單元推薦] 開始診斷 - 技能: {skill_id}")
            
            # 收集前置單元資訊
            from models import SkillInfo
            skill_info = db.session.get(SkillInfo, skill_id)
            prerequisite_units = []
            if skill_info and skill_info.prerequisites:
                prerequisite_units = [
                    {"id": prereq.skill_id, "name": prereq.skill_ch_name}
                    for prereq in skill_info.prerequisites
                ]
            
            current_app.logger.info(f"[前置單元推薦] 找到 {len(prerequisite_units)} 個前置單元")
            
            # 只有當有前置單元時才進行診斷（節省 API 成本）
            if prerequisite_units:
                # 收集對話歷史
                conversation_history = session.get('conversation_history', [])
                
                current_app.logger.info(f"[前置單元推薦] 呼叫 AI 診斷...")
                
                # 呼叫 AI 診斷
                error_diagnosis = diagnose_error(
                    question_text, 
                    correct_answer, 
                    user_ans,
                    prerequisite_units=prerequisite_units,
                    conversation_history=conversation_history
                )
                
                current_app.logger.info(f"[前置單元推薦] AI 診斷結果: {error_diagnosis}")
                
                # 如果有相關的前置單元推薦，加入回應中
                if error_diagnosis.get("related_prerequisite_id"):
                    prereq_id = error_diagnosis["related_prerequisite_id"]
                    prereq_skill = db.session.get(SkillInfo, prereq_id)
                    if prereq_skill:
                        result["suggested_prerequisite"] = {
                            "id": prereq_id,
                            "name": prereq_skill.skill_ch_name,
                            "reason": error_diagnosis.get("prerequisite_explanation", "建議複習此單元")
                        }
                        current_app.logger.info(f"[前置單元推薦] 推薦單元: {prereq_skill.skill_ch_name}")
                    else:
                        current_app.logger.warning(f"[前置單元推薦] 找不到前置單元: {prereq_id}")
                else:
                    current_app.logger.info(f"[前置單元推薦] AI 判斷與前置單元無關")
            else:
                current_app.logger.info(f"[前置單元推薦] 此技能無前置單元，跳過診斷")
        except Exception as e:
            current_app.logger.error(f"前置單元推薦失敗: {e}")
            import traceback
            traceback.print_exc()
    
    # 更新一般進度
    update_progress(current_user.id, skill_id, is_correct)

    # 若答錯，自動記錄到錯題本
    if not is_correct:
        try:
            q_text = current.get('question_text')
            existing_entry = db.session.query(MistakeNotebookEntry).filter_by(
                student_id=current_user.id,
                skill_id=skill_id
            ).filter(MistakeNotebookEntry.question_data.contains(q_text)).first()

            if not existing_entry and q_text:
                new_entry = MistakeNotebookEntry(
                    student_id=current_user.id,
                    skill_id=skill_id,
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
