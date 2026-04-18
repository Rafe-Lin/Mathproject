# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/exam.py
功能說明 (Description): 考卷診斷與分析路由模組，負責處理考卷上傳、整合 Core Analyzer 進行分析，以及查詢歷史分析記錄。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from models import db, ExamAnalysis
from . import core_bp
from core.exam_analyzer import analyze_exam_image, save_analysis_result
import os
import uuid
import traceback

# 允許的圖片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支援的檔案格式,請上傳 jpg, png 或 gif'}), 400
        
        # 2. 取得參數
        grade = request.form.get('grade', type=int)
        curriculum = request.form.get('curriculum', 'general')
        
        if not grade:
            return jsonify({'success': False, 'message': '請選擇年級'}), 400
        
        # 3. 儲存圖片
        # 建立目錄: static/exam_uploads/{user_id}/
        upload_dir = os.path.join(current_app.static_folder, 'exam_uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 產生唯一檔名
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
        # 儲存相對路徑 (相對於 static 目錄)
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
        
        # [Phase 6] 前置單元推薦
        suggested_prerequisite = None
        if not result.get('is_correct'):
            try:
                from core.ai_analyzer import diagnose_error
                from models import SkillInfo
                
                # 取得匹配的單元 ID
                matched_unit = result.get('matched_unit', {})
                skill_id = matched_unit.get('unit_id')
                
                if skill_id:
                    # 查找單元資訊
                    skill_info = db.session.get(SkillInfo, skill_id)
                    if skill_info and skill_info.prerequisites:
                        # 收集前置單元
                        prerequisite_units = [
                            {"id": prereq.skill_id, "name": prereq.skill_ch_name}
                            for prereq in skill_info.prerequisites
                        ]
                        
                        # AI 診斷錯誤
                        error_analysis_data = result.get('error_analysis', {})
                        question_text = matched_unit.get('path_name', '考卷題目')
                        student_answer = "錯誤答案"  # 考卷分析沒有具體答案
                        correct_answer = "正確答案"
                        
                        current_app.logger.info(f"[考卷前置單元推薦] 開始診斷 - 技能: {skill_id}")
                        
                        error_diagnosis = diagnose_error(
                            question_text,
                            correct_answer,
                            student_answer,
                            prerequisite_units=prerequisite_units,
                            conversation_history=None
                        )
                        
                        current_app.logger.info(f"[考卷前置單元推薦] 診斷結果: {error_diagnosis}")
                        
                        # 如果有相關的前置單元推薦
                        if error_diagnosis.get("related_prerequisite_id"):
                            prereq_id = error_diagnosis["related_prerequisite_id"]
                            prereq_skill = db.session.get(SkillInfo, prereq_id)
                            if prereq_skill:
                                suggested_prerequisite = {
                                    "id": prereq_id,
                                    "name": prereq_skill.skill_ch_name,
                                    "reason": error_diagnosis.get("prerequisite_explanation", "建議複習此單元")
                                }
                                current_app.logger.info(f"[考卷前置單元推薦] 推薦單元: {prereq_skill.skill_ch_name}")
            except Exception as e:
                current_app.logger.error(f"考卷前置單元推薦失敗: {e}")
                import traceback
                traceback.print_exc()
        
        return jsonify({
            'success': True,
            'message': '分析完成!',
            'data': {
                'exam_analysis_id': save_response['exam_analysis_id'],
                'is_correct': result.get('is_correct'),
                'matched_unit': result.get('matched_unit'),
                'error_analysis': result.get('error_analysis'),
                'image_url': url_for('static', filename=relative_path),
                'suggested_prerequisite': suggested_prerequisite  # [Phase 6] 添加推薦
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
        # 查詢該使用者的所有分析記錄
        analyses = db.session.query(ExamAnalysis).filter_by(
            user_id=current_user.id
        ).order_by(ExamAnalysis.created_at.desc()).all()
        
        # 轉換為字典列表
        history = [analysis.to_dict() for analysis in analyses]
        
        # 加入圖片 URL
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
    顯示考卷上傳頁面
    """
    return render_template('exam_upload.html', username=current_user.username)
