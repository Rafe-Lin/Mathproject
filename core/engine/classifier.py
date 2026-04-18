# -*- coding: utf-8 -*-
import os
import re
import json
from core.ai_wrapper import get_ai_client, call_ai_with_retry
from config import Config

class SkillClassifier:
    """
    SkillClassifier 負責將使用者輸入的題目 (文字或影像) 對應到系統中的 agent_skill。
    """
    def __init__(self, model_role='classifier'):
        self.client = get_ai_client(model_role)
        self.skills = self._discover_skills()

    def _discover_skills(self):
        """
        動態掃描 agent_skills 目錄。
        優先讀取各子目錄的 skill.json["skill_id"] 作為技能 ID；
        若 skill.json 不存在則退回目錄名稱。
        """
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        skills_dir = os.path.join(project_root, "agent_skills")
        skills = []
        if os.path.exists(skills_dir):
            for d in os.listdir(skills_dir):
                dir_path = os.path.join(skills_dir, d)
                if not os.path.isdir(dir_path):
                    continue
                manifest_path = os.path.join(dir_path, "skill.json")
                if os.path.isfile(manifest_path):
                    try:
                        with open(manifest_path, encoding="utf-8") as fh:
                            meta = json.load(fh)
                        sid = meta.get("skill_id", "").strip()
                        skills.append(sid if sid else d)
                        continue
                    except Exception:
                        pass
                skills.append(d)
        return sorted(skills)

    def _get_system_prompt(self):
        """
        構建分類專用的 System Prompt。
        """
        skills_str = "\n".join([f"- {s}" for s in self.skills])
        return f"""你是一個數學題目分類專家。
你的任務是閱讀使用者提供的「LaTeX 數學公式或題目文字」，並從下方的「技能清單」中選擇一個最符合該題目的技能名稱。

【技能清單】
{skills_str}

【分類規則】
1. 只輸出技能名稱，不要有任何其他解釋或標點符號。
2. 如果題目完全不屬於清單中的任何一項，請輸出 "Unknown"。
3. 優先根據數學結構判斷（例如：看到 \\sqrt 或根號選 FourOperationsOfRadicals）。

請開始分類："""

    def classify(self, input_text=None, image_path=None):
        """
        進行分類。
        Returns:
            str: 識別出的技能名稱或 "Unknown"
        """
        if not input_text and not image_path:
            return "Unknown"

        prompt = self._get_system_prompt()
        if input_text:
            prompt += f"\n\n題目內容：{input_text}"
        
        try:
            # --- 修改點：改為呼叫本地 Qwen3 ---
            # 參考 scaler.py 中的 _call_ai 邏輯
            from core.code_generator import _call_ai
            from config import Config
            
            # 使用環境中已定義的 qwen3-8b 配置，並特別限制它的輸出字數（分類不需要長文）
            model_config = Config.CODER_PRESETS.get(Config.DEFAULT_CODER_PRESET).copy()
            model_config['max_tokens'] = 120 # 強制截斷思考區塊，防止無限生成卡死超過1分鐘
            
            print(f">>> 🧠 本地 Qwen3 正在進行技能 DNA 比對...")
            # 呼叫本地推理
            raw_response, _, _, _ = _call_ai(prompt, model_config=model_config)
            
            # 2. 清洗結果 (移除思考區塊與標點)
            import re
            # 移除 <think> 標籤內容 (Qwen3-8B-Instruct 常見輸出)
            clean_res = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
            
            # 🚨 加固點 2：只提取英文字母與數字 (Skill ID 的標準格式)
            # 避免 AI 輸出 "結果是：RadicalOps" 或 "Skill: RadicalOps."
            match = re.search(r'[a-zA-Z0-9_]{5,}', clean_res) # 假設 Skill ID 至少 5 個字
            result = match.group(0) if match else clean_res
            result = re.sub(r'[`"\'\s]', '', result)
            
            # 3. 驗證與回傳 (保持原有的模糊比對邏輯)
            if result in self.skills:
                return result
            for s in self.skills:
                if s.lower() in result.lower():
                    return s
            return "Unknown"
                
        except Exception as e:
            print(f"本地分類失敗: {e}")
            return "Unknown"

if __name__ == "__main__":
    # 簡單測試
    classifier = SkillClassifier()
    print(f"可用技能: {classifier.skills}")
    test_q = "計算根號 2 加上根號 8 的值。"
    print(f"測試題目: {test_q}")
    print(f"分類結果: {classifier.classify(input_text=test_q)}")
