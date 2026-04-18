# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/diagnosis_analyzer.py
功能說明 (Description): 學生學習弱點分析模組，綜合錯題記錄 (MistakeLog) 與考卷分析 (ExamAnalysis)，生成雷達圖數據與 AI 評語。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# core/diagnosis_analyzer.py

from models import db, MistakeLog, ExamAnalysis, LearningDiagnosis, SkillInfo
from datetime import datetime, timedelta
from core.ai_analyzer import analyze_student_weakness
import json
from flask import current_app

def perform_weakness_analysis(student_id, force_refresh=False):
    """
    執行學生學習弱點分析
    
    Args:
        student_id: 學生 ID
        force_refresh: 是否強制重新分析 (忽略快取)
        
    Returns:
        dict: 分析結果，包含 'success', 'cached', 'data', 或 'error'
    """
    
    current_app.logger.info(f"[WeaknessAnalysis] Start analysis for student_id: {student_id}")

    # 1. 快取檢查：24 小時內有記錄且未要求強制刷新
    if not force_refresh:
        cached_diagnosis = LearningDiagnosis.query.filter_by(student_id=student_id).order_by(
            LearningDiagnosis.created_at.desc()
        ).first()
        
        if cached_diagnosis:
            time_diff = datetime.utcnow() - cached_diagnosis.created_at
            if time_diff < timedelta(hours=24):
                current_app.logger.info("[WeaknessAnalysis] Using cached diagnosis")
                return {
                    'success': True,
                    'cached': True,
                    'data': cached_diagnosis.to_dict()
                }
    
    # 2. 收集資料
    mistake_logs = MistakeLog.query.filter_by(user_id=student_id).all()
    
    # 查詢最近 20 筆考卷分析與錯題記錄
    exam_analyses = ExamAnalysis.query.filter_by(user_id=student_id).order_by(
        ExamAnalysis.created_at.desc()
    ).limit(20).all()
    
    current_app.logger.info(f"[WeaknessAnalysis] Mistake logs found: {len(mistake_logs)}")
    current_app.logger.info(f"[WeaknessAnalysis] Exam analyses found: {len(exam_analyses)}")
    
    # 3. 統計各技能的錯誤情況
    skill_error_stats = {}
    
    # 分析 MistakeLog
    for log in mistake_logs:
        skill_id = log.skill_id
        if skill_id not in skill_error_stats:
            skill_info = SkillInfo.query.get(skill_id)
            skill_error_stats[skill_id] = {
                'skill_name': skill_info.skill_ch_name if skill_info else skill_id,
                'concept_errors': 0,
                'calculation_errors': 0,
                'other_errors': 0,
                'total_errors': 0
            }
        
        skill_error_stats[skill_id]['total_errors'] += 1
        
        # 分類錯誤類型
        error_type = log.error_type or 'other'
        if 'concept' in error_type.lower() or '概念' in error_type:
            skill_error_stats[skill_id]['concept_errors'] += 1
        elif 'calculation' in error_type.lower() or '計算' in error_type:
            skill_error_stats[skill_id]['calculation_errors'] += 1
        else:
            skill_error_stats[skill_id]['other_errors'] += 1
    
    # 分析 ExamAnalysis (統計錯誤並補充信心度和評語資訊)
    exam_feedback = {}
    exam_details_list = [] # 儲存詳細考卷記錄供 AI 參考

    for exam in exam_analyses:
        skill_id = exam.skill_id
        
        # [修正] 確保即使只有考卷記錄也能被統計到
        if skill_id not in skill_error_stats:
            skill_info = SkillInfo.query.get(skill_id)
            skill_error_stats[skill_id] = {
                'skill_name': skill_info.skill_ch_name if skill_info else skill_id,
                'concept_errors': 0,
                'calculation_errors': 0,
                'other_errors': 0,
                'total_errors': 0
            }

        skill_name = skill_error_stats[skill_id]['skill_name']

        # [修正] 統計考卷中的錯誤
        if not exam.is_correct:
            skill_error_stats[skill_id]['total_errors'] += 1
            error_type = str(exam.error_type).upper() if exam.error_type else 'OTHER'
            
            if 'CONCEPT' in error_type: # CONFCEPTUAL or 觀念
                skill_error_stats[skill_id]['concept_errors'] += 1
            elif 'CALCULATION' in error_type: # CALCULATION or 計算
                skill_error_stats[skill_id]['calculation_errors'] += 1
            else:
                skill_error_stats[skill_id]['other_errors'] += 1

        if skill_id not in exam_feedback:
            exam_feedback[skill_id] = {
                'confidence_scores': [],
                'feedbacks': []
            }
        
        if exam.confidence is not None:
            exam_feedback[skill_id]['confidence_scores'].append(exam.confidence)
        if exam.feedback:
            exam_feedback[skill_id]['feedbacks'].append(exam.feedback)
            
        # [新增] 記錄詳細考卷結果
        is_correct_str = "正確" if exam.is_correct else "錯誤"
        detail_str = f"- [考卷診斷] 單元: {skill_name}, 結果: {is_correct_str}, 錯誤類型: {exam.error_type}, 評語: {exam.feedback or '無'}"
        exam_details_list.append(detail_str)
    
    # 4. 驗證資料量
    current_app.logger.info(f"[WeaknessAnalysis] Generated stats for skills: {list(skill_error_stats.keys())}")
    
    if not skill_error_stats:
        current_app.logger.warning("[WeaknessAnalysis] Insufficient data: skill_error_stats is empty")
        return {
            'success': False,
            'error': '尚無足夠的學習記錄進行分析'
        }
    
    # 5. 建立 AI Prompt
    prompt_data = "以下是學生的錯題統計資料：\n\n"
    
    for skill_id, stats in skill_error_stats.items():
        skill_name = stats['skill_name']
        prompt_data += f"【{skill_name}】\n"
        prompt_data += f"  - 總錯誤次數: {stats['total_errors']}\n"
        prompt_data += f"  - 概念錯誤: {stats['concept_errors']} 次\n"
        prompt_data += f"  - 計算錯誤: {stats['calculation_errors']} 次\n"
        prompt_data += f"  - 其他錯誤: {stats['other_errors']} 次\n"
        
        # 補充考卷診斷資訊
        if skill_id in exam_feedback:
            avg_confidence = sum(exam_feedback[skill_id]['confidence_scores']) / len(exam_feedback[skill_id]['confidence_scores']) if exam_feedback[skill_id]['confidence_scores'] else None
            if avg_confidence:
                prompt_data += f"  - 平均信心度: {avg_confidence:.2f}\n"
            if exam_feedback[skill_id]['feedbacks']:
                prompt_data += f"  - AI 評語摘要: {'; '.join(exam_feedback[skill_id]['feedbacks'][:2])}\n"
        
        
        prompt_data += "\n"
    
    # [新增] 補充詳細考卷記錄
    if exam_details_list:
        prompt_data += "\n【最近考卷分析記錄】(請重點參考)\n"
        prompt_data += "\n".join(exam_details_list)
        prompt_data += "\n"

    # 6. 呼叫 AI Analyzer
    try:
        ai_result = analyze_student_weakness(prompt_data)
        
        # 7. 儲存分析結果到資料庫
        new_diagnosis = LearningDiagnosis(
            student_id=student_id,
            radar_chart_data=json.dumps(ai_result.get('mastery_scores', {}), ensure_ascii=False),
            ai_comment=ai_result.get('overall_comment', ''),
            recommended_unit=ai_result.get('recommended_unit', '')
        )
        
        db.session.add(new_diagnosis)
        db.session.commit()
        
        return {
            'success': True,
            'cached': False,
            'data': new_diagnosis.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'分析過程發生錯誤: {str(e)}'
        }
