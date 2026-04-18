from app import app
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum

with app.app_context():
    print("=" * 60)
    print("國中一年級上學期 第一章 知識圖譜驗證")
    print("=" * 60)
    
    # 查詢國中一年級上學期的所有章節
    chapters = db.session.query(SkillCurriculum.chapter).filter(
        SkillCurriculum.curriculum == 'junior_high',
        SkillCurriculum.grade == 7,
        SkillCurriculum.volume == '數學1上'
    ).distinct().all()
    
    print(f"\n可用章節: {[c[0] for c in chapters]}")
    
    # 取第一章
    if chapters:
        first_chapter = chapters[0][0]
        print(f"\n正在檢查: {first_chapter}")
        print("-" * 60)
        
        # 查詢該章節的所有技能
        skills_in_chapter = db.session.query(SkillCurriculum).filter(
            SkillCurriculum.curriculum == 'junior_high',
            SkillCurriculum.grade == 7,
            SkillCurriculum.volume == '數學1上',
            SkillCurriculum.chapter == first_chapter
        ).all()
        
        print(f"\n該章節共有 {len(skills_in_chapter)} 個知識點")
        print("\n知識點列表:")
        
        skill_ids = []
        for i, sc in enumerate(skills_in_chapter, 1):
            skill = db.session.get(SkillInfo, sc.skill_id)
            if skill:
                skill_ids.append(skill.skill_id)
                print(f"{i}. [{skill.skill_id}] {skill.skill_ch_name}")
                print(f"   節: {sc.section}")
        
        # 查詢這些技能的前置關係
        print("\n" + "=" * 60)
        print("前置關係圖譜:")
        print("=" * 60)
        
        prereqs = db.session.query(SkillPrerequisites).filter(
            SkillPrerequisites.skill_id.in_(skill_ids)
        ).all()
        
        if prereqs:
            print(f"\n找到 {len(prereqs)} 個前置關係:\n")
            for prereq in prereqs:
                target_skill = db.session.get(SkillInfo, prereq.skill_id)
                prereq_skill = db.session.get(SkillInfo, prereq.prerequisite_id)
                
                if target_skill and prereq_skill:
                    print(f"  {prereq_skill.skill_ch_name}")
                    print(f"    ↓")
                    print(f"  {target_skill.skill_ch_name}")
                    print()
        else:
            print("\n⚠️ 警告: 該章節沒有找到任何前置關係！")
            print("這表示資料庫中可能沒有匯入前置關係資料。")
        
        # 模擬 API 返回的資料格式
        print("\n" + "=" * 60)
        print("API 會返回的資料格式 (nodes + links):")
        print("=" * 60)
        
        nodes = []
        for skill_id in skill_ids:
            skill = db.session.get(SkillInfo, skill_id)
            if skill:
                nodes.append({
                    'id': skill.skill_id,
                    'name': skill.skill_ch_name
                })
        
        links = []
        for prereq in prereqs:
            links.append({
                'source': prereq.prerequisite_id,
                'target': prereq.skill_id
            })
        
        print(f"\nNodes: {len(nodes)} 個")
        for node in nodes[:5]:
            print(f"  - {node['name']}")
        if len(nodes) > 5:
            print(f"  ... 還有 {len(nodes) - 5} 個")
        
        print(f"\nLinks: {len(links)} 個")
        for link in links[:5]:
            source_skill = db.session.get(SkillInfo, link['source'])
            target_skill = db.session.get(SkillInfo, link['target'])
            if source_skill and target_skill:
                print(f"  - {source_skill.skill_ch_name} → {target_skill.skill_ch_name}")
        if len(links) > 5:
            print(f"  ... 還有 {len(links) - 5} 個")
        
        print("\n" + "=" * 60)
        print("✅ 驗證完成")
        print("=" * 60)
