import os
from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    print("=== 資料庫診斷報告 ===")
    print(f"1. 實體資料庫路徑: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"2. 目前存在的表格: {existing_tables}")
    
    # 檢查缺失的表格
    expected_tables = [
        'users', 'progress', 'skills_info', 'skill_gencode_prompt', 
        'skill_curriculum', 'skill_prerequisites', 'classes', 
        'class_students', 'mistake_logs', 'exam_analysis', 
        'mistake_notebook_entries', 'textbook_examples', 
        'learning_diagnosis', 'system_settings', 'experiment_log', 
        'questions', 'quiz_attempts'
    ]
    
    missing = [t for t in expected_tables if t not in existing_tables]
    if missing:
        print(f"❌ 缺失表格: {missing}")
    else:
        print("✅ 所有定義的表格皆已存在。")

    # 檢查關鍵資料數量 (決定選單是否能顯示)
    from models import SkillCurriculum, SkillInfo
    try:
        curriculum_count = db.session.query(SkillCurriculum).count()
        skill_count = db.session.query(SkillInfo).count()
        print(f"3. 課綱資料數 (skill_curriculum): {curriculum_count}")
        print(f"4. 技能主資料數 (skills_info): {skill_count}")
    except Exception as e:
        print(f"❌ 讀取資料失敗: {e}")