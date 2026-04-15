# -*- coding: utf-8 -*-
# ==============================================================================
# ID: seed_analysis_data.py
# Version: V1.0.0 (Analysis Report Seed Data)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   建立或補齊學情分析報表示範所需之假資料（學生、錯題紀錄、診斷等），
#   供驗證視覺化與報表流程。
#
# [Database Schema Usage]:
#   寫入 User、MistakeLog、LearningDiagnosis、SkillInfo 等（依腳本邏輯）。
#
# [Logic Flow]:
#   1. 建立 Flask app 上下文。
#   2. 建立虛擬學生與種子錯題/診斷資料。
#   3. 提交資料庫。
# ==============================================================================
import sys
import os
import random
import json
from datetime import datetime, timedelta

# Add parent directory to path to import app and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy API key for seeding context
os.environ['GEMINI_API_KEY'] = 'dummy_key_for_seeding'

from app import create_app, db
from models import User, MistakeLog, LearningDiagnosis, SkillInfo

def seed_data():
    app = create_app()
    with app.app_context():
        print("Starting data seeding for Analysis Report...")

        # 1. Get or Create Dummy Students
        students = User.query.filter_by(role='student').all()
        if not students:
            print("No students found. Creating dummy students...")
            for i in range(1, 6):
                username = f"student{i}"
                if not User.query.filter_by(username=username).first():
                    user = User(username=username, password_hash='dummy', role='student')
                    db.session.add(user)
            db.session.commit()
            students = User.query.filter_by(role='student').all()
        
        print(f"Found {len(students)} students.")

        # 2. Seed Mistake Logs (for Chart)
        # Define some common questions/mistakes
        common_mistakes = [
            ("若 f(x) = 2x + 1，求 f(3)", "2*3+1=7"),
            ("解方程式 2x + 5 = 15", "x=5"),
            ("多項式 x^2 - 1 的因式分解", "(x+1)(x-1)"),
            ("計算 sin(30°)", "0.5"),
            ("若 x + y = 5, x - y = 1，求 x", "x=3"),
            ("圓周率的近似值", "3.14"),
            ("log(100) 的值", "2"),
            ("3 的平方法", "9"),
        ]

        print("Seeding MistakeLog...")
        for _ in range(50):  # Generate 50 mistake logs
            student = random.choice(students)
            question, correct = random.choice(common_mistakes)
            
            # Simulate some questions being wrong more often
            if random.random() > 0.5:
                 question, correct = common_mistakes[0] # "若 f(x) = 2x + 1..." is very hard apparently

            mistake = MistakeLog(
                user_id=student.id,
                skill_id='SKILL_001', # Dummy
                question_content=question,
                user_answer="wrong answer",
                correct_answer=correct,
                error_type='calculation',
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(mistake)
        
        # 3. Seed Learning Diagnosis (for List)
        print("Seeding LearningDiagnosis...")
        units = ["多項式", "指數與對數", "三角函數", "數列與級數"]
        comments = [
            "計算能力需加強，建議多練習基礎運算。",
            "觀念大致正確，但在細節上容易粗心。",
            "對此單元掌握度高，可嘗試挑戰進階題。",
            "建議回頭複習基本定義。",
            "表現優異！"
        ]

        for _ in range(20): # Generate 20 diagnosis records
            student = random.choice(students)
            unit = random.choice(units)
            comment = random.choice(comments)

            diagnosis = LearningDiagnosis(
                student_id=student.id,
                radar_chart_data=json.dumps({"calculation": 3, "concept": 4}),
                ai_comment=f"[{unit}] {comment}",
                recommended_unit=unit,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
            )
            db.session.add(diagnosis)

        db.session.commit()
        print("Data seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
