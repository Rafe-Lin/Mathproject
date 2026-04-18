"""
更新資料庫模型和路由的 Python Script
此腳本將：
1. 在 models.py 中新增 LearningDiagnosis 模型
2. 在 init_db() 函數中新增 learning_diagnosis 資料表
3. 在 routes.py 中新增 /student/analyze_weakness API
"""

import os
import re

# ==========================================
# 第一部分：更新 models.py
# ==========================================

models_path = r'c:\Mathproject\models.py'

print("正在讀取 models.py...")
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

# 1. 在 init_db() 函數中新增 learning_diagnosis 資料表建立邏輯
# 找到 textbook_examples 表格建立後的位置 (約第 166 行之後)
init_db_insert_pattern = r"(    c\.execute\('''[\s\S]*?CREATE TABLE IF NOT EXISTS textbook_examples[\s\S]*?'''\))"

learning_diagnosis_table_sql = """
    # 新增：建立 learning_diagnosis 表格 (學生學習診斷)
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_diagnosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            radar_chart_data TEXT NOT NULL,
            ai_comment TEXT,
            recommended_unit TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')"""

# 在 textbook_examples 表格建立後插入
models_content = re.sub(
    init_db_insert_pattern,
    r"\1\n\n" + learning_diagnosis_table_sql,
    models_content,
    count=1
)

# 2. 在檔案末尾新增 LearningDiagnosis ORM 模型
learning_diagnosis_model = """

# 新增 LearningDiagnosis ORM 模型 (學生學習診斷)
class LearningDiagnosis(db.Model):
    __tablename__ = 'learning_diagnosis'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    radar_chart_data = db.Column(db.Text, nullable=False)  # JSON 格式字串
    ai_comment = db.Column(db.Text)
    recommended_unit = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯到學生
    student = db.relationship('User', backref=db.backref('learning_diagnoses', lazy=True))

    def to_dict(self):
        \"\"\"將物件轉換為可序列化的字典。\"\"\"
        import json
        return {
            'id': self.id,
            'student_id': self.student_id,
            'radar_chart_data': json.loads(self.radar_chart_data) if self.radar_chart_data else {},
            'ai_comment': self.ai_comment,
            'recommended_unit': self.recommended_unit,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
"""

# 在檔案末尾新增模型
models_content += learning_diagnosis_model

print("正在寫入 models.py...")
with open(models_path, 'w', encoding='utf-8') as f:
    f.write(models_content)

print("✓ models.py 更新完成！")

# ==========================================
# 第二部分：更新 routes.py
# ==========================================

routes_path = r'c:\Mathproject\core\routes.py'

print("\n正在讀取 routes.py...")
with open(routes_path, 'r', encoding='utf-8') as f:
    routes_content = f.read()

# 新增 /student/analyze_weakness API
# 找到檔案末尾或適當位置插入
analyze_weakness_route = """

# ==========================================
# 學生學習診斷 API
# ==========================================

@core_bp.route('/student/analyze_weakness', methods=['POST'])
@login_required
def analyze_weakness():
    \"\"\"
    學生學習弱點分析 API
    - 分析 MistakeLog 和 ExamAnalysis 資料
    - 使用質性分析方式推估各單元熟練度 (0-100)
    - 實作 24 小時快取機制
    \"\"\"
    from models import MistakeLog, ExamAnalysis, LearningDiagnosis, SkillInfo
    from datetime import datetime, timedelta
    import json
    import google.generativeai as genai
    
    try:
        # 安全性：使用 current_user.id，不從前端接收 student_id
        student_id = current_user.id
        
        # 檢查是否需要強制刷新
        force_refresh = request.json.get('force_refresh', False) if request.json else False
        
        # 快取檢查：24 小時內有記錄且未要求強制刷新
        if not force_refresh:
            cached_diagnosis = LearningDiagnosis.query.filter_by(student_id=student_id).order_by(
                LearningDiagnosis.created_at.desc()
            ).first()
            
            if cached_diagnosis:
                time_diff = datetime.utcnow() - cached_diagnosis.created_at
                if time_diff < timedelta(hours=24):
                    return jsonify({
                        'success': True,
                        'cached': True,
                        'data': cached_diagnosis.to_dict()
                    })
        
        # 收集錯題記錄
        mistake_logs = MistakeLog.query.filter_by(user_id=student_id).all()
        
        # 收集考卷診斷記錄
        exam_analyses = ExamAnalysis.query.filter_by(user_id=student_id).all()
        
        # 統計各技能的錯誤情況
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
        
        # 分析 ExamAnalysis (補充信心度和評語資訊)
        exam_feedback = {}
        for exam in exam_analyses:
            skill_id = exam.skill_id
            if skill_id not in exam_feedback:
                exam_feedback[skill_id] = {
                    'confidence_scores': [],
                    'feedbacks': []
                }
            
            if exam.confidence is not None:
                exam_feedback[skill_id]['confidence_scores'].append(exam.confidence)
            if exam.feedback:
                exam_feedback[skill_id]['feedbacks'].append(exam.feedback)
        
        # 建立 AI Prompt
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
        
        if not skill_error_stats:
            return jsonify({
                'success': False,
                'error': '尚無足夠的學習記錄進行分析'
            }), 400
        
        # 呼叫 Gemini API
        # 為了避免編碼問題，將 Prompt 分段建立
        prompt_header = "你是一位專業的數學教學診斷專家。請根據以下學生的錯題記錄，使用「質性分析」方式推估各單元的熟練度。"
        
        prompt_rules = """
**分析規則**：
1. **概念錯誤**：代表學生對該單元的核心概念不熟練，應大幅降低熟練度分數 (建議扣 30-50 分)
2. **計算錯誤/粗心**：代表學生概念理解但執行細節有誤，應輕微扣分 (建議扣 5-15 分)
3. **信心度與評語**：若 AI 評語包含正向詞彙 (如「掌握良好」、「理解正確」)，可適度提高熟練度
4. **基準分數**：假設學生初始熟練度為 80 分，根據錯誤情況進行調整

請以 JSON 格式回傳分析結果：
{
  "mastery_scores": {
    "單元名稱1": 85,
    "單元名稱2": 60
  },
  "overall_comment": "整體學習評語 (100 字以內)",
  "recommended_unit": "建議優先加強的單元名稱"
}

注意：
- 熟練度分數範圍 0-100，分數越高代表越熟練
- 請務必回傳有效的 JSON 格式
- mastery_scores 的 key 必須是上述提供的單元名稱"""

        gemini_prompt = prompt_header + "\\n\\n" + prompt_data + "\\n" + prompt_rules

        # 設定 Gemini API
        genai.configure(api_key=current_app.config.get('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(gemini_prompt)
        ai_response_text = response.text.strip()
        
        # 解析 JSON 回應
        # 移除可能的 markdown 程式碼區塊標記
        ai_response_text = re.sub(r'^```json\s*', '', ai_response_text)
        ai_response_text = re.sub(r'\s*```$', '', ai_response_text)
        
        ai_result = json.loads(ai_response_text)
        
        # 儲存分析結果到資料庫
        new_diagnosis = LearningDiagnosis(
            student_id=student_id,
            radar_chart_data=json.dumps(ai_result.get('mastery_scores', {}), ensure_ascii=False),
            ai_comment=ai_result.get('overall_comment', ''),
            recommended_unit=ai_result.get('recommended_unit', '')
        )
        
        db.session.add(new_diagnosis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cached': False,
            'data': new_diagnosis.to_dict()
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': f'AI 回應格式錯誤: {str(e)}'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'分析失敗: {str(e)}'
        }), 500
"""

# 在檔案末尾新增路由
routes_content += analyze_weakness_route

print("正在寫入 routes.py...")
with open(routes_path, 'w', encoding='utf-8') as f:
    f.write(routes_content)

print("✓ routes.py 更新完成！")

print("\n" + "="*50)
print("所有檔案更新完成！")
print("="*50)
print("\n下一步：")
print("1. 重新啟動 Flask 應用")
print("2. 執行資料庫遷移 (如果需要)")
print("3. 測試 /student/analyze_weakness API")
