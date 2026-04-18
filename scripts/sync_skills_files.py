# -*- coding: utf-8 -*-
# ==============================================================================
# ID: sync_skills_files.py
# Version: V8.6.2 (DB ↔ skills/*.py Sync)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   同步資料庫 skills_info 與本機 skills/*.py：補齊缺失檔案、清理孤兒檔案、
#   依課綱階層篩選後呼叫 Architect/Coder 產生程式碼；技能列表依 display_order 排序。
#
# [Database Schema Usage]:
#   讀寫 SkillInfo、SkillCurriculum、TextbookExample；觸發 code_generator / prompt 產線。
#
# [Logic Flow]:
#   1. 互動選擇課綱範圍並比對 DB 與檔案系統。
#   2. 生成缺失檔或刪除確認後之孤兒檔。
#   3. 輸出統計與日誌。
# ==============================================================================

import sys
import os
import glob
import time
import logging
from datetime import datetime
from tqdm import tqdm
from sqlalchemy import distinct

# ==============================================================================
# 1. 智慧路徑設定 (自動偵測專案根目錄)
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while not os.path.exists(os.path.join(project_root, 'app.py')):
    parent = os.path.dirname(project_root)
    if parent == project_root:
        print("❌ 錯誤：無法定位專案根目錄 (找不到 app.py)")
        sys.exit(1)
    project_root = parent

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.code_generator import auto_generate_skill_code
from core.prompt_architect import generate_v9_spec
from config import Config

PROTECTED_FILES = {
    "Example_Program.py",
    "__init__.py", 
    "base_skill.py"
}

def get_user_selection(options, prompt_text):
    if not options: return None
    # [Fix] 移除 sorted()，保留外部傳入的正確順序 (display_order)
    options = [o for o in options if o is not None]
    
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

def reset_skill_prompts(skill_ids):
    """
    [Fix] 使用空字串 "" 而非 None 來清空 Prompt。
    解決 sqlite3.IntegrityError: NOT NULL constraint failed
    """
    if not skill_ids: return
    try:
        SkillInfo.query.filter(SkillInfo.skill_id.in_(skill_ids)).update({SkillInfo.gemini_prompt: ""}, synchronize_session=False)
        db.session.commit()
        tqdm.write(f"🧹 已清空 {len(skill_ids)} 筆舊規格書，準備重新生成。")
    except Exception as e:
        tqdm.write(f"⚠️ 清空舊規格失敗: {e}")
        db.session.rollback()

def auto_patch_missing_functions(code_content, skill_id):
    """
    [V9.8.3 防呆補丁] 自動檢查並修復缺失的關鍵函式
    """
    # 1. 萬能轉接頭：如果 AI 寫了無參數的 generate()，強制改為支援參數
    if "def generate():" in code_content or "def generate() " in code_content:
        # 簡單字串替換，解決最常見的錯誤
        code_content = code_content.replace("def generate():", "def generate(level=1, **kwargs):")
        code_content = code_content.replace("def generate() ", "def generate(level=1, **kwargs) ")
    
    patches = []
    
    # 2. 檢查 generate 進入點 (若完全沒有 generate)
    if "def generate" not in code_content:
        # 尋找是否有類似 generate_number_line 這樣的變體
        import re
        alt_gen = re.findall(r'def (generate_[a-zA-Z0-9_]+)\(', code_content)
        if alt_gen:
            patches.append(f"\n# [Auto-Fix] Alias {alt_gen[0]} to generate")
            patches.append(f"generate = {alt_gen[0]}")
        else:
            # 如果真的什麼都沒寫
            patches.append("\n# [Auto-Fix] Emergency Fallback Generate")
            patches.append("def generate(level=1, **kwargs): return {'question_text': '題目生成失敗，請重新整理', 'correct_answer': 'N/A'}")

    # 3. 檢查 check 函式
    if "def check" not in code_content:
        patches.append("\n# [Auto-Fix] Emergency Fallback Check")
        patches.append("def check(u, c): return {'correct': False, 'result': '評分系統異常'}")

    if patches:
        tqdm.write(f"⚠️  {skill_id}: 偵測到函式缺失或簽章錯誤，已自動注入補丁代碼。")
        return code_content + "\n" + "\n".join(patches)
    
    return code_content

def run_expert_pipeline(skill_ids, arch_model, current_model):
    """
    執行完整的專家分工流程 (Phase 1 + Phase 2)
    """
    if not skill_ids: return
    
    # Step 0: 清空舊 Spec
    print("\n" + "="*50)
    print(f"🧹 [Step 0] 清空舊規格書...")
    print("="*50)
    reset_skill_prompts(skill_ids)

    # Step 1: Architect
    # --- Smart Tag Detection ---
    c_model = current_model.lower()
    target_tag = 'local_14b' # 預設標籤
    
    if any(x in c_model for x in ['gemini', 'gpt', 'claude']): 
        target_tag = 'cloud_pro' # 雲端強大模型使用此標籤
    elif '70b' in c_model or '32b' in c_model or '14b' in c_model: 
        target_tag = 'local_14b'
    elif 'phi' in c_model or '7b' in c_model or '8b' in c_model: 
        target_tag = 'edge_7b'
    
    print("\n" + "="*60)
    print(f"🧠 [Phase 1] V9 Architect Analysis (Model: {arch_model})")
    print(f"   Target Strategy: '{target_tag}' (Detected from Coder: {current_model})")
    print("="*60)
    
    arch_success_count = 0
    pbar_arch = tqdm(skill_ids, desc="Phase 1 (Architect)", unit="file", ncols=100)
    
    for skill_id in pbar_arch:
        pbar_arch.set_description(f"Planning: {skill_id}")
        
        # [V9.0 Upgrade] Use generate_v9_spec with target_tag strategy
        try:
            # [Fix] 確保 model_tag 傳入 target_tag (如 'cloud_pro')，architect_model 傳入實際模型名稱
            result = generate_v9_spec(skill_id, model_tag=target_tag, architect_model=arch_model)
            success = result.get('success', False)
        except Exception as e:
            tqdm.write(f"   ❌ {skill_id} Architect Error: {e}")
            success = False

        if success:
            arch_success_count += 1
    
    print(f"\n✅ Phase 1 完成: {arch_success_count}/{len(skill_ids)} 份教案已生成。\n")
    
    # Step 2: Coder
    print("="*50)
    print(f"💻 [Step 2] 啟動工程師批次實作 ({current_model})...")
    print("="*50)
    
    success_count = 0
    fail_count = 0
    
    pbar_code = tqdm(skill_ids, desc="Phase 2 (Coder)", unit="file", ncols=100)
    
    for skill_id in pbar_code:
        pbar_code.set_description(f"Coding: {skill_id}")
        
        # [Phase 2] Generate Code
        # We set force_architect_refresh=False because Phase 1 already generated the spec.
        # If Phase 1 failed, the Auto-Architect inside will try again as a fallback.
        result = auto_generate_skill_code(skill_id, queue=None, force_architect_refresh=False)
        
        is_ok = False
        msg = ""
        if isinstance(result, tuple):
            is_ok, msg = result
        else:
            is_ok = result
        
        if is_ok:
            success_count += 1
            tqdm.write(f"   ✅ {skill_id}: Success")
            
            # [V9.8.2] Post-Validation Patching
            # 因為 auto_generate_skill_code 已經寫入檔案，我們必須讀出來檢查並修補
            try:
                # 假設 SKILLS_DIR 與 app.py 同層級的 skills 資料夾
                # 這裡使用 project_root (全域變數) 組合路徑
                skill_path = os.path.join(project_root, 'skills', f"{skill_id}.py")
                if os.path.exists(skill_path):
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    patched_content = auto_patch_missing_functions(content, skill_id)
                    
                    if patched_content != content:
                        with open(skill_path, 'w', encoding='utf-8') as f:
                            f.write(patched_content)
                        tqdm.write(f"   🔧 {skill_id}: Patched successfully.")
            except Exception as e:
                 tqdm.write(f"   ❌ {skill_id} Patching Error: {e}")

        else:
            fail_count += 1
            tqdm.write(f"   ❌ {skill_id}: Failed ({msg})")

    print("\n" + "=" * 50)
    print(f"🎉 專家模式作業完成！")
    print(f"   成功: {success_count}")
    print(f"   失敗: {fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    app = create_app()
    
    SKILLS_DIR = os.path.join(app.root_path, 'skills')
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ 找不到技能目錄: {SKILLS_DIR}")
        sys.exit(1)

    with app.app_context():
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
        current_model = role_config.get('model', 'Unknown')
        
        arch_config = Config.MODEL_ROLES.get('architect', {})
        arch_model = arch_config.get('model', 'Unknown')

        print(f"🚀 開始同步資料庫與實體檔案 (v8.6.2)")
        print(f"🤖 工程師模型 (Coder): \033[1;36m{current_model}\033[0m") 
        print(f"🧠 架構師模型 (Architect): \033[1;35m{arch_model}\033[0m")
        
        # --- 1. 互動篩選 ---
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇課綱:")

        q_grade = db.session.query(distinct(SkillCurriculum.grade))
        if selected_curr: q_grade = q_grade.filter(SkillCurriculum.curriculum == selected_curr)
        grades = [r[0] for r in q_grade.order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")

        q_vol = db.session.query(distinct(SkillCurriculum.volume))
        if selected_curr: q_vol = q_vol.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_vol = q_vol.filter(SkillCurriculum.grade == selected_grade)
        volumes = [r[0] for r in q_vol.all()]
        selected_vol = get_user_selection(volumes, "請選擇冊別:")

        q_chap = db.session.query(distinct(SkillCurriculum.chapter))
        if selected_curr: q_chap = q_chap.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: q_chap = q_chap.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: q_chap = q_chap.filter(SkillCurriculum.volume == selected_vol)
        chapters = [r[0] for r in q_chap.all()]
        selected_chap = get_user_selection(chapters, "請選擇章節:")

        selected_skill_id = None
        if any([selected_curr, selected_grade, selected_vol, selected_chap]):
            q_skill = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).join(SkillCurriculum).filter(SkillInfo.is_active == True)
            if selected_curr: q_skill = q_skill.filter(SkillCurriculum.curriculum == selected_curr)
            if selected_grade: q_skill = q_skill.filter(SkillCurriculum.grade == selected_grade)
            if selected_vol: q_skill = q_skill.filter(SkillCurriculum.volume == selected_vol)
            if selected_chap: q_skill = q_skill.filter(SkillCurriculum.chapter == selected_chap)
            
            # [Update v8.6.2] 使用 display_order 進行排序
            skills_raw = q_skill.order_by(SkillCurriculum.display_order).all()
            skill_options = [f"{s.skill_id} | {s.skill_ch_name}" for s in skills_raw]
            
            if skill_options:
                selected_skill_str = get_user_selection(skill_options, "請選擇單一技能 (Optional):")
                if selected_skill_str:
                    selected_skill_id = selected_skill_str.split(' | ')[0].strip()

        is_full_scan = all(x is None for x in [selected_curr, selected_grade, selected_vol, selected_chap, selected_skill_id])

        # --- 2. 查詢目標技能 ---
        print("\n🔍 正在查詢目標技能...")
        query = db.session.query(SkillInfo.skill_id).join(SkillCurriculum).filter(SkillInfo.is_active == True)
        
        if selected_curr: query = query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: query = query.filter(SkillCurriculum.grade == selected_grade)
        if selected_vol: query = query.filter(SkillCurriculum.volume == selected_vol)
        if selected_chap: query = query.filter(SkillCurriculum.chapter == selected_chap)
        if selected_skill_id: query = query.filter(SkillInfo.skill_id == selected_skill_id)
        
        target_skill_ids = set(r[0] for r in query.all())

        # --- 3. 掃描實體檔案 ---
        files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
        file_skill_ids = set()
        for f in files:
            fname = os.path.basename(f)
            if fname not in PROTECTED_FILES:
                file_skill_ids.add(fname.replace('.py', ''))
        
        # --- 4. 計算差異 ---
        to_create = target_skill_ids - file_skill_ids
        existing_in_scope = target_skill_ids.intersection(file_skill_ids)
        to_delete = set()
        if is_full_scan:
            all_active_ids = set(r[0] for r in db.session.query(SkillInfo.skill_id).filter_by(is_active=True).all())
            to_delete = file_skill_ids - all_active_ids

        # --- 5. 顯示狀態 ---
        print(f"\n📊 [範圍分析結果]")
        print(f"   - 範圍內技能總數: {len(target_skill_ids)}")
        print(f"   - 缺失檔案 (需新增): {len(to_create)}")
        print(f"   - 現有檔案 (可更新): {len(existing_in_scope)}")
        if is_full_scan:
            print(f"   - 孤兒檔案 (需刪除): {len(to_delete)}")

        if not target_skill_ids and not to_delete:
            print("✅ 範圍內無技能或無需操作，結束。")
            sys.exit(0)

        print("\n請選擇操作模式:")
        print("   [1] 僅生成缺失檔案 (Safe Mode - 僅 Phase2生成Code)")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All - Phase2生成Code)")
        print("   [3] 補考模式：針對缺失檔案執行完整重建 (Fill Missing - Full Pipeline重新生成Prompt與Code)")
        print("   [4] 專家分工模式：全部重跑 (Auto-Reset Spec - Full Pipeline重新生成Prompt與Code)") 
        if to_delete:
            print("   [5] 清理孤兒檔案 (Delete Orphans)")
        
        mode = input("👉 請輸入選項: ").strip()
        
        list_to_process = sorted(list(set()))
        run_full_pipeline = False
        
        if mode == '1':
            list_to_process = sorted(list(to_create))
        elif mode == '2':
            list_to_process = sorted(list(to_create.union(existing_in_scope)))
        elif mode == '3':
            # Mode 3: 只對「缺失」的檔案跑完整流程
            list_to_process = sorted(list(to_create))
            run_full_pipeline = True
            print(f"\n🚀 [補考模式] 將對 {len(list_to_process)} 個缺失技能執行完整重建 (Architect + Coder)...")
        elif mode == '4':
            # Mode 4: 全部重跑完整流程
            list_to_process = sorted(list(to_create.union(existing_in_scope)))
            run_full_pipeline = True
            print(f"\n🚀 [專家模式] 將對 {len(list_to_process)} 個技能執行完整重建 (Architect + Coder)...")
        elif mode == '5' and to_delete:
            print("\n🗑️  正在清理孤兒檔案...")
            for skill_id in tqdm(to_delete, desc="Deleting"):
                try:
                    os.remove(os.path.join(SKILLS_DIR, f"{skill_id}.py"))
                except Exception as e:
                    print(f"   ❌ 刪除失敗: {e}")
            print("✅ 清理完成。")
            sys.exit(0)
        else:
            print("❌ 無效選項或無操作。")
            sys.exit(0)

        if not list_to_process:
            print("✅ 沒有需要處理的檔案。")
            sys.exit(0)

        # --- [警示] ---
        count = len(list_to_process)
        base_time = 0.5 
        if run_full_pipeline: base_time = 3.5 
        
        total_est_min = count * base_time
        
        print(f"\n⚠️  [注意] 準備開始")
        print(f"   數量: {count} 題")
        print(f"   預估總耗時: {total_est_min:.1f} 分鐘")
        confirm = input("   確定要繼續嗎? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消。")
            sys.exit(0)

        # --- 6. 執行生成 ---
        if run_full_pipeline:
            # 呼叫封裝好的專家流程
            run_expert_pipeline(list_to_process, arch_model, current_model)
        else:
            # 只跑 Code Gen (Phase 2)
            print(f"\n🚀 開始生成任務 (Code Gen Only)... (Log 將顯示於下方)\n")
            success_count = 0
            fail_count = 0
            
            pbar = tqdm(list_to_process, desc="Progress", unit="file", ncols=100)
            
            for skill_id in pbar:
                pbar.set_description(f"Processing: {skill_id}")
                start_dt = datetime.now()
                
                try:
                    result = auto_generate_skill_code(skill_id, queue=None)
                    
                    if isinstance(result, tuple):
                        is_ok, msg = result
                    else:
                        is_ok = result
                        msg = ""
                    
                    end_dt = datetime.now()
                    duration = (end_dt - start_dt).total_seconds()

                    if is_ok:
                        success_count += 1
                        tqdm.write(f"   ✅ {skill_id} ({duration:.1f}s)")
                    else:
                        fail_count += 1
                        tqdm.write(f"   ❌ {skill_id} ({duration:.1f}s) - {msg}")

                except KeyboardInterrupt:
                    print("\n⚠️  使用者強制中斷！")
                    break
                except Exception as e:
                    fail_count += 1
                    tqdm.write(f"❌ 異常 {skill_id}: {e}")
            
            print("\n" + "=" * 50)
            print(f"🎉 作業完成！")
            print(f"   成功: {success_count}")
            print(f"   失敗: {fail_count}")
            print("=" * 50)