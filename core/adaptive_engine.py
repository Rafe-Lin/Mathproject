# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): adaptive_engine.py
功能說明 (Description): 實現自適應學習的核心演算法，包括能力更新與題目推薦。
=============================================================================
"""
import random
from sqlalchemy import desc, or_
from . import adaptive_config as config
from models import db, StudentAbility, TextbookExample, QuizAttempt, SkillInfo, SkillPrerequisites

def get_all_prerequisites(initial_skill_ids: list) -> set:
    """
    遞迴獲取給定技能列表的所有前置技能。

    Args:
        initial_skill_ids (list): 初始的技能 ID 列表。

    Returns:
        set: 包含所有初始技能及其所有層級前置技能的集合。
    """
    all_skills = set(initial_skill_ids)
    skills_to_check = list(initial_skill_ids)
    
    while skills_to_check:
        current_skill_id = skills_to_check.pop()
        
        prereqs = db.session.query(SkillPrerequisites.prerequisite_id).filter_by(skill_id=current_skill_id).all()
        
        for prereq in prereqs:
            prereq_id = prereq.prerequisite_id
            if prereq_id not in all_skills:
                all_skills.add(prereq_id)
                skills_to_check.append(prereq_id)
                
    return all_skills

def recommend_question(user_id, skill_ids: list):
    """
    [V2] 根據學生當前能力和指定的技能範圍，推薦最合適的下一道題目。

    Args:
        user_id (int): 學生 ID。
        skill_ids (list): 指定的技能 ID 範圍。

    Returns:
        TextbookExample: 推薦的題目物件，若無則返回 None。
    """
    # 1. 獲取學生在指定技能範圍內的所有能力記錄，存入字典以便快速查找
    abilities_query = StudentAbility.query.filter(
        StudentAbility.user_id == user_id,
        StudentAbility.skill_id.in_(skill_ids)
    ).all()
    abilities = {ability.skill_id: ability for ability in abilities_query}

    # 2. 獲取學生最近做過的 N 道題，以避免重複
    recent_question_ids = [
        attempt.question_id for attempt in
        QuizAttempt.query.filter_by(user_id=user_id)
                     .order_by(desc(QuizAttempt.timestamp))
                     .limit(config.RS_NON_REPEAT_HISTORY_COUNT)
                     .all()
    ]

    # 3. 獲取所有候選題目
    candidate_questions = TextbookExample.query.filter(TextbookExample.skill_id.in_(skill_ids)).all()
    if not candidate_questions:
        return None

    best_question = None
    max_rs_score = -1

    # 4. 遍歷所有候選題目，計算 RS 分數
    for question in candidate_questions:
        # 規則 2: 變化性 (最近做過的題目不推薦)
        if question.id in recent_question_ids:
            continue

        # 獲取當前題目對應的能力值，如果沒有則使用預設值
        ability = abilities.get(question.skill_id)
        if not ability:
            # 建立一個臨時的預設能力物件用於計算，但不存入資料庫
            ability = StudentAbility(ability_a=config.ABILITY_DEFAULT, concept_u=config.CONCEPT_DEFAULT, calculation_c=config.CALCULATION_DEFAULT)

        # 規則 1: 難度適中性
        diff = abs(ability.ability_a - question.difficulty_h)
        score_level = max(0, 1 - (diff / config.ABILITY_MAX))
        if diff <= config.RS_LEVEL_RANGE:
            score_level *= 1.5

        # 規則 3 & 4: 觀念與計算強化 (能力越弱，分數越高)
        score_concept = 1 - (ability.concept_u / config.CONCEPT_MAX)
        score_calculation = 1 - (ability.calculation_c / config.CALCULATION_MAX)

        # 規則 5: 知識點重要性
        score_importance = question.skill_info.importance if question.skill_info else 1.0

        # 計算總分 RS
        rs_score = (
            config.W_LEVEL * score_level +
            config.W_NON_REPEAT * 1.0 + # 只要沒做過就是 1.0
            config.W_CONCEPT * score_concept +
            config.W_CALCULATION * score_calculation +
            config.W_IMPORTANCE * score_importance
        )

        if rs_score > max_rs_score:
            max_rs_score = rs_score
            best_question = question

    # 如果所有題目都做過了或沒有計算出分數，隨機選一題
    if not best_question and candidate_questions:
        # 過濾掉做過的題目
        unseen_questions = [q for q in candidate_questions if q.id not in recent_question_ids]
        if unseen_questions:
            best_question = random.choice(unseen_questions)
        else: # 如果所有題目真的都做完了
            best_question = random.choice(candidate_questions)
        
    return best_question

def apply_error_penalty(user_id, skill_id, question_id, error_type):
    """
    [Phase 5] 根據 AI 診斷的錯誤類型，對學生的能力值進行精準扣分。
    """
    ability = StudentAbility.query.filter_by(user_id=user_id, skill_id=skill_id).first()
    if not ability: return

    question = db.session.get(TextbookExample, question_id)
    if not question: return

    H = question.difficulty_h
    penalty = config.ERROR_PENALTY_FACTOR * H

    if error_type == "concept":
        ability.concept_u = max(0, ability.concept_u - penalty)
    elif error_type == "calculation":
        ability.calculation_c = max(0, ability.calculation_c - penalty)
    
    db.session.commit()

def update_student_ability(user_id, skill_id, question_id, is_correct, time_taken_seconds):
    """
    根據學生的答題表現，更新其在特定知識點上的能力值 (A, U, C)。
    """
    question = db.session.query(TextbookExample).options(
        db.joinedload(TextbookExample.skill_info)
    ).filter(TextbookExample.id == question_id).first()
    
    if not question: return

    H = question.difficulty_h

    ability = StudentAbility.query.filter_by(user_id=user_id, skill_id=skill_id).first()
    if not ability:
        ability = StudentAbility(user_id=user_id, skill_id=skill_id)
        db.session.add(ability)

    if is_correct:
        if time_taken_seconds < config.AVG_ANSWER_TIME_SECONDS:
            T_factor = config.T_FACTOR_FAST
        elif time_taken_seconds > config.MAX_ANSWER_TIME_SECONDS:
            T_factor = config.T_FACTOR_SLOW
        else:
            T_factor = config.T_FACTOR_NORMAL

        A_new = ability.ability_a + (H / 2) * (1 - ability.ability_a / config.ABILITY_MAX)
        U_new = ability.concept_u + (2 * (1 - ability.concept_u / config.CONCEPT_MAX) * T_factor)
        C_new = ability.calculation_c + (H * (1 - ability.calculation_c / config.CALCULATION_MAX) * T_factor)

        ability.ability_a = min(A_new, config.ABILITY_MAX)
        ability.concept_u = min(U_new, config.CONCEPT_MAX)
        ability.calculation_c = min(C_new, config.CALCULATION_MAX)
    else:
        pass # 答錯的扣分邏輯已移到 apply_error_penalty
    
    db.session.commit()
