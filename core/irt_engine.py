# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱: core/irt_engine.py
功能說明: 提供基於 IRT 的能力計算與更新，將題庫作答結果透過 AI 或 Jaccard 相似度匹配到知識圖譜的細部節點。
=============================================================================
"""

import math
from datetime import datetime
import json
import logging
from sqlalchemy import text

# Import the SQLAlchemy db and the models we need
from models import db, NodeCompetency, SkillFamilyBridge

logger = logging.getLogger(__name__)

# IRT Configuration
DEFAULT_THETA = 0.0          # 預設能力值
THETA_MIN, THETA_MAX = -3.0, 3.0 # 能力值邊界
LEARNING_RATE = 0.4          # K 值：每次更新的幅度
DEFAULT_DIFFICULTY = 0.0     # 預設題目難度 (b)
    
def calculate_irt_probability(theta, b):
    """
    計算學生(能力 theta) 在面對難度(b) 時的答對機率 (1PL Rasch Model)。
    """
    # 避免 math.exp 溢位限制
    x = theta - b
    if x > 10: return 0.999
    if x < -10: return 0.001
    return 1.0 / (1.0 + math.exp(-x))

def theta_to_score(theta):
    """將 -3 到 +3 的 theta 轉為 0 到 100 的百分制分數"""
    # 使用 logistic 函數做平滑轉換
    p = 1.0 / (1.0 + math.exp(-1.5 * theta))
    score = round(p * 100, 1)
    return max(0.0, min(100.0, score))

def _jaccard_similarity(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return float(intersection) / union if union > 0 else 0.0

def match_family_id_by_text(skill_id, problem_text):
    """
    利用簡單的 Jaccard 相似度演算法，將問題的文字匹配到關聯的 family_id (知識圖譜節點) 上。
    1. 撈出該 skill_id 對應的所有 family_id 及其 subskill_nodes。
    2. 將 problem_text 清洗分詞。
    3. 計算兩者的文字相關性。
    回傳：最相近的 family_id 列表 (1~2個)
    """
    bridges = db.session.query(SkillFamilyBridge).filter_by(skill_id=skill_id).all()
    if not bridges:
        return []
    
    # 簡單文字清洗
    clean_problem = set(problem_text.lower().replace(',', ' ').replace('。', ' ').replace('?', ' ').split())
    
    scores = []
    for bridge in bridges:
        try:
            nodes = json.loads(bridge.subskill_nodes)
        except:
            nodes = [item.strip() for item in str(bridge.subskill_nodes or '').split(';')]
            
        nodes_str = " ".join(nodes).lower()
        clean_nodes = set(nodes_str.replace('_', ' ').replace('-', ' ').split())
        
        sim = _jaccard_similarity(clean_problem, clean_nodes)
        scores.append((bridge.family_id, sim))
    
    # 排序並取最高分的，若分數相同可以回傳全部或前兩個
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # 回傳 top 2
    top_matches = [item[0] for item in scores[:2] if item[1] > 0]
    
    # 如果都沒匹配到字詞，預設回傳該 skill 最核心的第一個節點，或全回傳
    if not top_matches and scores:
        top_matches = [scores[0][0]]
        
    return top_matches

def update_node_competencies(user_id, skill_id, problem_text, is_correct, difficulty_level=1):
    """
    更新能力質主程式：
    當學生做完一題時，找出關聯的知識圖譜微節點，並利用 IRT 理論更新能力質。
    """
    try:
        # 1. 動態匹配
        target_nodes = match_family_id_by_text(skill_id, problem_text)
        if not target_nodes:
            logger.warning(f"No target nodes found for skill {skill_id}")
            return False
            
        # 簡易難度轉換：將 difficulty_level (1~5) 轉為 IRT 難度 b (-1.5 ~ +1.5)
        # 1: 非常簡單 (-1.5), 2: 簡單 (-0.5), 3: 中等 (0), 4: 困難 (0.5), 5: 極難 (1.5)
        b_map = {1: -1.5, 2: -0.5, 3: 0.0, 4: 0.5, 5: 1.5}
        b = b_map.get(difficulty_level, 0.0)
        
        S = 1.0 if is_correct else 0.0
        
        for node_id in target_nodes:
            # 取得目前的 competency
            comp = db.session.query(NodeCompetency).filter_by(user_id=user_id, node_id=node_id).first()
            if not comp:
                comp = NodeCompetency(
                    user_id=user_id, 
                    node_id=node_id, 
                    competency_theta=DEFAULT_THETA,
                    competency_score=theta_to_score(DEFAULT_THETA)
                )
                db.session.add(comp)
            
            # IRT 計算
            P = calculate_irt_probability(comp.competency_theta, b)
            new_theta = comp.competency_theta + LEARNING_RATE * (S - P)
            
            # 防止能力值爆表
            new_theta = max(THETA_MIN, min(THETA_MAX, new_theta))
            
            comp.competency_theta = new_theta
            comp.competency_score = theta_to_score(new_theta)
            
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating node competencies: {str(e)}")
        db.session.rollback()
        return False
