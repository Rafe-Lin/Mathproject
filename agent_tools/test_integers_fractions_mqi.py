#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试整数和分数运算单元的 MQI 分数"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.evaluate_mcri import MCRI_Evaluator

# 创建评估器实例（使用虚拟参数，因为我们只需要 analyze_math_complexity 方法）
evaluator = MCRI_Evaluator(
    skill_path="dummy", 
    ablation_id=3,
    model_name="dummy"
)

def test_integers_unit():
    """测试整数四则运算 - 不应该有根号问题"""
    print("=" * 60)
    print("测试单元 1: 整数四则运算")
    print("=" * 60)
    
    test_cases = [
        {
            "question": r"計算 $[(-20) + (-10)] \div (-5) \times 3 + \left|8 \times (-2) - 5\right|$ 的值。",
            "expected_ops": ["abs", "×", "÷", "+", "-"],
            "expected_score_range": (2.0, 5.0)
        },
        {
            "question": r"計算 $(-15) \times 4 + \left|(-8) \div 2\right| - 3$ 的值。",
            "expected_ops": ["abs", "×", "÷", "+", "-"],
            "expected_score_range": (2.0, 4.0)
        },
        {
            "question": r"計算 $\left|(-12) + 7\right| \times 5 - 10 \div 2$ 的值。",
            "expected_ops": ["abs", "×", "÷", "+", "-"],
            "expected_score_range": (2.0, 4.0)
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['question'][:50]}...")
        final_ops, atom_count, inference_steps = evaluator.analyze_math_complexity(case['question'])
        score = min(5.0, (final_ops / 25.0) * 5.0)
        
        min_score, max_score = case['expected_score_range']
        status = "✅" if min_score <= score <= max_score else "❌"
        
        print(f"  MQI 分数: {score:.2f}/5.00 {status}")
        print(f"  期望范围: {min_score:.1f} - {max_score:.1f}")
        
        if score < min_score:
            print(f"  ⚠️ 分数过低！可能有问题。")

def test_fractions_unit():
    """测试分数运算 - 检查 \\frac{}{} 是否正确计分"""
    print("\n" + "=" * 60)
    print("测试单元 2: 分数四则运算")
    print("=" * 60)
    
    test_cases = [
        {
            "question": r"計算 $[(-2+5) \times \frac{1}{3}] \div \left(-\frac{5}{2}\right) + \left|8 \times \left(-\frac{1}{4}\right) - 5\right|$ 的值。",
            "expected_ops": ["frac", "abs", "×", "÷", "+", "-"],
            "expected_score_range": (3.0, 5.0),
            "note": "包含 3 个 \\frac{}{} 应该得高分"
        },
        {
            "question": r"計算 $\frac{3}{4} + \frac{2}{5} - \frac{1}{2}$ 的值。",
            "expected_ops": ["frac", "+", "-"],
            "expected_score_range": (2.0, 4.0),
            "note": "包含 3 个 \\frac{}{}"
        },
        {
            "question": r"計算 $\left|\frac{-8}{3} + \frac{5}{6}\right| \times \frac{2}{7}$ 的值。",
            "expected_ops": ["frac", "abs", "×", "+"],
            "expected_score_range": (3.0, 5.0),
            "note": "包含 3 个 \\frac{}{} + abs"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['question'][:50]}...")
        print(f"  说明: {case['note']}")
        final_ops, atom_count, inference_steps = evaluator.analyze_math_complexity(case['question'])
        score = min(5.0, (final_ops / 25.0) * 5.0)
        
        min_score, max_score = case['expected_score_range']
        status = "✅" if min_score <= score <= max_score else "❌"
        
        print(f"  MQI 分数: {score:.2f}/5.00 {status}")
        print(f"  期望范围: {min_score:.1f} - {max_score:.1f}")
        
        if score < min_score:
            print(f"  ❌ 分数过低！\\frac{{}}{{}} 可能未被正确计分！")
            print(f"  详细: final_ops={final_ops}, atom_count={atom_count}, inference_steps={inference_steps}")

def test_combined():
    """测试混合运算"""
    print("\n" + "=" * 60)
    print("测试单元 3: 混合运算（包含分数和根号）")
    print("=" * 60)
    
    test_cases = [
        {
            "question": r"化簡 $\sqrt{48} + \frac{1}{2}\sqrt{12} - \frac{2}{3}\sqrt{27}$。",
            "expected_ops": ["sqrt", "frac", "+", "-"],
            "expected_score_range": (4.0, 5.0),
            "note": "3个 sqrt + 2个 frac = 至少 3*3 + 2*2 = 13 bonus"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['question'][:60]}...")
        print(f"  说明: {case['note']}")
        final_ops, atom_count, inference_steps = evaluator.analyze_math_complexity(case['question'])
        score = min(5.0, (final_ops / 25.0) * 5.0)
        
        min_score, max_score = case['expected_score_range']
        status = "✅" if min_score <= score <= max_score else "❌"
        
        print(f"  MQI 分数: {score:.2f}/5.00 {status}")
        print(f"  期望范围: {min_score:.1f} - {max_score:.1f}")

if __name__ == "__main__":
    print("\n🔍 检查整数和分数运算单元的 MQI 分数")
    print("=" * 60)
    
    test_integers_unit()
    test_fractions_unit()
    test_combined()
    
    print("\n" + "=" * 60)
    print("📊 总结")
    print("=" * 60)
    print("如果分数运算单元的 MQI 分数过低（< 2.0），")
    print("说明 \\frac{}{} 也需要在 evaluate_mcri.py 中添加 bonus 分！")
