from app import app, db
from models import SkillInfo, SkillPrerequisites

with app.app_context():
    skill = db.session.query(SkillInfo).filter_by(
        skill_id='jh_數學1上_Mixedintegeradditionandsubtraction'
    ).first()
    
    if skill:
        print(f"技能名稱: {skill.skill_ch_name}")
        prereqs = db.session.query(SkillPrerequisites).filter_by(
            skill_id=skill.skill_id
        ).all()
        print(f"前置單元數量: {len(prereqs)}")
        for p in prereqs:
            if p.prerequisite_skill:
                print(f"  - {p.prerequisite_skill.skill_ch_name} ({p.prerequisite_skill_id})")
    else:
        print("技能不存在")
