"""
═════════════════════════════════════════════════════════════════════════════
自適應複習模式 - Flask API 集成層
═════════════════════════════════════════════════════════════════════════════

提供 REST API 端點，將自適應複習功能整合到 Flask 應用中。

API 端點：
1. POST /api/adaptive-review/start
   - 開始新的複習會話
   - 輸入：學生學習歷史
   - 輸出：推薦題目列表

2. GET /api/adaptive-review/analyze/<student_id>
   - 分析學生弱項
   - 輸出：弱項技能、建議

3. POST /api/adaptive-review/feedback
   - 提交答題反饋
   - 輸入：題目 ID、答對結果
   - 輸出：更新後的知識狀態、下一步推薦

4. GET /api/adaptive-review/plan/<student_id>
   - 生成多會話複習計畫
   - 輸出：完整複習規劃
"""

from flask import Blueprint, request, jsonify
from functools import lru_cache
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from adaptive_review_mode import (
    AdaptiveReviewEngine,
    analyze_weak_skills,
    generate_review_plan,
    REVIEW_CONFIG,
    BETA_THRESHOLD,
)

# ═══════════════════════════════════════════════════════════════════════════
# 初始化
# ═══════════════════════════════════════════════════════════════════════════

logger = logging.getLogger(__name__)
adaptive_review_bp = Blueprint('adaptive_review', __name__, url_prefix='/api/adaptive-review')

# 全局引擎實例（緩存）
_engine_instance = None

def get_engine() -> AdaptiveReviewEngine:
    """獲取或創建複習引擎實例（單例）"""
    global _engine_instance
    if _engine_instance is None:
        logger.info("初始化自適應複習引擎...")
        _engine_instance = AdaptiveReviewEngine()
        logger.info("✓ 複習引擎已初始化")
    return _engine_instance


# ═══════════════════════════════════════════════════════════════════════════
# 工具函數
# ═══════════════════════════════════════════════════════════════════════════

def normalize_history(history: Dict) -> Dict:
    """
    標準化學習歷史格式
    
    支援多種輸入格式：
    - 格式1: {'item_history': [...], 'skill_history': [...], 'resp_history': [...]}
    - 格式2: {'items': [...], 'skills': [...], 'responses': [...]}
    - 格式3: [{'item_id': ..., 'skill_id': ..., 'correct': ...}, ...]
    """
    if isinstance(history, list):
        # 格式3 → 標準格式
        items = [h.get('item_id', 0) for h in history]
        skills = [h.get('skill_id', 0) for h in history]
        responses = [h.get('correct', 0) for h in history]
        return {
            'item_history': items,
            'skill_history': skills,
            'resp_history': responses,
        }
    
    # 支援別名
    if 'items' in history and 'item_history' not in history:
        history['item_history'] = history.pop('items')
    if 'skills' in history and 'skill_history' not in history:
        history['skill_history'] = history.pop('skills')
    if 'responses' in history and 'resp_history' not in history:
        history['resp_history'] = history.pop('responses')
    
    return history


def validate_history(history: Dict) -> Tuple[bool, str]:
    """驗證歷史格式"""
    required = ['item_history', 'skill_history', 'resp_history']
    for key in required:
        if key not in history:
            return False, f"缺少必需欄位: {key}"
        if not isinstance(history[key], list):
            return False, f"{key} 必須是列表"
    
    if not (len(history['item_history']) == len(history['skill_history']) == len(history['resp_history'])):
        return False, "三個序列長度不一致"
    
    return True, "OK"


# ═══════════════════════════════════════════════════════════════════════════
# API 端點
# ═══════════════════════════════════════════════════════════════════════════

@adaptive_review_bp.route('/start', methods=['POST'])
def start_review_session():
    """
    開始新的自適應複習會話
    
    Request:
    {
        "student_id": "STU_001",
        "history": {
            "item_history": [0, 5, 10, ...],
            "skill_history": [0, 1, 2, ...],
            "resp_history": [1, 0, 1, ...]
        },
        "n_recommendations": 5,  // 可選，預設 5
        "use_rl": true            // 可選，預設 true
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "student_id": "STU_001",
            "current_apr": 0.65,
            "recommendations": [
                {
                    "item_id": 42,
                    "skill_id": 3,
                    "skill_name": "polynomial-operations",
                    "predicted_difficulty": 0.45
                },
                ...
            ],
            "session_id": "sess_abc123",
            "timestamp": "2024-01-15T10:30:00"
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': '無效的 JSON'}), 400
        
        # 提取必要信息
        student_id = data.get('student_id', 'unknown')
        history = data.get('history', {})
        n_recommendations = data.get('n_recommendations', 5)
        use_rl = data.get('use_rl', True)
        
        # 標準化和驗證
        history = normalize_history(history)
        is_valid, error_msg = validate_history(history)
        if not is_valid:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        
        # 獲取引擎
        engine = get_engine()
        
        # 計算當前知識狀態和 APR
        s_t = engine.get_knowledge_state(
            history['item_history'],
            history['skill_history'],
            history['resp_history']
        )
        current_apr = engine.get_apr(s_t)
        
        # 推薦題目
        recommendations = engine.recommend_next_items(
            history['item_history'],
            history['skill_history'],
            history['resp_history'],
            n_items=n_recommendations,
            use_rl=use_rl
        )
        
        # 生成會話 ID
        session_id = f"sess_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            'status': 'success',
            'data': {
                'student_id': student_id,
                'current_apr': current_apr,
                'apr_target': BETA_THRESHOLD,
                'recommendations': recommendations,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'min_session_length': REVIEW_CONFIG['min_session_length'],
                    'max_session_length': REVIEW_CONFIG['max_session_length'],
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 複習會話啟動失敗: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'伺服器錯誤: {str(e)}'
        }), 500


@adaptive_review_bp.route('/analyze/<student_id>', methods=['GET'])
def analyze_student(student_id: str):
    """
    分析學生的弱項和強項
    
    Query Parameters:
    - history_json: URL-encoded JSON of history
    
    Response:
    {
        "status": "success",
        "data": {
            "student_id": "STU_001",
            "overall_apr": 0.62,
            "weakest_skills": [
                {"skill_id": 5, "skill_name": "radical-operations", "mastery": 0.35},
                ...
            ],
            "strongest_skills": [
                {"skill_id": 1, "skill_name": "addition", "mastery": 0.85},
                ...
            ],
            "recommendations": [
                "建議加強根式運算",
                "已掌握基本整數運算，可考慮進階內容"
            ]
        }
    }
    """
    try:
        # 從 URL 參數讀取歷史
        history_json = request.args.get('history_json', '{}')
        history = json.loads(history_json)
        
        history = normalize_history(history)
        is_valid, error_msg = validate_history(history)
        if not is_valid:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        
        engine = get_engine()
        
        # 分析弱項
        analysis = analyze_weak_skills(
            engine,
            history['item_history'],
            history['skill_history'],
            history['resp_history']
        )
        
        # 生成建議
        recommendations = []
        overall_apr = analysis['overall_apr']
        
        if overall_apr < 0.5:
            recommendations.append("⚠️ 整體掌握度較低，建議從基礎概念開始複習")
        
        for skill in analysis['weakest_skills'][:3]:
            if skill['mastery'] < 0.4:
                recommendations.append(f"🔴 {skill['skill_name']}: 掌握度 {skill['mastery']:.2%}，需要重點加強")
            elif skill['mastery'] < 0.65:
                recommendations.append(f"🟡 {skill['skill_name']}: 掌握度 {skill['mastery']:.2%}，建議強化練習")
        
        if overall_apr >= BETA_THRESHOLD:
            recommendations.append(f"✅ 已達到目標掌握度 ({overall_apr:.2%})，可考慮進階內容")
        
        return jsonify({
            'status': 'success',
            'data': {
                'student_id': student_id,
                'overall_apr': analysis['overall_apr'],
                'target_apr': BETA_THRESHOLD,
                'weakest_skills': analysis['weakest_skills'][:5],
                'strongest_skills': analysis['strongest_skills'][:5],
                'all_skills': analysis['all_skills'],
                'recommendations': recommendations,
            }
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': '無效的歷史 JSON'}), 400
    except Exception as e:
        logger.error(f"❌ 分析失敗: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'伺服器錯誤: {str(e)}'}), 500


@adaptive_review_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    提交答題反饋並獲取下一步推薦
    
    Request:
    {
        "student_id": "STU_001",
        "history": {...},
        "item_id": 42,
        "correct": 1,
        "time_spent": 45  // 可選，單位秒
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "updated_apr": 0.68,
            "apr_change": +0.03,
            "next_recommendations": [...],
            "feedback": "很好！掌握度提升了，建議繼續練習相關題目"
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': '無效的 JSON'}), 400
        
        student_id = data.get('student_id', 'unknown')
        history = normalize_history(data.get('history', {}))
        item_id = data.get('item_id')
        correct = data.get('correct', 0)
        
        if item_id is None:
            return jsonify({'status': 'error', 'message': '缺少 item_id'}), 400
        
        # 驗證歷史
        is_valid, error_msg = validate_history(history)
        if not is_valid:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        
        engine = get_engine()
        
        # 計算反饋前的 APR
        s_t_before = engine.get_knowledge_state(
            history['item_history'],
            history['skill_history'],
            history['resp_history']
        )
        apr_before = engine.get_apr(s_t_before)
        
        # 更新歷史
        skill_id = engine.akt_inference.problem_to_skill_id.get(item_id, 0)
        updated_history = {
            'item_history': history['item_history'] + [item_id],
            'skill_history': history['skill_history'] + [skill_id],
            'resp_history': history['resp_history'] + [correct],
        }
        
        # 計算反饋後的 APR
        s_t_after = engine.get_knowledge_state(
            updated_history['item_history'],
            updated_history['skill_history'],
            updated_history['resp_history']
        )
        apr_after = engine.get_apr(s_t_after)
        apr_change = apr_after - apr_before
        
        # 獲取下一步推薦
        next_recommendations = engine.recommend_next_items(
            updated_history['item_history'],
            updated_history['skill_history'],
            updated_history['resp_history'],
            n_items=3,
            use_rl=True
        )
        
        # 生成反饋訊息
        feedback_msg = "✓ 回答已記錄" if correct else "✗ 本題未掌握"
        
        if apr_change > 0.05:
            feedback_msg += " - 掌握度顯著提升！"
        elif apr_change > 0:
            feedback_msg += " - 掌握度略有提升"
        elif apr_after >= BETA_THRESHOLD:
            feedback_msg = f"🎉 恭喜！已達到目標掌握度 ({apr_after:.2%})"
        else:
            feedback_msg += " - 建議加強練習"
        
        return jsonify({
            'status': 'success',
            'data': {
                'student_id': student_id,
                'item_id': item_id,
                'correct': correct,
                'apr_before': apr_before,
                'apr_after': apr_after,
                'apr_change': apr_change,
                'target_apr': BETA_THRESHOLD,
                'reached_target': apr_after >= BETA_THRESHOLD,
                'next_recommendations': next_recommendations,
                'feedback': feedback_msg,
                'timestamp': datetime.now().isoformat(),
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 反饋提交失敗: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'伺服器錯誤: {str(e)}'}), 500


@adaptive_review_bp.route('/plan/<student_id>', methods=['GET'])
def get_review_plan(student_id: str):
    """
    生成完整的多會話複習計畫
    
    Query Parameters:
    - history_json: URL-encoded JSON of history
    - num_sessions: 會話數（預設 3）
    
    Response:
    {
        "status": "success",
        "data": {
            "student_id": "STU_001",
            "num_sessions": 3,
            "overall_stats": {
                "apr_initial": 0.60,
                "apr_final": 0.78,
                "apr_gain": +0.18,
                "total_items_practiced": 18
            },
            "sessions": [
                {
                    "session_name": "複習會話 #1",
                    "apr_initial": 0.60,
                    "apr_final": 0.68,
                    "apr_gain": +0.08,
                    "correct_rate": 0.67,
                    "skills_practiced": {...}
                },
                ...
            ]
        }
    }
    """
    try:
        history_json = request.args.get('history_json', '{}')
        num_sessions = request.args.get('num_sessions', 3, type=int)
        
        history = json.loads(history_json)
        history = normalize_history(history)
        
        is_valid, error_msg = validate_history(history)
        if not is_valid:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        
        engine = get_engine()
        
        # 生成計畫
        plan = generate_review_plan(history, num_sessions=num_sessions, engine=engine)
        
        return jsonify({
            'status': 'success',
            'data': {
                'student_id': student_id,
                'num_sessions': num_sessions,
                'overall_stats': plan['overall_stats'],
                'sessions': plan['sessions'],
                'timestamp': datetime.now().isoformat(),
            }
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': '無效的歷史 JSON'}), 400
    except Exception as e:
        logger.error(f"❌ 計畫生成失敗: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'伺服器錯誤: {str(e)}'}), 500


@adaptive_review_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    try:
        engine = get_engine()
        return jsonify({
            'status': 'success',
            'message': '複習引擎就緒',
            'n_skills': engine.n_skills,
            'n_items': engine.n_items,
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'複習引擎異常: {e}'
        }), 500


if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(adaptive_review_bp)
    
    # 配置日誌
    logging.basicConfig(level=logging.INFO)
    
    print("自適應複習模式 API 伺服器")
    print("http://127.0.0.1:5000/api/adaptive-review/health")
    
    app.run(debug=True, port=5000)
