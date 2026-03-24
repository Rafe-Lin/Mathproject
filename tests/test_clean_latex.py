# -*- coding: utf-8 -*-
"""
测试 clean_latex_output 函数的中文字处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.code_generator import clean_latex_output

print("="*60)
print("测试 clean_latex_output 中文字分离功能")
print("="*60)

# 测试用例
test_cases = [
    # (输入, 预期输出（大致）, 说明)
    ("計算 (10 + (-20)) \\times (-4) \\times (-1) 的值。", 
     "計算 $...$ 的值。", 
     "中文 + 数学式 + 中文"),
    
    ("計算 3 + 5", 
     "計算 $3$ $+$ $5$", 
     "中文 + 简单算式"),
    
    ("5 + 3", 
     "$5 + 3$", 
     "纯数学式（无中文）"),
    
    ("求 (a + b) / c 的值",
     "求 $...$ 的值",
     "中文 + 代数式"),
]

print("\n📝 测试用例：\n")

for i, (input_str, expected_pattern, desc) in enumerate(test_cases, 1):
    print(f"[{i}] {desc}")
    print(f"  输入：{input_str}")
    
    result = clean_latex_output(input_str)
    print(f"  输出：{result}")
    
    # 检查中文是否在 $ 外面
    import re
    
    # 检查是否有中文在 $ 内
    chinese_in_math = re.findall(r'\$[^$]*[\u4e00-\u9fff][^$]*\$', result)
    
    if chinese_in_math:
        print(f"  ❌ 错误：中文字在 $ 内！{chinese_in_math}")
    else:
        print(f"  ✅ 正确：中文字在 $ 外")
    
    print()

print("="*60)
print("详细测试：用户报告的实际case")
print("="*60)

actual_input = "計算 (10 + (-20)) \\times (-4) \\times (-1) 的值。"
print(f"\n输入：{actual_input}")

result = clean_latex_output(actual_input)
print(f"输出：{result}")

# 分析输出
if "$計算" in result or "的值。$" in result:
    print("\n❌ 失败：中文字仍在 $ 内！")
else:
    print("\n✅ 成功：中文字在 $ 外！")

print("\n预期格式：計算 $(10 + (-20)) \\times (-4) \\times (-1)$ 的值。")
print("或类似：計算 $...$數學式... 的值。")
