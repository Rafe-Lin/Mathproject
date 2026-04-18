from app import app, db
from models import SkillInfo, SkillPrerequisites

with app.app_context():
    # 搜尋包含 "加減" 的技能
    skills = db.session.query(SkillInfo).filter(
        db.or_(
            SkillInfo.skill_ch_name.like('%加減%'),
            SkillInfo.skill_id.like('%Mixed%'),
            SkillInfo.skill_id.like('%addition%')
        )
    ).all()
    
    print(f"找到 {len(skills)} 個相關技能：")
    for skill in skills:
        print(f"\nID: {skill.skill_id}")
        print(f"名稱: {skill.skill_ch_name}")
        
        # 檢查前置單元
        prereqs = skill.prerequisites if hasattr(skill, 'prerequisites') else []
        if prereqs:
            print(f"  前置單元 ({len(prereqs)}):")
            for p in prereqs:
                print(f"    - {p.skill_ch_name}")
        else:
            print("  無前置單元")
