# -*- coding: utf-8 -*-
import os
import time
from core.engine.classifier import SkillClassifier
from core.engine.scaler import AdaptiveScaler

class MathEngine:
    """
    MathEngine 是系統的總對外窗口。
    流程：輸入 -> 識別技能 (Classifier) -> 生成練習場 (Scaler)
    """
    def __init__(self):
        self.classifier = SkillClassifier()
        self.scaler = AdaptiveScaler()

    def generate_practice_set(self, input_text=None, image_path=None, count=5, model_id=None, ablation_mode=False, skill_name=None):
        """
        根據輸入生成依照例題仿製的練習題。
        """
        print("\n" + "="*50)
        mode_label = "🔥 原生 AI 模擬 (Ab1)" if ablation_mode else "🛡️ Math Project 強防護模式 (Ab3)"
        print(f"🤖 Math Learning Engine: 正在處理您的請求... [{mode_label}]")
        print("="*50)
        
        # 1. 識別技能
        start_time = time.time()
        if not skill_name:
            skill_name = self.classifier.classify(input_text=input_text, image_path=image_path)
        
        if skill_name == "Unknown":
            return {
                "success": False,
                "error": "無法識別題目類型，請提供更清晰的描述或照片。"
            }
            
        print(f"[OK] 識別完成: [ {skill_name} ] (耗時: {time.time()-start_time:.1f}s)")
        
        # 2. 為特定題型生成題目
        try:
            # Fallback for model_id compatibility
            kwargs = {}
            if model_id is not None:
                kwargs['model_id'] = model_id
                
            if count > 5:
                # 判斷大於 5 題就使用 batch 模式
                response = self.scaler.generate_batch(skill_name, input_text, n=count, ablation_mode=ablation_mode, **kwargs)
            else:
                response = self.scaler.generate_custom_problems(skill_name, input_text, count=count, ablation_mode=ablation_mode, **kwargs)
                
            problems = response.get("problems", [])
            debug_meta = response.get("debug_meta", {})
            ab2_result = response.get("ab2_result")
            
        except Exception as e:
             return {
                "success": False,
                "error": str(e)
            }
        
        return {
            "success": True,
            "skill": skill_name,
            "original_input": input_text or "[Image]",
            "problems": problems,
            "debug_meta": debug_meta,
            "ab2_result": ab2_result
        }

if __name__ == "__main__":
    # Demo 測試
    engine = MathEngine()
    
    # 範例：使用者提供一題多項式加法
    user_input = "若 (2x+1) + P = 5x-3，求 P。"
    print(f"使用者輸入: {user_input}")
    
    output = engine.generate_practice_set(input_text=user_input)
    
    if output["success"]:
        print(f"\n[RECOMMEND] 推薦練習場：{output['skill']}")
        for i, data in enumerate(output["problems"]):
            print(f"--- [題目 {i+1}] ---")
            if "error" in data:
                print(f"生成失敗: {data['error']}")
            else:
                print(f"Q: {data.get('question_text', '')}")
                print(f"A: {data.get('correct_answer', '')}")
    else:
        print(f"[ERR] 錯誤: {output['error']}")
