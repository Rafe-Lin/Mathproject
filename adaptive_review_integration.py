"""
═════════════════════════════════════════════════════════════════════════════
自適應複習模式 - 集成檢查清單與快速開始
═════════════════════════════════════════════════════════════════════════════

本文件提供完整的集成步驟，確保系統正確部署。
"""

# ═════════════════════════════════════════════════════════════════════════════
# 集成檢查清單
# ═════════════════════════════════════════════════════════════════════════════

INTEGRATION_CHECKLIST = """

┌─ 【前置檢查】 ─────────────────────────────────────────────────────────┐
│                                                                           │
│  ✓ 步驟 1: 驗證必要模型和數據文件
│    □ models/akt_curriculum.pth              (AKT 知識追蹤模型)
│    □ models/rl_akt_curriculum/ppo_akt_curriculum.zip  (PPO RL 模型)
│    □ synthesized_training_data.csv          (訓練數據)
│
│  ✓ 步驟 2: 驗證 Python 依賴
│    □ torch                (深度學習框架)
│    □ gymnasium            (RL 環境)
│    □ stable-baselines3    (PPO 實現)
│    □ pandas               (數據處理)
│    □ numpy                (數值計算)
│    □ flask                (Web 框架)
│    
│    安裝命令:
│    pip install torch gymnasium stable-baselines3 pandas numpy flask
│
│  ✓ 步驟 3: 驗證文件位置
│    □ adaptive_review_mode.py        (複習引擎)
│    □ adaptive_review_api.py         (Flask API)
│    □ adaptive_review_examples.py    (使用示例)
│    □ akt_inference.py               (AKT 推論)
│    □ train_rl_akt_curriculum.py     (RL 訓練)
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【快速集成】 ─────────────────────────────────────────────────────────┐
│                                                                           │
│  步驟 A: 在主應用 (app.py) 中添加 API
│  ───────────────────────────────────────
│
│  在 app.py 頂部添加:
│  
│    from adaptive_review_api import adaptive_review_bp
│
│  在應用初始化部分添加:
│  
│    app = Flask(__name__)
│    
│    # ... 其他藍圖 ...
│    
│    # 註冊自適應複習 API
│    app.register_blueprint(adaptive_review_bp)
│    
│    if __name__ == '__main__':
│        app.run(debug=True)
│
│  ✓ 驗證: 訪問 http://127.0.0.1:5000/api/adaptive-review/health
│
│
│  步驟 B: 創建前端頁面 (可選)
│  ──────────────────────────
│
│  在 templates/ 中創建 adaptive_review.html:
│
│    <div id=\"review-interface\">\n
│      <h2>🎯 適性複習模式</h2>\n
│      <div id=\"recommendations\"></div>\n
│      <button onclick=\"startReviewSession()\">開始複習</button>\n
│    </div>\n
│    \n
│    <script src=\"{{ url_for('static', filename='adaptive_review.js') }}\"></script>
│
│  在 static/ 中創建 adaptive_review.js (見下一節)
│
│
│  步驟 C: 在現有路由中調用
│  ─────────────────────────
│
│  在 app.py 或其他路由文件中:
│
│    from adaptive_review_mode import AdaptiveReviewEngine
│    
│    @app.route('/student/<student_id>/review')
│    def student_review(student_id):
│        # 獲取學生歷史 (從數據庫)
│        history = get_student_history(student_id)
│        
│        # 初始化複習引擎
│        engine = AdaptiveReviewEngine()
│        
│        # 分析弱項
│        weak_analysis = analyze_weak_skills(engine, ...)
│        
│        return render_template('adaptive_review.html',
│                             student_id=student_id,
│                             weak_skills=weak_analysis['weakest_skills'])
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【前端示例】 (adaptive_review.js) ──────────────────────────────────┐
│                                                                           │
│  async function startReviewSession() {
│    const studentId = document.getElementById('student-id').value;
│    const history = await fetchStudentHistory(studentId);
│    
│    const response = await fetch('/api/adaptive-review/start', {
│        method: 'POST',
│        headers: {'Content-Type': 'application/json'},
│        body: JSON.stringify({
│            student_id: studentId,
│            history: history,
│            n_recommendations: 5,
│            use_rl: true
│        })
│    });
│    
│    const data = await response.json();
│    if (data.status === 'success') {
│        displayRecommendations(data.data.recommendations);
│        updateAPRDisplay(data.data.current_apr);
│    }
│  }
│  
│  async function submitAnswer(itemId, correct) {
│    const response = await fetch('/api/adaptive-review/feedback', {
│        method: 'POST',
│        headers: {'Content-Type': 'application/json'},
│        body: JSON.stringify({
│            student_id: getCurrentStudentId(),
│            history: getCurrentHistory(),
│            item_id: itemId,
│            correct: correct
│        })
│    });
│    
│    const data = await response.json();
│    updateUIWithFeedback(data.data);
│  }
│
│  function displayRecommendations(recommendations) {
│    const container = document.getElementById('recommendations');
│    container.innerHTML = recommendations.map(rec => `
│        <div class=\"recommendation-card\">
│            <h4>${rec.skill_name}</h4>
│            <p>難度: ${Math.round((1 - rec.predicted_difficulty) * 100)}%</p>
│            <button onclick=\"selectQuestion(${rec.item_id})\">
│                做這題 →
│            </button>
│        </div>
│    `).join('');
│  }
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【數據庫集成】 ────────────────────────────────────────────────────────┐
│                                                                           │
│  假設你有一個 Student 模型和 StudentHistory 模型:
│
│  def get_student_history(student_id: str):
│      \"\"\"從數據庫獲取學生的學習歷史\"\"\"
│      student = Student.query.get(student_id)
│      
│      history_records = StudentHistory.query.filter_by(
│          student_id=student_id
│      ).order_by(StudentHistory.timestamp).all()
│      
│      return {
│          'item_history': [h.item_id for h in history_records],
│          'skill_history': [h.skill_id for h in history_records],
│          'resp_history': [h.correct for h in history_records],
│      }
│
│  def save_review_session(student_id: str, session_result: Dict):
│      \"\"\"保存複習會話結果\"\"\"
│      session = ReviewSession(
│          student_id=student_id,
│          apr_before=session_result['apr_before'],
│          apr_after=session_result['apr_after'],
│          items_count=len(session_result['items']),
│          correct_count=sum(1 for i in session_result['items'] if i['correct']),
│          timestamp=datetime.now()
│      )
│      db.session.add(session)
│      db.session.commit()
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【性能優化】 ──────────────────────────────────────────────────────────┐
│                                                                           │
│  1. 模型緩存
│     ──────────
│     from functools import lru_cache
│     
│     @lru_cache(maxsize=1)
│     def get_engine():
│         return AdaptiveReviewEngine()
│
│  2. 異步處理複習計畫生成
│     ─────────────────────
│     from celery import shared_task
│     
│     @shared_task
│     def generate_plan_async(student_id, history, num_sessions):
│         engine = get_engine()
│         plan = generate_review_plan(history, num_sessions, engine)
│         save_plan_to_db(student_id, plan)
│         return plan
│
│  3. 結果緩存（Redis）
│     ──────────────────
│     from flask_caching import Cache
│     
│     cache.cached(timeout=3600)
│     def analyze_student(student_id):
│         ...
│
│  4. 批量推薦優化
│     ────────────
│     使用 batch_size 處理多個學生的推薦
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【監控和日誌】 ───────────────────────────────────────────────────────┐
│                                                                           │
│  import logging
│  
│  logging.basicConfig(
│      level=logging.INFO,
│      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
│      handlers=[
│          logging.FileHandler('adaptive_review.log'),
│          logging.StreamHandler()
│      ]
│  )
│  
│  logger = logging.getLogger('adaptive_review')
│  
│  # 使用示例
│  logger.info(f'開始複習會話: {student_id}')
│  logger.warning(f'推薦失敗: {error}')
│  logger.error(f'模型載入失敗: {error}')
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【測試和驗證】 ───────────────────────────────────────────────────────┐
│                                                                           │
│  1. 運行本地測試
│     ────────────
│     python adaptive_review_examples.py 1
│
│  2. 運行 API 測試
│     ─────────────
│     # 終端 1: 啟動應用
│     python app.py
│     
│     # 終端 2: 運行測試
│     python adaptive_review_examples.py 3
│
│  3. 創建單元測試
│     ────────────
│     import unittest
│     from adaptive_review_mode import AdaptiveReviewEngine
│     
│     class TestAdaptiveReview(unittest.TestCase):
│         def setUp(self):
│             self.engine = AdaptiveReviewEngine()
│         
│         def test_knowledge_state_computation(self):
│             history = {
│                 'item_history': [0, 5, 10],
│                 'skill_history': [0, 1, 2],
│                 'resp_history': [1, 0, 1],
│             }
│             s_t = self.engine.get_knowledge_state(...)
│             self.assertEqual(len(s_t), self.engine.n_items)
│
│  4. 負載測試
│     ────────
│     ab -n 1000 -c 10 http://127.0.0.1:5000/api/adaptive-review/health
│
└───────────────────────────────────────────────────────────────────────────┘

┌─ 【部署】 ──────────────────────────────────────────────────────────────┐
│                                                                           │
│  1. 生產環境設定
│     ────────────
│     # .env 文件
│     FLASK_ENV=production
│     FLASK_DEBUG=0
│     AKT_INFER_DEVICE=cuda
│     
│  2. 使用 Gunicorn
│     ─────────────
│     pip install gunicorn
│     gunicorn -w 4 -b 0.0.0.0:5000 app:app
│     
│  3. 使用 Docker
│     ──────────
│     docker build -t adaptive-review .
│     docker run -p 5000:5000 adaptive-review
│
│  4. 負載均衡
│     ────────
│     使用 Nginx 進行反向代理
│     upstream adaptive_review {
│         server 127.0.0.1:5001;
│         server 127.0.0.1:5002;
│         server 127.0.0.1:5003;
│     }
│
└───────────────────────────────────────────────────────────────────────────┘

"""

# ═════════════════════════════════════════════════════════════════════════════
# 快速驗證腳本
# ═════════════════════════════════════════════════════════════════════════════

def verify_installation():
    """驗證所有必需的依賴和文件"""
    import os
    import sys
    
    print("\n" + "="*70)
    print("自適應複習模式 - 安裝驗證")
    print("="*70 + "\n")
    
    checks = {
        '✓ 必需文件': [
            ('models/akt_curriculum.pth', 'AKT 模型'),
            ('models/rl_akt_curriculum/ppo_akt_curriculum.zip', 'RL 模型'),
            ('synthesized_training_data.csv', '訓練數據'),
            ('adaptive_review_mode.py', '複習引擎'),
            ('adaptive_review_api.py', 'Flask API'),
            ('akt_inference.py', 'AKT 推論'),
        ],
        '✓ Python 依賴': [
            'torch',
            'gymnasium',
            'stable_baselines3',
            'pandas',
            'numpy',
            'flask',
        ]
    }
    
    all_passed = True
    
    # 檢查文件
    print("📁 檢查文件...")
    for filepath, desc in checks['✓ 必需文件']:
        if os.path.exists(filepath):
            print(f"  ✓ {filepath:50} ({desc})")
        else:
            print(f"  ✗ {filepath:50} ({desc}) - 缺失")
            all_passed = False
    
    # 檢查依賴
    print("\n📦 檢查 Python 依賴...")
    for package in checks['✓ Python 依賴']:
        try:
            __import__(package)
            print(f"  ✓ {package:30} 已安裝")
        except ImportError:
            print(f"  ✗ {package:30} 未安裝")
            all_passed = False
    
    # 驗證模型載入
    print("\n🔧 驗證模型...")
    try:
        from adaptive_review_mode import AdaptiveReviewEngine
        engine = AdaptiveReviewEngine()
        print(f"  ✓ 複習引擎初始化成功")
        print(f"    - 技能數: {engine.n_skills}")
        print(f"    - 題目數: {engine.n_items}")
    except Exception as e:
        print(f"  ✗ 複習引擎初始化失敗: {e}")
        all_passed = False
    
    # 最終結果
    print("\n" + "="*70)
    if all_passed:
        print("✅ 所有檢查通過！系統可以正常使用")
    else:
        print("❌ 有些檢查未通過，請參考上面的錯誤信息")
    print("="*70 + "\n")
    
    return all_passed


def quick_test():
    """快速功能測試"""
    print("\n" + "="*70)
    print("快速功能測試")
    print("="*70 + "\n")
    
    try:
        from adaptive_review_mode import AdaptiveReviewEngine, analyze_weak_skills
        
        # 初始化引擎
        print("1️⃣  初始化引擎...")
        engine = AdaptiveReviewEngine()
        print("   ✓ 成功\n")
        
        # 測試知識狀態推論
        print("2️⃣  測試知識狀態推論...")
        history = {
            'item_history': [0, 5, 10],
            'skill_history': [0, 1, 2],
            'resp_history': [1, 0, 1],
        }
        s_t = engine.get_knowledge_state(
            history['item_history'],
            history['skill_history'],
            history['resp_history']
        )
        apr = engine.get_apr(s_t)
        print(f"   ✓ APR = {apr:.4f}\n")
        
        # 測試弱項分析
        print("3️⃣  測試弱項分析...")
        analysis = analyze_weak_skills(engine, 
            history['item_history'],
            history['skill_history'],
            history['resp_history']
        )
        print(f"   ✓ 最弱技能: {analysis['weakest_skills'][0]['skill_name']}\n")
        
        # 測試推薦
        print("4️⃣  測試題目推薦...")
        recs = engine.recommend_next_items(
            history['item_history'],
            history['skill_history'],
            history['resp_history'],
            n_items=3,
            use_rl=True
        )
        print(f"   ✓ 推薦 {len(recs)} 題:")
        for rec in recs[:2]:
            print(f"     - Item {rec['item_id']}: {rec['skill_name']}\n")
        
        print("="*70)
        print("✅ 所有測試通過！")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    print(INTEGRATION_CHECKLIST)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'verify':
            verify_installation()
        elif sys.argv[1] == 'test':
            quick_test()
    else:
        # 默認運行驗證
        if verify_installation():
            print("\n💡 下一步: python adaptive_review_integration.py test\n")
