# -*- coding: utf-8 -*-
"""
测试 clean_latex_output 函数的中文字处理
"""

import re

def clean_latex_output(q_str):
    """
    [V9.2.6 Fix] LaTeX 格式清洗器 - 智能分离中文与数学式
    """
    if not isinstance(q_str, str): return str(q_str)
    clean_q = q_str.replace('$', '').strip()
    
    # 1. 修复运算符
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*\*\s*', r' \\times ', clean_q)
    clean_q = re.sub(r'(?<![\\a-zA-Z])\s*/\s*(?![{}])', r' \\div ', clean_q)
    
    # 2. 修复双重括号
    clean_q = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', clean_q)
    
    # 3. 移除多余空白
    clean_q = re.sub(r'\s+', ' ', clean_q).strip()
    
    # 4. 智能分离中文与数学式
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', clean_q))
    
    if has_chinese:
        # Pattern: 匹配数学表达式
        math_pattern = r'[\d\-+()（）\[\]【】]+|\\[a-z]+\s*\{[^}]*\}|\\[a-z]+|[a-zA-Z_]\w*'
        
        parts = []
        last_end = 0
        
        for match in re.finditer(math_pattern, clean_q):
            start, end = match.span()
            
            # 添加之前的文本（中文部分）
            if start > last_end:
                text_part = clean_q[last_end:start].strip()
                if text_part:
                    parts.append(text_part)
            
            # 添加数学部分（需要包裹 $）
            math_part = match.group()
            if math_part.strip():
                parts.append(f'${math_part}$')
            
            last_end = end
        
        # 添加剩余的文本
        if last_end < len(clean_q):
            text_part = clean_q[last_end:].strip()
            if text_part:
                parts.append(text_part)
        
        # 合并并清理多余空格
        result = ' '.join(parts)
        result = re.sub(r'\s+', ' ', result).strip()
        
        # 清理连续的 $ 符号
        result = re.sub(r'\$\s+\$', ' ', result)
        
        return result
    else:
        return f"${clean_q}$"

# 测试
print("="*60)
print("测试 clean_latex_output 中文字分离功能")
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

print("\n预期：計算 $...$ 的值。（中文在外，数学式在内）")

# 更多测试
test_cases = [
    "計算 3 + 5",
    "求 (a + b) / c 的值",
    "5 + 3",  # 纯数学
]

print("\n" + "="*60)
print("更多测试")
print("="*60)

for test in test_cases:
    result = clean_latex_output(test)
    has_chinese_in_math = bool(re.search(r'\$[^$]*[\u4e00-\u9fff]', result))
    status = "❌" if has_chinese_in_math else "✅"
    print(f"{status} {test}")
    print(f"   → {result}")
