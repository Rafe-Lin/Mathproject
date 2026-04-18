#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
# ID: seed_unit_pattern_skills.py
# Version: V1.0.0 (Unit Pattern DB Seed)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   將 MVP 三個 pattern skills 寫入 skills_info 與 skill_curriculum，使
#   /get_next_question?mode=unit 可運作。採輕量 Flask 啟動，避免載入完整 app 管線。
#   執行：python scripts/seed_unit_pattern_skills.py
#
# [Database Schema Usage]:
#   寫入 SkillInfo、SkillCurriculum；呼叫 init_db。
#
# [Logic Flow]:
#   1. 建立最小 Flask app 與 DB 上下文。
#   2. 插入根式相關三技能列。
#   3. 提交交易。
# ==============================================================================

import os
import sys

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)
os.chdir(basedir)


def seed():
    from flask import Flask
    from config import Config
    from models import db, SkillInfo, SkillCurriculum, init_db

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        init_db(db.engine)
        skills_to_add = [
            {"skill_id": "jh_數學2上_RadicalSimplify", "skill_ch_name": "根式化簡", "skill_en_name": "RadicalSimplify"},
            {"skill_id": "jh_數學2上_RadicalAddSub", "skill_ch_name": "根式加減", "skill_en_name": "RadicalAddSub"},
            {"skill_id": "jh_數學2上_RadicalMultiply", "skill_ch_name": "根式相乘", "skill_en_name": "RadicalMultiply"},
        ]
        for s in skills_to_add:
            existing = SkillInfo.query.filter_by(skill_id=s["skill_id"]).first()
            if not existing:
                si = SkillInfo(
                    skill_id=s["skill_id"],
                    skill_en_name=s["skill_en_name"],
                    skill_ch_name=s["skill_ch_name"],
                    description=f"單一題型 pattern skill: {s['skill_ch_name']}",
                    input_type="text",
                    gemini_prompt="",
                    is_active=True,
                )
                db.session.add(si)
                print(f"  + skills_info: {s['skill_id']}")
            else:
                print(f"  - skills_info 已存在: {s['skill_id']}")

        curriculum, grade, volume, chapter, section = "junior_high", 8, "數學2上", "第二章 二次方根與畢氏定理", "根式四則"
        for i, s in enumerate(skills_to_add):
            sid = s["skill_id"]
            paragraph = str(i)  # 區分每筆以滿足 unique 約束
            existing = SkillCurriculum.query.filter_by(
                curriculum=curriculum, volume=volume, chapter=chapter, skill_id=sid
            ).first()
            if not existing:
                sc = SkillCurriculum(
                    skill_id=sid,
                    curriculum=curriculum,
                    grade=grade,
                    volume=volume,
                    chapter=chapter,
                    section=section,
                    paragraph=paragraph,
                    display_order=i,
                    difficulty_level=1,
                )
                db.session.add(sc)
                print(f"  + skill_curriculum: {sid} @ {chapter}")
            else:
                print(f"  - skill_curriculum 已存在: {sid}")

        db.session.commit()
        print("完成。")


if __name__ == "__main__":
    seed()
