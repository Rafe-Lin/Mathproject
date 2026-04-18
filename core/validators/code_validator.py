# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/validators/code_validator.py
# Version: V2.1 (Refactored from code_generator.py)
# Last Updated: 2026-01-30
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   Python 代碼驗證和錯誤分類工具
#   提供兩個核心功能：
#   1. validate_python_code: 驗證生成的 Python 代碼是否可執行
#   2. categorize_error: 將錯誤訊息分類為 SyntaxError, FormatError, RuntimeError
#
# [Logic Flow]:
#   1. validate_python_code -> 在受控環境中執行代碼 -> 返回 (是否成功, 錯誤訊息)
#   2. categorize_error -> 分析錯誤訊息文字 -> 返回錯誤類別字串
#
# [Dependencies]:
#   - ast, operator, re, math, random, Fraction (用於執行環境)
# ==============================================================================

import ast
import operator
import re
import math
import random
from fractions import Fraction


def categorize_error(error_msg):
    """
    錯誤分類器
    
    將錯誤訊息分類為三大類：
    - SyntaxError: 語法錯誤
    - FormatError: 格式錯誤（如 list 操作錯誤）
    - RuntimeError: 運行時錯誤
    
    Args:
        error_msg (str): 錯誤訊息
    
    Returns:
        str: 錯誤類別 ('SyntaxError', 'FormatError', 'RuntimeError') 或 None
    
    Examples:
        >>> categorize_error("SyntaxError: invalid syntax")
        'SyntaxError'
        >>> categorize_error("IndexError: list index out of range")
        'FormatError'
        >>> categorize_error("NameError: name 'x' is not defined")
        'RuntimeError'
    """
    if not error_msg or error_msg == "None":
        return None
    
    err_low = error_msg.lower()
    
    # 語法錯誤
    if "syntax" in err_low:
        return "SyntaxError"
    
    # 格式錯誤（列表、索引等）
    if "list" in err_low:
        return "FormatError"
    
    # 其他運行時錯誤
    return "RuntimeError"


def validate_python_code(code_str):
    """
    驗證生成的 Python 代碼是否可執行
    
    使用 exec() 嘗試執行代碼，檢查是否有語法或運行時錯誤。
    提供詳細的錯誤提示以幫助診斷問題。
    
    Args:
        code_str (str): 待驗證的 Python 代碼字符串
    
    Returns:
        tuple: (is_valid, error_msg)
            - is_valid (bool): 代碼是否有效
            - error_msg (str): 錯誤訊息（成功時為 "Success"）
    
    Notes:
        - 代碼在隔離的命名空間中執行（提供 Fraction, random, math, re, ast, operator）
        - PERFECT_UTILS 中的函數定義已包含在 code_str 中
        - 過濾掉 "break outside loop" 錯誤（可能是 AST Healer 導致的假陽性）
    
    Examples:
        >>> code = "def generate(): return {'question_text': 'test', 'answer': '42', 'mode': 1}"
        >>> is_valid, msg = validate_python_code(code)
        >>> is_valid
        True
    """
    try:
        # [V46.1 Fix] 修正 Host 端 NameError
        # 我們不需要手動傳入 safe_eval，因為 code_str (生成的代碼)
        # 裡面已經透過 PERFECT_UTILS 注入了 safe_eval 的定義。
        # exec 執行時會自然地先定義函式，再執行後面的邏輯。
        
        exec(code_str, {
            'Fraction': Fraction, 
            'random': random, 
            'math': math, 
            're': re,
            'ast': ast,
            'operator': operator
        })
        return True, "Success"
    
    except Exception as e:
        # [Debug] 詳細錯誤輸出
        error_msg = f"{type(e).__name__}: {str(e)}"
        
        # 過濾掉一些非代碼邏輯的干擾訊息
        if "break outside loop" in error_msg:
            return False, error_msg

        print(f"[Validation Failed] Execution error: {error_msg}")
        
        # Provide diagnostic hints
        if "local variable" in error_msg and "referenced before assignment" in error_msg:
            print(f"   Hint: This may be due to uninitialized variables after while True circuit breaker.")
        elif "safe_eval" in error_msg:
            print(f"   Hint: Check if PERFECT_UTILS is included at the beginning of generated code.")
        
        return False, error_msg
