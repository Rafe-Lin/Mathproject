# -*- coding: utf-8 -*-
# ==============================================================================
# ID: enrich_skills.py
# Version: V1.0.0 (Skill Prompt Enrichment)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   掃描資料庫 skills_info 中缺少 suggested_prompt 的技能，依課本例題上下文呼叫模型，
#   批次產生繁中、精簡的引導語（功文風格），寫回資料庫供前台練習使用。
#
# [Database Schema Usage]:
#   讀寫 skills_info、關聯 curriculum；讀取 textbook example 作為生成上下文。
#
# [Logic Flow]:
#   1. 互動選擇課綱/章節範圍。
#   2. 查詢待補技能並組裝提示。
#   3. 呼叫 AI 寫入 suggested_prompt 欄位。
# ==============================================================================
import sys
import os
import json
import time
from tqdm import tqdm  # 如果沒安裝 tqdm，請執行 pip install tqdm
import re
from sqlalchemy import distinct, text

# 1. 設定路徑以匯入專案模組 (指回專案根目錄)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, SkillInfo, TextbookExample, SkillCurriculum
# 使用專案統一的 AI 介面
from core.ai_analyzer import get_model

def get_user_selection(options, prompt_text):
    """
    通用互動函式：讓使用者從選項中選擇，或輸入 0 全選
    """
    if not options:
        return None
    
    # 去除 None 值並排序
    options = sorted([o for o in options if o is not None])
    
    print(f"\n{prompt_text}")
    print("   [0] ALL (全部處理)")
    for i, opt in enumerate(options, 1):
        print(f"   [{i}] {opt}")
        
    while True:
        try:
            choice = input("👉 請選擇 (輸入數字): ").strip()
            if choice == '0':
                return None  # 代表全選
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("❌ 輸入無效，請重試。")
        except ValueError:
            print("❌ 請輸入數字。")

def generate_prompts(model, skill: SkillInfo, examples: list[TextbookExample]) -> dict:
    """
    呼叫 Gemini 生成 3 個學生視角的點擊式問句。
    [名師引導版 - 最終修訂]
    
    修正重點：
    1. [新增] 強制禁止 Markdown 粗體/斜體格式，確保前端顯示乾淨。
    2. 保持解題三部曲邏輯 (啟動 -> 策略 -> 檢查)。
    """
    
    # 1. 讀取 Context
    skill_code_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills', f'{skill.skill_id}.py')
    code_content = None
    
    if os.path.exists(skill_code_path):
        try:
            with open(skill_code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception:
            pass 

    if code_content:
        context_source = "Python 題目生成程式碼"
        context_content = f"```python\n{code_content}\n```"
    else:
        context_source = "課本例題"
        context_content = "\n---\n".join([
            f"例題 {i+1}:\n題目：{ex.problem_text}\n詳解：{ex.detailed_solution}"
            for i, ex in enumerate(examples)
        ])

    JSON_SCHEMA = 'prompt_1, prompt_2, prompt_3' 

    # 設定 System Prompt
    SYSTEM_PROMPT = f"""
你是一位經驗豐富、擅長引導低成就學生的數學老師。
請根據提供的單元資料，設計 3 個**「學生解題當下最該問自己的問題」**。

目標：讓學生點擊這些按鈕時，像是有個老師在旁邊輕聲提醒他思考方向。

---
【強制輸出要求】
1. 輸出格式：純 JSON 物件 (keys: {JSON_SCHEMA})。
2. 語氣：**學生的內心獨白** (以「我」為主詞)。
3. 字數：25 字以內 (短而有力)。
4. **格式禁令**：**嚴禁使用 Markdown 粗體 (**...**) 或斜體 (*...*)**。按鈕文字必須是純文字。
5. **LaTeX**：數學符號用 `$` 包覆 (例如 $x^2$)。
6. **關鍵字**：請從資料中提取專有名詞或概念填入問題。

---
目標技能描述: {skill.description}
[資料來源: {context_source}]
{context_content}

---
請生成以下解題三部曲：

1. **prompt_1 (啟動與聚焦 - Start)**: 
   - **如果是有專有名詞的題目**：問定義。 (如：什麼是『判別式』？)
   - **如果是應用題**：問題目目標。 (如：題目給這些數字，是要我求什麼？)
   - **如果是計算題**：問運算規則。 (如：看到絕對值，第一步要先做什麼？)
   - 【通用框架】**「這題提到的『[關鍵字]』是什麼意思？第一步該看哪裡？」**

2. **prompt_2 (策略與工具 - Method)**: 
   - 學生需要知道「用什麼招式」。
   - 【框架】**「這種題型是要直接『[某種運算]』，還是要先『列方程式』？」**
   - 或 **「有沒有什麼『口訣』或『固定步驟』可以解這題？」**

3. **prompt_3 (反思與檢查 - Check)**: 
   - 養成驗算習慣，避開常見陷阱。
   - 【框架】**「算出來的答案，有沒有符合『[題目特殊要求]』？」**
   - 或 **「最後一步，我是不是忘了檢查『[常見錯誤點，如正負號/單位]』？」**
"""

    try:
        response = model.generate_content(SYSTEM_PROMPT)
        text = response.text.strip()
        
        # 清理 Markdown Code Block 標記
        if text.startswith("```"):
            text = re.sub(r"^```json\s*|^```\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 嘗試修復 LaTeX 跳脫字元問題
            fixed_text = re.sub(r'(?<!\\)\\(?![u"\\/bfnrt])', r'\\\\', text)
            try:
                return json.loads(fixed_text)
            except json.JSONDecodeError:
                return None
                
    except Exception as e:
        print(f"   ⚠️ API 呼叫錯誤: {e}")
        return None

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # [CRITICAL FIX] 啟用 WAL 模式以支援高併發寫入，防止資料庫壞檔
        try:
            with db.engine.connect() as connection:
                connection.execute(text("PRAGMA journal_mode=WAL"))
            print("✅ SQLite WAL 模式已啟用 (防止資料庫鎖死與損壞)")
        except Exception as e:
            print(f"⚠️ 無法啟用 WAL 模式: {e}")
        print("🚀 開始為技能補充 AI 提示詞 (Enrich Skills - Interactive Mode)...")
        
        try:
            model = get_model()
        except Exception as e:
            print(f"❌ 無法初始化 AI 模型: {e}")
            sys.exit(1)

        # ==========================================
        # 1. 階層篩選 (Hierarchical Filtering)
        # ==========================================
        base_query = db.session.query(SkillCurriculum)

        # Level 1: Curriculum
        curriculums = [r[0] for r in db.session.query(distinct(SkillCurriculum.curriculum)).order_by(SkillCurriculum.curriculum).all()]
        selected_curr = get_user_selection(curriculums, "請選擇要處理的課綱:")
        if selected_curr:
            base_query = base_query.filter(SkillCurriculum.curriculum == selected_curr)

        # Level 2: Grade
        grades = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.grade)).order_by(SkillCurriculum.grade).all()]
        selected_grade = get_user_selection(grades, "請選擇年級:")
        if selected_grade:
            base_query = base_query.filter(SkillCurriculum.grade == selected_grade)

        # Level 3: Volume
        volumes = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.volume)).order_by(SkillCurriculum.volume).all()]
        selected_volume = get_user_selection(volumes, "請選擇冊別:")
        if selected_volume:
            base_query = base_query.filter(SkillCurriculum.volume == selected_volume)

        # Level 4: Chapter
        chapters = [r[0] for r in base_query.with_entities(distinct(SkillCurriculum.chapter)).order_by(SkillCurriculum.chapter).all()]
        selected_chapter = get_user_selection(chapters, "請選擇章節:")
        if selected_chapter:
            base_query = base_query.filter(SkillCurriculum.chapter == selected_chapter)

        # ==========================================
        # 2. 準備處理清單
        # ==========================================
        final_query = db.session.query(SkillInfo).join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id).filter(SkillInfo.is_active == True)
        
        # 再次應用篩選條件以確保正確對應到 SkillInfo
        if selected_curr: final_query = final_query.filter(SkillCurriculum.curriculum == selected_curr)
        if selected_grade: final_query = final_query.filter(SkillCurriculum.grade == selected_grade)
        if selected_volume: final_query = final_query.filter(SkillCurriculum.volume == selected_volume)
        if selected_chapter: final_query = final_query.filter(SkillCurriculum.chapter == selected_chapter)

        skills_to_process = final_query.distinct().all()
        total = len(skills_to_process)
        print(f"\n📊 根據您的篩選，共找到 {total} 個技能範圍。\n")
        
        if total == 0:
            print("✅ 無需處理。")
            sys.exit(0)

        # ==========================================
        # 3. 模式選擇 (Mode Selection)
        # ==========================================
        print("請選擇執行模式：")
        print("   [1] 僅生成缺失檔案 (Safe Mode) - 檢查 suggested_prompt_2 是否為空")
        print("   [2] 強制重新生成範圍內所有檔案 (Overwrite All)")
        
        mode = None
        while True:
            choice = input("👉 請選擇 (1 或 2): ").strip()
            if choice in ['1', '2']:
                mode = choice
                break
            print("❌ 輸入無效，請輸入 1 或 2。")

        # ==========================================
        # 4. 執行生成
        # ==========================================
        count_processed = 0
        count_skipped = 0

        for skill in tqdm(skills_to_process, desc="處理進度"):
            
            # [邏輯檢查] 根據模式決定是否跳過
            if mode == '1': # Safe Mode
                # 如果 suggested_prompt_2 已經有內容，則跳過
                if skill.suggested_prompt_2 and skill.suggested_prompt_2.strip():
                    count_skipped += 1
                    continue
            
            # 若為 Overwrite 模式，或 Safe Mode 且欄位為空，則繼續執行
            
            # 取得例題上下文
            examples = db.session.query(TextbookExample).filter_by(skill_id=skill.skill_id).limit(2).all()
            
            # 生成提示詞
            prompts = generate_prompts(model, skill, examples)
            
            if prompts:
                try:
                    skill.suggested_prompt_1 = prompts.get('prompt_1')
                    skill.suggested_prompt_2 = prompts.get('prompt_2')
                    skill.suggested_prompt_3 = prompts.get('prompt_3')
                    
                    db.session.commit()
                    count_processed += 1
                except Exception as e:
                    db.session.rollback()
                    print(f"寫入 DB 失敗: {e}")
            
            # 避免 API Rate Limit
            time.sleep(1)

        print(f"\n✨ 全部作業完成！")
        print(f"   - 實際處理/更新: {count_processed} 個")
        print(f"   - 跳過 (原本已有內容): {count_skipped} 個")