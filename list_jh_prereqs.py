from app import app, db
from models import SkillInfo

with app.app_context():
    # 查找所有國一技能並列出有前置單元的
    jh_skills = db.session.query(SkillInfo).filter(
        SkillInfo.skill_id.like('jh_%')
    ).all()
    
    skills_with_prereqs = []
    for skill in jh_skills:
        prereqs = skill.prerequisites if hasattr(skill, 'prerequisites') else []
        if prereqs:
            skills_with_prereqs.append({
                'id': skill.skill_id,
                'name': skill.skill_ch_name,
                'prereq_count': len(prereqs),
                'prereqs': [p.skill_ch_name for p in prereqs]
            })
    
    print(f"找到 {len(skills_with_prereqs)} 個有前置單元的國一技能：\n")
    for s in sorted(skills_with_prereqs, key=lambda x: x['prereq_count'], reverse=True):
        print(f"【{s['name']}】")
        print(f"  ID: {s['id']}")
        print(f"  前置單元 ({s['prereq_count']}):")
        for p in s['prereqs']:
            print(f"    - {p}")
        print()
