# -*- coding: utf-8 -*-
"""
测试 MQI 评分逻辑
"""
import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("⚠️ SymPy 未安装!")

print("="*80)
print("🔍 MQI 评分逻辑测试")
print("="*80)

# 模拟生成的题目
test_questions = [
    # 实际生成的题目格式
    "化簡 $$(\\sqrt{8} + \\sqrt{12}) + 3(\\sqrt{3} + \\sqrt{4})$$",
    "化簡 $$(4\\sqrt{8} + 7\\sqrt{18}) + 3(\\sqrt{3} + \\sqrt{4})$$",
    
    # 简单题目对比
    "計算 3 + 5 × 2",
    "計算 (3 + 5) × (2 - 1)",
    "計算 \\frac{3}{4} + \\frac{5}{6}",
]

def analyze_math_complexity(question_text: str):
    """
    复制自 evaluate_mcri.py 的实现
    """
    if not HAS_SYMPY:
        return 0, 0, 0
    
    try:
        text = str(question_text).strip()
        if not text: return 0, 0, 0

        print(f"\n原始题目: {text}")

        # 1. 强力清洗
        text = text.replace("計算", "").replace("化簡", "").replace("的值", "").replace("。", "").replace(" ", "")
        text = text.replace(r'\\left', '').replace(r'\\right', '')
        text = text.replace(r'\\div', '/').replace(r'\\times', '*').replace(r'\\cdot', '*')
        text = re.sub(r'\\\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
        
        mapping = {
            '×': '*', '÷': '/', '⋅': '*', 
            '[': '(', ']': ')', '{': '(', '}': ')',
            '（': '(', '）': ')', '－': '-', '＋': '+', '／': '/'
        }
        for old, new in mapping.items():
            text = text.replace(old, new)
        
        text = re.sub(r'\|([^|]+)\|', r'abs(\1)', text)
        
        print(f"清洗后: {text}")
        
        # 2. 提取算式核心
        clean_q = re.sub(r'[^\d\.\+\-\*\/\(\)absx=,]', '', text)
        
        if '=' in clean_q:
            clean_q = clean_q.split('=')[0]
        
        print(f"提取核心: {clean_q}")
        
        if not clean_q: 
            print("❌ 提取失败，核心为空")
            return 0, 0, 0

        # 3. 解析
        transformations = standard_transformations + (implicit_multiplication_application,)
        local_dict = {"abs": sympy.Abs}
        
        expr = parse_expr(clean_q, transformations=transformations, local_dict=local_dict)
        print(f"SymPy 表达式: {expr}")
        
        # 基础运算数
        base_ops = int(sympy.count_ops(expr))
        print(f"基础 ops (count_ops): {base_ops}")
        
        # 加分项
        bonus_ops = 0
        if r'\frac' in question_text:
            frac_count = question_text.count(r'\frac')
            bonus_ops += 2 * frac_count
            print(f"   +{2 * frac_count} (\\frac × {frac_count})")
        
        if 'abs(' in text or '|' in question_text:
            abs_count = text.count('abs(')
            bonus_ops += 3 * abs_count
            print(f"   +{3 * abs_count} (abs × {abs_count})")
        
        if '-' in text:
            minus_count = text.count('-')
            bonus_ops += 1 * minus_count
            print(f"   +{1 * minus_count} (minus × {minus_count})")
        
        final_ops = base_ops + bonus_ops
        print(f"最终 math_ops: {final_ops}")
        
        # 计算 MQI
        mqi_score = min(5.0, (final_ops / 25.0) * 5.0)
        print(f"MQI 分数: {mqi_score:.2f}/5.00")
        
        # 推导步数
        inference_steps = 0
        for node in sympy.preorder_traversal(expr):
            if isinstance(node, (sympy.Add, sympy.Mul, sympy.Pow, sympy.Abs)):
                inference_steps += 1
        
        print(f"推导步数: {inference_steps}")
        
        return final_ops, sympy.count_ops(expr), inference_steps
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        # Fallback
        try:
            fallback_ops = len(re.findall(r'[\+\-\*\/]', question_text))
            print(f"Fallback ops: {fallback_ops}")
            mqi_fallback = min(5.0, (fallback_ops / 25.0) * 5.0)
            print(f"MQI 分数 (fallback): {mqi_fallback:.2f}/5.00")
            return fallback_ops, 0, 0
        except:
            return 0, 0, 0

print("\n" + "="*80)
print("测试开始")
print("="*80)

for i, q in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"测试 {i}/{len(test_questions)}")
    print("="*80)
    analyze_math_complexity(q)

print("\n" + "="*80)
print("✅ 测试完成")
print("="*80)

print("\n💡 MQI 评分公式:")
print("   mqi_score = min(5.0, (math_ops / 25.0) * 5.0)")
print("\n   要达到满分 5.0，需要 math_ops ≥ 25")
print("   math_ops = base_ops + bonus_ops")
print("     - base_ops: SymPy count_ops (基础运算符)")
print("     - bonus_ops: \\frac(+2) + abs(+3) + minus(+1)")
