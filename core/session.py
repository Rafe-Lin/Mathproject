# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/session.py
功能說明 (Description): 負責管理使用者在練習過程中的 Session 資料，提供安全存取、設定與清除當前題目、答案及相關技能資訊的介面。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""此模組負責管理使用者在練習過程中的 Session 資料，提供安全存取、設定與清除當前題目、答案及相關技能資訊的函式。"""
# core/session.py
from flask import session

def set_current(skill, data):
    """
    安全儲存當前題目資料，將所有資料整合到一個字典中
    """
    # 建立副本以確保不影響原始資料
    saved_data = data.copy()
    
    # 確保寫入 skill_id
    saved_data['skill'] = skill
    
    # 兼容性處理：舊版代碼可能預期 'question' 鍵
    if 'question_text' in saved_data:
        saved_data['question'] = saved_data['question_text']
        
    # 兼容性處理：舊版代碼可能預期 'inequality' 鍵
    if 'inequality_string' in saved_data:
        saved_data['inequality'] = saved_data['inequality_string']

    # 將整個字典存入 Session (注意：routes.py 已經先過濾掉圖片了)
    session['current_data'] = saved_data

def get_current():
    """
    安全取得當前題目資料，直接回傳整合的字典
    """
    return session.get('current_data', {})

def clear():
    """
    清除所有 current 資料
    """
    keys = ['current_skill', 'current_question', 'current_answer', 'current_prereq_skills',
            'current_inequality', 'current_correct_answer']
    for k in keys:
        session.pop(k, None)