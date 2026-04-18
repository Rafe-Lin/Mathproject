# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/exam_analyzer.py
功能說明 (Description): 考卷診斷核心模組，負責將課程綱要路徑扁平化，並整合 Gemini API 進行考卷圖片分析、錯誤分類與結果儲存。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""
考卷診斷與分析核心邏輯模組

提供以下功能:
1. 路徑扁平化: 將課程綱要轉換為扁平化的單元列表
2. Gemini API 整合: 呼叫 AI 分析考卷圖片
3. 結果儲存: 將分析結果存入資料庫
"""

import os
import json
import google.generativeai as genai
from flask import current_app
from core.ai_analyzer import get_model
from models import db, SkillInfo, SkillCurriculum, ExamAnalysis
from datetime import datetime


# 錯誤類型定義
ERROR_TYPES = {
    'CALCULATION': '計算錯誤',
    'CONCEPTUAL': '觀念錯誤',
    'LOGIC': '邏輯推演錯誤',
    'COMPREHENSION': '題意理解錯誤',
    'UNATTEMPTED': '未作答'
}


def get_flattened_unit_paths(grade=None, curriculum='general'):
    """
    從資料庫查詢課程綱要,並產生扁平化的單元路徑列表
    
    Args:
        grade: 年級 (7, 10, 11, 12),若為 None 則查詢所有年級
        curriculum: 課程類型 ('general', 'vocational', 'junior_high')
    
    Returns:
        list: 扁平化的單元列表,格式為:
              [
                  {
                      'unit_id': 'remainder',
                      'path': '普通高中/高一/數學(一)/第一章/1-2 餘式定理',
                      'skill_name': '餘式定理'
                  },
                  ...
              ]
    """
    # 建立查詢
    query = db.session.query(
        SkillCurriculum.skill_id,
        SkillCurriculum.curriculum,
        SkillCurriculum.grade,
        SkillCurriculum.volume,
        SkillCurriculum.chapter,
        SkillCurriculum.section,
        SkillInfo.skill_ch_name
    ).join(
        SkillInfo, SkillCurriculum.skill_id == SkillInfo.skill_id
    ).filter(
        SkillInfo.is_active == True
    )
    
    # 篩選條件
    if curriculum:
        query = query.filter(SkillCurriculum.curriculum == curriculum)
    if grade is not None:
        query = query.filter(SkillCurriculum.grade == grade)
    
    # 執行查詢
    results = query.order_by(
        SkillCurriculum.grade,
        SkillCurriculum.volume,
        SkillCurriculum.chapter,
        SkillCurriculum.section
    ).all()
    
    # 課程類型對應
    curriculum_map = {
        'general': '普通高中',
        'vocational': '技術型高中',
        'junior_high': '國民中學'
    }
    
    # 年級對應
    grade_map = {
        7: '國一',
        8: '國二',
        9: '國三',
        10: '高一',
        11: '高二',
        12: '高三'
    }
    
    # 產生扁平化列表
    flattened_units = []
    for row in results:
        skill_id, curr, grd, vol, chap, sec, skill_name = row
        
        # 建構路徑字串
        curr_name = curriculum_map.get(curr, curr)
        grade_name = grade_map.get(grd, f'年級{grd}')
        path = f"{curr_name}/{grade_name}/{vol}/{chap}/{sec}"
        
        flattened_units.append({
            'unit_id': skill_id,
            'path': path,
            'skill_name': skill_name
        })
    
    return flattened_units


def build_gemini_prompt(flattened_units):
    """
    建構給 Gemini 的 System Prompt
    
    Args:
        flattened_units: 扁平化的單元列表
    
    Returns:
        str: 完整的 prompt 字串
    """
    # 建構單元列表字串
    units_text = "\n".join([
        f"ID: {unit['unit_id']} | Path: {unit['path']} | Name: {unit['skill_name']}"
        for unit in flattened_units
    ])
    
    # JSON Schema
    json_schema = {
        "analysis_result": {
            "is_correct": "boolean",
            "matched_unit": {
                "unit_id": "string (必須從提供的單元列表中選擇)",
                "path_name": "string",
                "confidence": "float (0.0-1.0)"
            },
            "error_analysis": {
                "error_type": "string (CALCULATION | CONCEPTUAL | LOGIC | COMPREHENSION | UNATTEMPTED)",
                "student_answer_latex": "string (學生手寫內容的 LaTeX 格式)",
                "feedback": "string (給學生的簡短建議,限50字以內)"
            }
        }
    }
    
    prompt = f"""你是一位專業的數學教師助理,負責分析學生的手寫考卷。

【任務】
1. OCR 識別題目與學生的手寫算式
2. 判斷計算過程是否正確
3. 從提供的單元列表中,找出最符合題意的單元 ID
4. 分類錯誤類型

【可用的數學單元列表】
{units_text}

【錯誤類型定義】
- CALCULATION: 計算錯誤 (運算失誤、符號錯誤等)
- CONCEPTUAL: 觀念錯誤 (公式使用錯誤、概念混淆) - 權重最高
- LOGIC: 邏輯推演錯誤 (推理步驟錯誤)
- COMPREHENSION: 題意理解錯誤 (誤解題目要求)
- UNATTEMPTED: 未作答

【輸出格式】
請以 JSON 格式回應,結構如下:
{json.dumps(json_schema, ensure_ascii=False, indent=2)}

【注意事項】
- matched_unit.unit_id 必須從提供的單元列表中選擇
- confidence 應反映你對單元匹配的信心程度 (0.0-1.0)
- feedback 應簡短、具體、鼓勵性,限50字以內
- 如果學生答對,error_type 可以為 null
- student_answer_latex 請盡可能使用 LaTeX 格式表示數學式子
"""
    
    return prompt


def analyze_exam_image(image_path, grade, curriculum='general'):
    """
    分析考卷圖片
    
    Args:
        image_path: 圖片檔案路徑
        grade: 年級
        curriculum: 課程類型
    
    Returns:
        dict: 分析結果,包含:
              {
                  'success': bool,
                  'result': dict (如果成功),
                  'error': str (如果失敗)
              }
    """
    try:
        # 1. 獲取扁平化單元列表
        flattened_units = get_flattened_unit_paths(grade=grade, curriculum=curriculum)
        
        if not flattened_units:
            return {
                'success': False,
                'error': f'找不到年級 {grade} 的課程資料'
            }
        
        # 2. 建構 Prompt
        prompt = build_gemini_prompt(flattened_units)
        
        # 3. 讀取圖片
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'圖片檔案不存在: {image_path}'
            }
        
        model = get_model()
        # 上傳圖片
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 生成分析
        response = model.generate_content([
            prompt,
            {
                'mime_type': 'image/jpeg',
                'data': image_data
            }
        ])
        
        # 5. 解析回應
        response_text = response.text.strip()
        
        # 移除可能的 markdown 程式碼區塊標記
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # 解析 JSON
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'無法解析 AI 回應的 JSON: {e}\n原始回應: {response_text[:200]}'
            }
        
        return {
            'success': True,
            'result': analysis_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'分析過程發生錯誤: {str(e)}'
        }


from models import db, SkillInfo, SkillCurriculum, ExamAnalysis, MistakeNotebookEntry

# ... (rest of the file is the same until save_analysis_result)

def save_analysis_result(user_id, analysis_result, image_path):
    """
    將分析結果存入資料庫,並在答錯時自動記錄到錯題本
    
    Args:
        user_id: 使用者 ID
        analysis_result: 分析結果 (從 analyze_exam_image 回傳的 result)
        image_path: 圖片路徑
    
    Returns:
        dict: {
            'success': bool,
            'exam_analysis_id': int (如果成功),
            'error': str (如果失敗)
        }
    """
    try:
        # 提取資料
        result = analysis_result.get('analysis_result', {})
        matched_unit = result.get('matched_unit', {})
        error_analysis = result.get('error_analysis', {})
        
        unit_id = matched_unit.get('unit_id')
        is_correct = result.get('is_correct', False)
        
        # 查詢對應的課程資訊
        curriculum_info = db.session.query(SkillCurriculum).filter_by(
            skill_id=unit_id
        ).first()
        
        # 建立 ExamAnalysis 記錄
        exam_analysis = ExamAnalysis(
            user_id=user_id,
            skill_id=unit_id,
            curriculum=curriculum_info.curriculum if curriculum_info else None,
            grade=curriculum_info.grade if curriculum_info else None,
            volume=curriculum_info.volume if curriculum_info else None,
            chapter=curriculum_info.chapter if curriculum_info else None,
            section=curriculum_info.section if curriculum_info else None,
            is_correct=is_correct,
            error_type=error_analysis.get('error_type'),
            confidence=matched_unit.get('confidence'),
            student_answer_latex=error_analysis.get('student_answer_latex'),
            feedback=error_analysis.get('feedback'),
            image_path=image_path
        )
        db.session.add(exam_analysis)

        # 如果答錯,自動記錄到錯題本
        if not is_correct:
            # 檢查是否已存在相同的錯題記錄 (基於圖片路徑)
            existing_entry = db.session.query(MistakeNotebookEntry).filter_by(
                student_id=user_id,
                exam_image_path=image_path
            ).first()

            if not existing_entry:
                new_mistake_entry = MistakeNotebookEntry(
                    student_id=user_id,
                    exam_image_path=image_path,
                    question_data={
                        'type': 'exam_diagnosis',
                        'matched_unit': matched_unit,
                        'error_analysis': error_analysis
                    },
                    notes='考卷診斷自動記錄',
                    skill_id=unit_id
                )
                db.session.add(new_mistake_entry)
        
        db.session.commit()
        
        return {
            'success': True,
            'exam_analysis_id': exam_analysis.id
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'儲存分析結果失敗: {str(e)}'
        }

