# -*- coding: utf-8 -*-
# ==============================================================================
# ID: prompt_factory_v9.py
# Version: V9.1.2 (V9 Prompt Factory)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   V9 專用 Prompt 生成工廠：依課程篩選批次產生 Cloud/Local/Edge 等 Tier 的
#   gencode prompt 規格，並寫入 skill_gencode_prompt；互動選單標示更新狀態。
#
# [Database Schema Usage]:
#   讀寫 SkillGenCodePrompt、SkillInfo、SkillCurriculum；呼叫 generate_v9_spec。
#
# [Logic Flow]:
#   1. 互動選擇課綱/章節與 tier。
#   2. 對選中技能呼叫 generate_v9_spec。
#   3. 提交資料庫並顯示進度。
# ==============================================================================

import sys
import os
import time
from tqdm import tqdm
from sqlalchemy import distinct

# --- 1. 路徑修正 (確保能找到根目錄的 models 與 app) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models import db, SkillInfo, SkillCurriculum, SkillGenCodePrompt
from core.prompt_architect import generate_v9_spec

def get_user_selection(options, prompt_text):
    """移植自 v8.6.2 的選單功能"""
    if not options: return None
    options = sorted([o for o in options if o is not None])
    
    print(f"\n{prompt_text}")
    print("   [0] ALL (全部/跳過)")
    for i, opt in enumerate(options, 1):
        print(f"   [{i}] {opt}")
        
    while True:
        try:
            choice = input("👉 請選擇 (輸入數字): ").strip()
            if choice == '0': return None
            idx = int(choice) - 1
            if 0 <= idx < len(options): return options[idx]
            print("❌ 輸入無效，請重試。")
        except ValueError:
            print("❌ 請輸入數字。")

def run_architect_factory(skill_ids, model_tag_choice):
    """
    執行 Prompt 生成任務 (僅 Stage 1)
    """
    # 定義要運行的 Tags
    target_tags = []
    if model_tag_choice == 'generate_all':
        target_tags = ['cloud_pro', 'local_14b', 'edge_7b']
    else:
        target_tags = [model_tag_choice]

    print("\n" + "="*60)
    print(f"🧠 [V9.1.2 Architect Factory] 啟動 Prompt 備料程序")
    print(f"   - 技能數量: {len(skill_ids)}")
    print(f"   - 目標分級: {target_tags}")
    print("="*60)

    success_count = 0
    fail_count = 0

    # 開始批次處理
    for skill_id in tqdm(skill_ids, desc="Overall", unit="skill"):
        print(f"\n🔹 Analyzing: {skill_id}")
        
        for tag in target_tags:
            print(f"   -> Generating {tag} spec...", end=" ", flush=True)
            try:
                # 呼叫修改後的核心架構師
                result = generate_v9_spec(skill_id, model_tag=tag)
                
                if result.get('success'):
                    print(f"✅ (V{result['version']})")
                    success_count += 1
                else:
                    print(f"❌ ({result.get('message')})")
                    fail_count += 1
            except Exception as e:
                print(f"💥 Error: {e}")
                fail_count += 1

    print("\n" + "="*60)
    print(f"🎉 備料完成！")
    print(f"   成功生成: {success_count} 筆 Prompt")
    print(f"   失敗數量: {fail_count} 筆")
    print(f"   提示：助教指引已同步更新至 SkillInfo.gemini_prompt")
    print("="*60)

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        print("\n============================================================")
        print("🚀 Math-Master V9.1.2 Prompt 工廠 (階層式範圍選取)")
        print("============================================================")
        
        # --- 1. 階層式選取 (嚴格參考 sync_skills_files.py) ---
        
        # 1.1 選擇課綱
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        sel_curr = get_user_selection(curriculums, "請選擇課綱:")

        # 1.2 選擇年級
        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if sel_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == sel_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        sel_grade = get_user_selection(grades, "請選擇年級:")

        # 1.3 選擇冊別
        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if sel_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: q_vol = q_vol.filter(SkillCurriculum.grade == sel_grade)
        volumes = [r[0] for r in q_vol.all()]
        sel_vol = get_user_selection(volumes, "請選擇冊別:")

        # 1.4 選擇章節
        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if sel_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: q_chap = q_chap.filter(SkillCurriculum.grade == sel_grade)
        if sel_vol: q_chap = q_chap.filter(SkillCurriculum.volume == sel_vol)
        chapters = [r[0] for r in q_chap.all()]
        sel_chap = get_user_selection(chapters, "請選擇章節:")

        # 1.5 單一技能挑選 (支援 display_order 排序)
        sel_skill_id = None
        if any([sel_curr, sel_grade, sel_vol, sel_chap]):
            q_skill = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).join(SkillCurriculum).filter(SkillInfo.is_active == True)
            if sel_curr: q_skill = q_skill.filter(SkillCurriculum.curriculum == sel_curr)
            if sel_grade: q_skill = q_skill.filter(SkillCurriculum.grade == sel_grade)
            if sel_vol: q_skill = q_skill.filter(SkillCurriculum.volume == sel_vol)
            if sel_chap: q_skill = q_skill.filter(SkillCurriculum.chapter == sel_chap)
            
            skills_raw = q_skill.order_by(SkillCurriculum.display_order).all()
            skill_opts = [f"{s.skill_id} | {s.skill_ch_name}" for s in skills_raw]
            
            if skill_opts:
                sel_skill_str = get_user_selection(skill_opts, "請選擇單一技能 (Optional):")
                if sel_skill_str:
                    sel_skill_id = sel_skill_str.split(' | ')[0].strip()

        # --- 2. 鎖定最終清單 ---
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        if sel_curr: query = query.filter(SkillCurriculum.curriculum == sel_curr)
        if sel_grade: query = query.filter(SkillCurriculum.grade == sel_grade)
        if sel_vol: query = query.filter(SkillCurriculum.volume == sel_vol)
        if sel_chap: query = query.filter(SkillCurriculum.chapter == sel_chap)
        if sel_skill_id: query = query.filter(SkillInfo.skill_id == sel_skill_id)
        
        target_ids = list(set([r[0] for r in query.all()]))
        target_ids.sort()

        if not target_ids:
            print("❌ 找不到符合條件的技能。")
            sys.exit(0)

        # --- 3. 設定分級參數 ---
        print("\n" + "-"*40)
        print("🎯 請選擇要生成的 Prompt 分級 (Model Tag):")
        print("   [1] \033[1;33mcloud_pro\033[0m  (全量生成 12+ 題型，更新助教指引)")
        print("   [2] \033[1;36mlocal_14b\033[0m  (歸納為 3 大核心題型，不更新助教)")
        print("   [3] \033[1;36medge_7b\033[0m    (精煉為 1 種最簡計算，不更新助教)")
        print("   [4] Generate ALL (一次生成三種，助教以 Cloud 為準)")
        
        choice_map = {'1': 'cloud_pro', '2': 'local_14b', '3': 'edge_7b', '4': 'generate_all'}
        while True:
            c = input("👉 請輸入 (1-4): ").strip()
            if c in choice_map:
                selected_tag = choice_map[c]
                break
        
        # --- 4. 執行確認 ---
        print(f"\n⚠️  準備為 {len(target_ids)} 個技能生成 '{selected_tag}' 規格書。")
        if input("👉 確認執行？ (y/n): ").lower() == 'y':
            run_architect_factory(target_ids, selected_tag)
        else:
            print("操作已取消。")