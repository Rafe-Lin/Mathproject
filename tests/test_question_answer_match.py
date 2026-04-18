# -*- coding: utf-8 -*-
"""
验证题目和答案是否匹配
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入生成的模块
from skills.jh_數學1上_FourArithmeticOperationsOfIntegers import generate

print("="*60)
print("验证题目和答案是否匹配")
print("="*60)

# 生成 10 个题目并验证
for i in range(10):
    result = generate()
    question = result['question_text']
    answer = result['correct_answer']
    
    # 提取数学表达式（去掉中文和多余的 $）
    import re
    # 提取 $ 内的内容
    math_expr = re.search(r'\$(.+?)\$', question)
    if math_expr:
        expr = math_expr.group(1)
        
        # 清理 LaTeX 符号
        expr_clean = expr.replace('\\times', '*').replace('\\div', '/')
        expr_clean = expr_clean.replace(' ', '')
        
        try:
            # 计算题目的实际答案
            actual_answer = eval(expr_clean)
            
            # 清理给定的答案（去掉括号）
            given_answer = answer.replace('(', '').replace(')', '')
            given_answer_num = float(given_answer)
            
            # 比较
            if abs(actual_answer - given_answer_num) < 0.01:
                print(f"[{i+1}] ✅ 匹配")
            else:
                print(f"[{i+1}] ❌ 不匹配！")
                print(f"    题目：{expr}")
                print(f"    实际答案：{actual_answer}")
                print(f"    给定答案：{given_answer_num}")
                print(f"    差异：{abs(actual_answer - given_answer_num)}")
        
        except Exception as e:
            print(f"[{i+1}] ⚠️  计算错误：{e}")
            print(f"    表达式：{expr_clean}")
    else:
        print(f"[{i+1}] ⚠️  无法提取数学表达式")

print("\n" + "="*60)
print("测试完成")
print("="*60)
