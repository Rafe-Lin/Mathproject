# -*- coding: utf-8 -*-
"""
快速測試：驗證 generate_operands 返回值修復
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("="*60)
print("測試生成的代碼是否能穩定執行")
print("=" *60)

try:
    # 導入生成的模組
    from skills.jh_數學1上_FourArithmeticOperationsOfIntegers_14B_Ab3 import generate
    
    print("\n✅ 模組導入成功\n")
    
    # 測試 20 次生成
    successes = 0
    failures = 0
    errors = []
    
    for i in range(20):
        try:
            result = generate()
            assert isinstance(result, dict), f"返回值類型錯誤：{type(result)}"
            assert 'question_text' in result, "缺少 question_text"
            assert 'answer' in result, "缺少 answer"
            successes += 1
            if i < 3:  # 顯示前 3 個
                print(f"[{i+1}/20] ✅ {result['question_text'][:60]}...")
        except Exception as e:
            failures += 1
            error_msg = f"[{i+1}/20] ❌ {type(e).__name__}: {str(e)}"
            errors.append(error_msg)
            if failures <= 3:  # 只顯示前 3 個錯誤
                print(error_msg)
    
    print(f"\n{'='*60}")
    print(f"測試結果")
    print(f"{'='*60}")
    print(f"  成功：{successes}/20 ({successes/20*100:.1f}%)")
    print(f"  失敗：{failures}/20 ({failures/20*100:.1f}%)")
    
    if failures > 0:
        print(f"\n{'='*60}")
        print(f"錯誤詳情（前 3 個）")
        print(f"{'='*60}")
        for err in errors[:3]:
            print(err)
        
        print(f"\n🔴 問題確認：generate_operands 仍然可能返回 None")
        print(f"建議：Code Generator 需要添加更強的防護邏輯")
    else:
        print(f"\n🎉 所有測試通過！代碼修復成功！")
        
except Exception as e:
    print(f"\n❌ 錯誤：{type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
