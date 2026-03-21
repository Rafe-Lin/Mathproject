# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/validators/syntax_validator.py
功能說明 (Description): Python 語法驗證器
執行語法 (Usage): from core.validators import SyntaxValidator
版本資訊 (Version): V2.0 (Refactored from code_generator.py::validate_python_code)
更新日期 (Date): 2026-01-30
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import ast
import logging

logger = logging.getLogger(__name__)

class SyntaxValidator:
    """
    Python 語法驗證器
    檢查代碼是否可以被 Python 解析
    """
    
    def validate(self, code_str: str) -> tuple:
        """
        驗證 Python 語法
        
        Args:
            code_str: 代碼字串
            
        Returns:
            tuple: (是否通過, 錯誤訊息)
        """
        # 臨時實現：調用舊函數
        from core.code_generator import validate_python_code
        is_valid, error_msg = validate_python_code(code_str)
        
        if is_valid:
            logger.info("✅ 語法驗證通過")
        else:
            logger.warning(f"❌ 語法驗證失敗: {error_msg}")
        
        return is_valid, error_msg
