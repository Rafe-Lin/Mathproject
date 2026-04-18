"""
═════════════════════════════════════════════════════════════════════════════
自適應總複習模式 - 完整使用指南與測試範例
═════════════════════════════════════════════════════════════════════════════

本文件展示如何使用自適應複習系統的各個功能。
"""

import json
import requests
from typing import Dict, List
from adaptive_review_mode import AdaptiveReviewEngine, analyze_weak_skills

# ═══════════════════════════════════════════════════════════════════════════
# 1. 本地使用示例 - 無需 API
# ═══════════════════════════════════════════════════════════════════════════

def example_local_usage():
    """
    示例 1: 在 Python 中直接使用複習引擎
    """
    print("\n" + "="*70)
    print("示例 1: 本地直接使用")
    print("="*70)
    
    # 初始化引擎
    engine = AdaptiveReviewEngine()
    
    # 模擬學生歷史
    # - 做過 5 題
    # - 技能涵蓋：加法、乘法、分數、幾何等
    student_history = {
        'item_history': [0, 5, 10, 15, 20],
        'skill_history': [0, 1, 2, 3, 4],
        'resp_history': [1, 0, 1, 1, 0],  # 3 題答對，2 題答錯
    }
    
    print(f"\n📚 學生初始狀態:")
    print(f"  - 已做題數: {len(student_history['item_history'])}")
    print(f"  - 答對率: {sum(student_history['resp_history']) / len(student_history['resp_history']):.2%}")
    
    # 分析當前知識狀態
    s_t = engine.get_knowledge_state(
        student_history['item_history'],
        student_history['skill_history'],
        student_history['resp_history']
    )
    current_apr = engine.get_apr(s_t)
    
    print(f"  - 當前 APR (平均掌握度): {current_apr:.4f}")
    print(f"  - 目標 APR: 0.6500")
    
    # 分析弱項
    print(f"\n🔍 弱項分析:")
    weak_analysis = analyze_weak_skills(
        engine,
        student_history['item_history'],
        student_history['skill_history'],
        student_history['resp_history']
    )
    
    print(f"  最弱的 3 個技能:")
    for i, skill in enumerate(weak_analysis['weakest_skills'][:3], 1):
        print(f"    {i}. {skill['skill_name']}")
        print(f"       掌握度: {skill['mastery']:.4f}, 練習次數: {skill['practice_count']}")
    
    # 推薦下一批題目
    print(f"\n📋 推薦下一批題目 (使用 RL 模型):")
    recommendations = engine.recommend_next_items(
        student_history['item_history'],
        student_history['skill_history'],
        student_history['resp_history'],
        n_items=5,
        use_rl=True  # 使用訓練好的 RL 模型
    )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. Item {rec['item_id']} - {rec['skill_name']}")
        print(f"     預測難度: {1 - rec['predicted_difficulty']:.2%}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. 多會話複習計畫示例
# ═══════════════════════════════════════════════════════════════════════════

def example_multi_session_plan():
    """
    示例 2: 生成多會話複習計畫
    """
    print("\n" + "="*70)
    print("示例 2: 多會話複習計畫")
    print("="*70)
    
    engine = AdaptiveReviewEngine()
    
    # 學生初始歷史
    student_history = {
        'item_history': list(range(10)),
        'skill_history': [i % engine.n_skills for i in range(10)],
        'resp_history': [1 if i % 2 == 0 else 0 for i in range(10)],
    }
    
    initial_apr = engine.get_apr(
        engine.get_knowledge_state(
            student_history['item_history'],
            student_history['skill_history'],
            student_history['resp_history']
        )
    )
    
    print(f"\n初始狀態:")
    print(f"  - 已做題數: {len(student_history['item_history'])}")
    print(f"  - 初始 APR: {initial_apr:.4f}")
    
    # 模擬 3 個會話
    print(f"\n模擬 3 個複習會話:")
    
    from adaptive_review_mode import generate_review_plan
    
    review_plan = generate_review_plan(
        student_history,
        num_sessions=3,
        engine=engine
    )
    
    for session in review_plan['sessions']:
        print(f"\n  {session['session_name']}")
        print(f"    - APR 增幅: {session['apr_gain']:+.4f}")
        print(f"    - 答對率: {session['correct_rate']:.2%}")
        print(f"    - 練習技能: {len(session['skills_practiced'])} 個")
    
    print(f"\n📊 整體成果:")
    print(f"  - 初始 APR: {review_plan['overall_stats']['apr_initial']:.4f}")
    print(f"  - 最終 APR: {review_plan['overall_stats']['apr_final']:.4f}")
    print(f"  - 總增幅: {review_plan['overall_stats']['apr_final'] - review_plan['overall_stats']['apr_initial']:+.4f}")
    print(f"  - 總練習題數: {review_plan['overall_stats']['total_items_practiced']}")


# ═════════════════════════════════════════════════════════════════════════════
# 3. API 調用示例
# ═════════════════════════════════════════════════════════════════════════════

class AdaptiveReviewClient:
    """
    自適應複習 API 客戶端
    
    使用示例：
        client = AdaptiveReviewClient('http://127.0.0.1:5000')
        response = client.start_review('STU_001', history)
    """
    
    def __init__(self, base_url: str = 'http://127.0.0.1:5000'):
        self.base_url = base_url
        self.prefix = '/api/adaptive-review'
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """通用請求方法"""
        url = f"{self.base_url}{self.prefix}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, **kwargs)
            elif method == 'POST':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"不支援的方法: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API 請求失敗: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def health_check(self) -> bool:
        """檢查 API 是否在線"""
        result = self._request('GET', '/health')
        return result.get('status') == 'success'
    
    def start_review(self, student_id: str, history: Dict, 
                    n_recommendations: int = 5, 
                    use_rl: bool = True) -> Dict:
        """
        開始複習會話
        
        Args:
            student_id: 學生 ID
            history: 學習歷史 {'item_history': [...], 'skill_history': [...], 'resp_history': [...]}
            n_recommendations: 推薦題目數
            use_rl: 是否使用 RL 推薦
        
        Returns:
            {'status': 'success', 'data': {...}} 或錯誤訊息
        """
        payload = {
            'student_id': student_id,
            'history': history,
            'n_recommendations': n_recommendations,
            'use_rl': use_rl,
        }
        return self._request('POST', '/start', json=payload)
    
    def analyze_student(self, student_id: str, history: Dict) -> Dict:
        """
        分析學生弱項
        
        Args:
            student_id: 學生 ID
            history: 學習歷史
        
        Returns:
            分析結果，包括弱項、強項、建議等
        """
        history_json = json.dumps(history)
        params = {'history_json': history_json}
        return self._request('GET', f'/analyze/{student_id}', params=params)
    
    def submit_feedback(self, student_id: str, history: Dict, 
                       item_id: int, correct: int) -> Dict:
        """
        提交答題反饋
        
        Args:
            student_id: 學生 ID
            history: 當前學習歷史
            item_id: 題目 ID
            correct: 是否正確 (0 或 1)
        
        Returns:
            更新後的狀態和下一步推薦
        """
        payload = {
            'student_id': student_id,
            'history': history,
            'item_id': item_id,
            'correct': correct,
        }
        return self._request('POST', '/feedback', json=payload)
    
    def get_review_plan(self, student_id: str, history: Dict, 
                       num_sessions: int = 3) -> Dict:
        """
        生成複習計畫
        
        Args:
            student_id: 學生 ID
            history: 學習歷史
            num_sessions: 會話數
        
        Returns:
            完整複習計畫
        """
        history_json = json.dumps(history)
        params = {
            'history_json': history_json,
            'num_sessions': num_sessions,
        }
        return self._request('GET', f'/plan/{student_id}', params=params)


def example_api_usage():
    """
    示例 3: 通過 API 使用複習系統
    
    前提：確保 Flask 應用已啟動
    python app.py  或  FLASK_APP=app.py flask run
    """
    print("\n" + "="*70)
    print("示例 3: 通過 API 使用")
    print("="*70)
    
    client = AdaptiveReviewClient('http://127.0.0.1:5000')
    
    # 1. 健康檢查
    print("\n[1] 健康檢查...")
    if not client.health_check():
        print("❌ API 不在線，請先啟動應用")
        print("   python app.py")
        return
    print("✓ API 在線")
    
    # 模擬學生歷史
    student_id = "STU_001"
    history = {
        'item_history': [0, 5, 10, 15, 20],
        'skill_history': [0, 1, 2, 3, 4],
        'resp_history': [1, 0, 1, 1, 0],
    }
    
    # 2. 開始複習
    print(f"\n[2] 為 {student_id} 開始複習會話...")
    result = client.start_review(student_id, history, n_recommendations=5)
    if result['status'] == 'success':
        data = result['data']
        print(f"✓ 當前 APR: {data['current_apr']:.4f}")
        print(f"  推薦 {len(data['recommendations'])} 題:")
        for rec in data['recommendations'][:3]:
            print(f"    - Item {rec['item_id']}: {rec['skill_name']}")
    else:
        print(f"❌ 錯誤: {result.get('message')}")
        return
    
    # 3. 分析弱項
    print(f"\n[3] 分析學生弱項...")
    result = client.analyze_student(student_id, history)
    if result['status'] == 'success':
        data = result['data']
        print(f"✓ 整體 APR: {data['overall_apr']:.4f}")
        print(f"  最弱技能:")
        for skill in data['weakest_skills'][:2]:
            print(f"    - {skill['skill_name']}: {skill['mastery']:.4f}")
    
    # 4. 提交反饋
    print(f"\n[4] 提交答題反饋 (Item 42, 正確)...")
    updated_history = {
        'item_history': history['item_history'] + [42],
        'skill_history': history['skill_history'] + [1],
        'resp_history': history['resp_history'] + [1],
    }
    result = client.submit_feedback(student_id, history, item_id=42, correct=1)
    if result['status'] == 'success':
        data = result['data']
        print(f"✓ APR 更新: {data['apr_before']:.4f} → {data['apr_after']:.4f}")
        print(f"  增幅: {data['apr_change']:+.4f}")
        print(f"  {data['feedback']}")
    
    # 5. 生成複習計畫
    print(f"\n[5] 生成 3 會話複習計畫...")
    result = client.get_review_plan(student_id, history, num_sessions=3)
    if result['status'] == 'success':
        data = result['data']
        stats = data['overall_stats']
        print(f"✓ 計畫完成:")
        print(f"  - 初始 APR: {stats['apr_initial']:.4f}")
        print(f"  - 預期最終 APR: {stats['apr_final']:.4f}")
        print(f"  - 預期增幅: {stats['apr_final'] - stats['apr_initial']:+.4f}")
        print(f"  - 預期練習題數: {stats['total_items_practiced']}")


# ═════════════════════════════════════════════════════════════════════════════
# 4. 整合到現有應用的示例
# ═════════════════════════════════════════════════════════════════════════════

def example_app_integration():
    """
    示例 4: 在現有 Flask 應用中整合複習功能
    
    在 app.py 中添加：
    
    from adaptive_review_api import adaptive_review_bp
    
    app = Flask(__name__)
    app.register_blueprint(adaptive_review_bp)
    """
    print("\n" + "="*70)
    print("示例 4: 應用整合")
    print("="*70)
    
    print("""
在 app.py 中添加以下代碼以整合複習功能：

    from adaptive_review_api import adaptive_review_bp
    
    app = Flask(__name__)
    
    # ... 其他藍圖 ...
    
    # 註冊自適應複習模式 API
    app.register_blueprint(adaptive_review_bp)
    
    # 可用端點：
    # - POST /api/adaptive-review/start           (開始複習)
    # - GET  /api/adaptive-review/analyze/<id>   (分析弱項)
    # - POST /api/adaptive-review/feedback        (提交反饋)
    # - GET  /api/adaptive-review/plan/<id>      (生成計畫)
    # - GET  /api/adaptive-review/health         (健康檢查)
    """)


# ═════════════════════════════════════════════════════════════════════════════
# 5. 前端集成示例
# ═════════════════════════════════════════════════════════════════════════════

def example_frontend_integration():
    """
    示例 5: 前端 JavaScript 調用示例
    """
    print("\n" + "="*70)
    print("示例 5: 前端集成")
    print("="*70)
    
    print("""
// 前端 JavaScript 代碼示例
async function startReviewSession(studentId, history) {
    try {
        const response = await fetch('/api/adaptive-review/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_id: studentId,
                history: history,
                n_recommendations: 5,
                use_rl: true
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            // 顯示推薦題目
            displayRecommendations(data.data.recommendations);
        } else {
            console.error('錯誤:', data.message);
        }
    } catch (error) {
        console.error('API 請求失敗:', error);
    }
}

// 提交答題反饋
async function submitAnswer(studentId, history, itemId, correct) {
    const response = await fetch('/api/adaptive-review/feedback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            student_id: studentId,
            history: history,
            item_id: itemId,
            correct: correct
        })
    });
    
    const data = await response.json();
    if (data.status === 'success') {
        // 更新 APR 顯示
        updateAPRDisplay(data.data.apr_after);
        // 顯示下一步推薦
        displayRecommendations(data.data.next_recommendations);
    }
}

// 分析弱項
async function analyzeWeakSkills(studentId, history) {
    const historyJson = encodeURIComponent(JSON.stringify(history));
    const response = await fetch(
        `/api/adaptive-review/analyze/${studentId}?history_json=${historyJson}`
    );
    
    const data = await response.json();
    if (data.status === 'success') {
        // 顯示弱項列表和建議
        displayWeakSkills(data.data.weakest_skills);
        displayRecommendations(data.data.recommendations);
    }
}
    """)


# ═════════════════════════════════════════════════════════════════════════════
# 主函數
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║  自適應複習系統 - 完整使用指南                              ║")
    print("╚" + "="*68 + "╝")
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "1":
            example_local_usage()
        elif example == "2":
            example_multi_session_plan()
        elif example == "3":
            print("\n⚠️  API 示例需要 Flask 應用正在運行")
            print("   請先運行: python app.py")
            print("\n然後再運行本腳本:")
            print("   python adaptive_review_examples.py 3")
            # 取消註解以實際測試 API
            # example_api_usage()
        elif example == "4":
            example_app_integration()
        elif example == "5":
            example_frontend_integration()
        else:
            print(f"未知示例: {example}")
            sys.exit(1)
    else:
        # 運行所有本地示例
        example_local_usage()
        example_multi_session_plan()
        example_app_integration()
        example_frontend_integration()
        
        print("\n" + "="*70)
        print("💡 運行特定示例:")
        print("   python adaptive_review_examples.py 1  # 本地直接使用")
        print("   python adaptive_review_examples.py 2  # 多會話計畫")
        print("   python adaptive_review_examples.py 3  # API 使用")
        print("   python adaptive_review_examples.py 4  # 應用整合")
        print("   python adaptive_review_examples.py 5  # 前端集成")
        print("="*70 + "\n")
