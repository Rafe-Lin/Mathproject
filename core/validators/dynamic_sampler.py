# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/validators/dynamic_sampler.py
功能說明 (Description): 動態採樣驗證器，執行代碼並驗證輸出
執行語法 (Usage): from core.validators import DynamicSampler
版本資訊 (Version): V2.0 (Refactored from code_generator.py)
更新日期 (Date): 2026-01-30
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import logging

logger = logging.getLogger(__name__)

class DynamicSampler:
    """
    動態採樣驗證器
    執行生成的代碼並驗證輸出正確性
    """
    
    def __init__(self, iterations=3):
        """
        Args:
            iterations: 採樣次數（預設 3 次）
        """
        self.iterations = iterations
    
    def validate(self, code_str: str, iterations=None) -> tuple:
        """
        執行動態採樣驗證
        
        Args:
            code_str: 代碼字串
            iterations: 採樣次數（可覆蓋初始化值）
            
        Returns:
            tuple: (是否通過, 錯誤訊息)
        """
        iterations = iterations or self.iterations
        
        try:
            namespace = {}
            exec(code_str, namespace)
            
            generate_func = namespace.get('generate')
            if not generate_func:
                return False, "找不到 generate() 函數"
            
            # 執行多次採樣
            for i in range(iterations):
                try:
                    result = generate_func(level=4)
                    
                    # 基本驗證
                    if not isinstance(result, dict):
                        return False, f"第 {i+1} 次採樣：返回值不是 dict"
                    
                    if 'question_text' not in result:
                        return False, f"第 {i+1} 次採樣：缺少 question_text"
                    
                    if 'answer' not in result:
                        return False, f"第 {i+1} 次採樣：缺少 answer"
                    
                except Exception as e:
                    return False, f"第 {i+1} 次採樣失敗: {str(e)}"
            
            logger.info(f"✅ 動態採樣通過（{iterations} 次）")
            return True, ""
            
        except Exception as e:
            error_msg = f"動態採樣執行失敗: {str(e)}"
            logger.warning(f"❌ {error_msg}")
            return False, error_msg
