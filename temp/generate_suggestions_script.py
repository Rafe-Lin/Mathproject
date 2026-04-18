import pandas as pd
import google.generativeai as genai
import time
import random

# ================= 設定區 =================
# 1. 請在此填入你的 Gemini API Key
GOOGLE_API_KEY = "AIzaSyAgLGBxMt1CuA49Zfl094cGLRu9Xi-s_i0"

# 2. 檔案路徑 (維持您上次提供的路徑)
INPUT_FILE_PATH = r"C:\Mathproject\datasource\data source_課程資料\skills_info\技高\skills_info\skills_info_數學C2.xlsx"
OUTPUT_FILE_PATH = r"C:\Mathproject\datasource\data source_課程資料\skills_info\技高\skills_info\skills_info_數學C2_short.xlsx"

# 3. 設定 Gemini 模型 (繼續使用速度最快的 2.5 Flash)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# ================= 核心功能函數 =================

def generate_student_prompts(unit_name, description):
    """
    根據單元名稱和描述，生成三個學生可能會問的 AI 提示詞。
    """
    if pd.isna(description) or pd.isna(unit_name):
        return ["", "", ""]

    # === Prompt 修改重點 ===
    # 1. 加入字數限制 (18字)
    # 2. 要求簡潔有力
    prompt = f"""
    你是一位高中一年級學生，正看著數學題目發愁。
    學習單元：「{unit_name}」。
    內容描述：「{description}」。
    
    請生成 3 個「問 AI 助教」的短句。
    
    【嚴格限制】：
    1. **每個句子必須在 18 個中文字以內** (越短越好)。
    2. **不要囉唆**，不要用「請問」、「我想知道」開頭，直接問重點。
    3. 語氣要像學生，自然、口語。
    
    【問題方向】：
    1. 第一問：概念/定義 (例如：什麼是判別式？)
    2. 第二問：解題技巧/SOP (例如：這題要先畫圖嗎？)
    3. 第三問：易錯點/陷阱 (例如：根號內可以是負的嗎？)
    
    格式：回傳三個句子，用「|||」隔開。
    """

    # === 自動重試機制 ===
    max_retries = 5
    base_wait_time = 5

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            questions = text.split('|||')
            
            cleaned_questions = [q.strip() for q in questions if q.strip()]
            
            # 檢查字數，如果 AI 不小心吐太長，強制截斷 (雖然 Prompt 有講，但防呆一下)
            final_questions = []
            for q in cleaned_questions:
                if len(q) > 25: # 如果真的太長
                    q = q[:24] + "..." # 強制截斷
                final_questions.append(q)

            while len(final_questions) < 3:
                final_questions.append("這題重點是什麼？") # 預設短句
            
            return final_questions[:3]

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Resource exhausted" in error_msg or "503" in error_msg:
                wait_time = base_wait_time * (attempt + 1) + random.uniform(0, 3)
                print(f"⚠️ 速度太快 (429)，休息 {wait_time:.1f} 秒... (重試 {attempt + 1})")
                time.sleep(wait_time)
            else:
                print(f"❌ 生成失敗 ({unit_name}): {error_msg}")
                return ["Error", "Error", "Error"]
    
    print(f"❌ 放棄 ({unit_name})")
    return ["Error", "Error", "Error"]

# ================= 主程式邏輯 =================

def main():
    print(f"正在讀取: {INPUT_FILE_PATH}")
    try:
        df = pd.read_excel(INPUT_FILE_PATH)
        
        COL_INDEX_NAME = 2  # C欄
        COL_INDEX_DESC = 4  # E欄
        
        if len(df.columns) <= COL_INDEX_DESC:
            print("❌ 錯誤：Excel 欄位不足。")
            return

        print(f"鎖定：名稱(C)='{df.columns[COL_INDEX_NAME]}', 描述(E)='{df.columns[COL_INDEX_DESC]}'")
        print("-" * 30)

        k_col, l_col, m_col = [], [], []
        total_rows = len(df)
        
        print(f"🚀 啟動短句模式！共 {total_rows} 筆...")

        for index, row in df.iterrows():
            name = row.iloc[COL_INDEX_NAME]
            desc = row.iloc[COL_INDEX_DESC]
            
            print(f"處理 ({index + 1}/{total_rows}): {name}")

            prompts = generate_student_prompts(name, desc)
            
            k_col.append(prompts[0])
            l_col.append(prompts[1])
            m_col.append(prompts[2])
            
            # 為了速度，設為 1 秒，若遇到 429 會自動變慢
            time.sleep(1.0) 

        df['K_AI_Prompt(概念)'] = k_col
        df['L_AI_Prompt(技巧)'] = l_col
        df['M_AI_Prompt(易錯)'] = m_col

        print("-" * 30)
        print("正在儲存...")
        df.to_excel(OUTPUT_FILE_PATH, index=False)
        print(f"✅ 完成！短句版已儲存至：\n{OUTPUT_FILE_PATH}")

    except FileNotFoundError:
        print("❌ 錯誤：找不到檔案。")
    except Exception as e:
        print(f"❌ 未預期錯誤：{e}")

if __name__ == "__main__":
    main()