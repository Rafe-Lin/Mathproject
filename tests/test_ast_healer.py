# -*- coding: utf-8 -*-
"""
测试 AST Healer 的内部函数返回值自动修复功能
"""

import sys
import os
import ast
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.code_generator import ASTHealer, fix_code_via_ast

print("="*60)
print("测试 AST Healer 自动修复内部函数返回值")
print("="*60)

# 测试代码：模拟 AI 生成的缺少返回值的内部函数
test_code = """
def generate(level=1, **kwargs):
    def helper(target):
        for i in range(100):
            if i == target:
                return i * 2
    
    result = helper(10)
    return {'answer': result}
"""

print("\n📝 原始代码（有 bug）：")
print(test_code)

print("\n🔧 运行 AST Healer...")
fixed_code, fixes = fix_code_via_ast(test_code)

print(f"\n✅ 修复完成！修复次数: {fixes}")
print("\n📝 修复后的代码：")
print(fixed_code)

# 验证修复是否正确
print("\n🧪 验证修复结果...")
try:
    tree = ast.parse(fixed_code)
    
    # 找到 helper 函数
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'helper':
            last_stmt = node.body[-1]
            if isinstance(last_stmt, ast.Return):
                print("✅ helper 函数现在有默认返回值！")
                # 打印返回值
                if isinstance(last_stmt.value, ast.Tuple):
                    print(f"   返回值：({last_stmt.value.elts[0].value}, {last_stmt.value.elts[1].value})")
            else:
                print("❌ helper 函数仍然缺少返回值")
            break
    
    # 尝试执行修复后的代码
    print("\n🧪 尝试执行修复后的代码...")
    namespace = {}
    exec(fixed_code, namespace)
    result = namespace['generate']()
    print(f"✅ 执行成功！返回值: {result}")
    
except Exception as e:
    print(f"❌ 错误：{type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("测试完成！")
print("="*60)
