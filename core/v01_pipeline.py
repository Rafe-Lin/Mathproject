# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/v01_pipeline.py
# Version: v0.1 Pipeline
# Last Updated: 2026-01-29
# Author: Math AI Research Team
#
# [Description]:
#   v0.1 獨立管道模組，實現完整的 Architect → Coder → Healer → Verify 流程
#   不修改舊有的 code_generator.py，完全獨立
#
#   包含：
#   - 數據庫查詢函數
#   - 代碼提取/修復/執行
#
# ==============================================================================

import re
import random
import math
from fractions import Fraction

from core.architect_v01 import ArchitectV01

try:
    from models import db, TextbookExample
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def query_textbook_example(example_id):
    """
    從數據庫查詢課本例題
    
    Args:
        example_id: 例題 ID（整數），或 skill_id（字符串）
    
    Returns:
        dict: {
            'id': int,
            'skill_id': str,
            'problem_text': str,
            'solution': str,
            'difficulty': int,
            ...
        }
    
    如果數據庫不可用，返回 None
    """
    
    if not DATABASE_AVAILABLE:
        return None
    
    try:
        if isinstance(example_id, int):
            # 按 ID 查詢
            example = db.session.query(TextbookExample).filter_by(id=example_id).first()
        else:
            # 按 skill_id 查詢（返回第一個）
            example = db.session.query(TextbookExample).filter_by(skill_id=example_id).first()
        
        if example:
            return {
                'id': example.id,
                'skill_id': example.skill_id,
                'problem_text': example.problem_text,
                'solution': example.solution if hasattr(example, 'solution') else None,
                'difficulty': example.difficulty if hasattr(example, 'difficulty') else None,
            }
        return None
    
    except Exception as e:
        print(f"[警告] 數據庫查詢失敗: {e}")
        return None


def get_skill_domain(skill_id):
    """根據 skill_id 判斷其所屬的 Domain"""
    domain_mapping = {
        'ApplicationsOfDerivatives': 'ApplicationsOfDerivatives',
        'AverageValueOfContinuousFunction': 'AverageValueOfContinuousFunction',
        'PolynomialInequalities': 'PolynomialInequalities',
        'JudgingTheRelationshipOfCircleAndLine': 'JudgingTheRelationshipOfCircleAndLine',
        'BasicTrigonometricIdentities': 'BasicTrigonometricIdentities',
        'Logarithms': 'Logarithms',
        'LinearTransformationsOnAPlane': 'LinearTransformationsOnAPlane',
    }
    return domain_mapping.get(skill_id, None)


def extract_code_from_response(response):
    """從 AI 回應中萃取代碼（去掉 markdown wrapper）"""
    match = re.search(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
    if match:
        return match.group(1)
    return response


def heal_code(code):
    """使用 Healer 修復代碼（簡化版，v0.1 版本）"""
    # 修復 1: ^ 改為 **
    code = re.sub(r'(\w+)\s*\^\s*(\w+)', r'\1 ** \2', code)
    
    # 修復 2: 移除 import 語句
    code = re.sub(r'^import\s+.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'^from\s+.*import.*$', '', code, flags=re.MULTILINE)
    
    # 修復 3: 移除空行
    code = re.sub(r'\n\s*\n', '\n', code)
    
    return code


def execute_generated_code(code):
    """
    在沙盒環境執行生成的代碼
    
    Returns:
        dict: {'question_text': ..., 'answer': ...} 或 {'error': ...}
    """
    
    # 安全執行環境
    safe_globals = {
        'randint': random.randint,
        'choice': random.choice,
        'shuffle': random.shuffle,
        'symbols': __import__('sympy').symbols,
        'diff': __import__('sympy').diff,
        'simplify': __import__('sympy').simplify,
        'latex': __import__('sympy').latex,
        'Fraction': Fraction,
        'math': math,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'zip': zip,
        'range': range,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
    }
    
    safe_locals = {}
    
    try:
        # 執行代碼
        exec(code, safe_globals, safe_locals)
        
        # 檢查返回值
        if 'result' in safe_locals:
            result = safe_locals['result']
        else:
            return {"error": "代碼未返回結果（未找到 result 變數）"}
        
        # 驗證返回格式
        if not isinstance(result, dict):
            return {"error": f"返回值必須是 dict，收到 {type(result).__name__}"}
        
        if 'question_text' not in result or 'answer' not in result:
            return {"error": f"返回 dict 缺少必要的鍵：'question_text' 或 'answer'"}
        
        return result
        
    except SyntaxError as e:
        return {"error": f"語法錯誤: {str(e)} (行 {e.lineno})"}
    except Exception as e:
        return {"error": f"執行錯誤: {type(e).__name__}: {str(e)}"}
