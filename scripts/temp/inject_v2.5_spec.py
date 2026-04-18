import sys
import os

# Ensure we can import the app modules
sys.path.append(os.getcwd())

from app import app
from models import db, SkillGenCodePrompt

USER_SPEC = r"""# Python Implementation Plan for Junior Coder AI

**Problem Type**: `jh_數學1上_DistanceBetweenTwoPointsOnNumberLine` (數線上兩點的距離)

## 🎯 GOAL 1: ADAPTIVE SCENARIO (絕對指令)
- **純計算模式**：此技能為純代數運算，**嚴禁導入任何 Matplotlib 或繪圖邏輯**。
- **Return Requirement**：`image_base64` 必須設為 `None`。

## 🛠️ ENGINEERING ROBUSTNESS (嚴格規範)
1. **單題生成**：主函式必須命名為 `generate(level=1)`，且必須回傳「單一字典」，禁止產出題目列表。
2. **字串安全**：嚴禁在 LaTeX 算式中使用 f-string 的雙括號。請務必使用 `template.replace()` 或 `.format()` 注入變數。
3. **返回格式**：必須包含以下鍵值：
   - `question_text`: 包含 LaTeX 的問題描述 (繁體中文)。
   - `correct_answer`: 純文字/數字答案，供系統比對。
   - `answer`: 同 `correct_answer`。
   - `image_base64`: None。

## 🛡️ NUMERICAL GUARDRAILS (數值邏輯)
- 座標範圍：隨機生成 -20 到 20 之間的整數或一位小數。
- 多樣性：必須涵蓋「同號座標」、「異號座標」、「含零座標」以及「兩點重合 (距離 0)」等情境。
- 距離公式：計算 `abs(A - B)`。

## 📝 實作範例結構：
```python
def generate(level=1):
    # 1. 隨機生成 A, B
    # 2. 計算 distance = abs(A - B)
    # 3. 使用 replace 處理 LaTeX：
    template = "在數線上，點 $A$ 的座標為 ${a}$，點 $B$ 的座標為 ${b}$，求 $\\overline{AB}$ 的長度。\\n(答案格式：請填入數字)"
    question = template.replace("{a}", str(a)).replace("{b}", str(b))
    return {
        "question_text": question,
        "correct_answer": str(round(distance, 2)),
        "image_base64": None,
        "problem_type": "數線上兩點的距離"
    }
```"""

def inject_prompt():
    skill_id = "jh_數學1上_DistanceBetweenTwoPointsOnNumberLine"
    target_tag = "cloud_pro" # Default target for this instruction
    
    with app.app_context():
        # Find existing prompt or create new one
        prompt = SkillGenCodePrompt.query.filter_by(
            skill_id=skill_id, 
            model_tag=target_tag
        ).first()
        
        if not prompt:
            print(f"Creating NEW V9 Prompt for {skill_id} ({target_tag})")
            prompt = SkillGenCodePrompt(
                skill_id=skill_id,
                model_tag=target_tag,
                is_active=True,
                version=1
            )
            db.session.add(prompt)
        
        prompt.user_prompt_template = USER_SPEC
        prompt.updated_at = db.func.now()
        prompt.version += 1
        
        db.session.commit()
        print(f"✅ Successfully injected V9 Spec for {skill_id}. Version: {prompt.version}")

if __name__ == "__main__":
    inject_prompt()
