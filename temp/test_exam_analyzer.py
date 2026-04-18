"""
測試考卷分析系統的核心功能
"""
import sys
import os

# 確保可以匯入專案模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from core.exam_analyzer import get_flattened_unit_paths

def test_flattened_paths():
    """測試路徑扁平化功能"""
    print("=== 測試路徑扁平化功能 ===\n")
    
    with app.app_context():
        # 測試 1: 查詢高一的課程
        print("測試 1: 查詢高一普通高中的課程")
        units = get_flattened_unit_paths(grade=10, curriculum='general')
        print(f"找到 {len(units)} 個單元")
        
        if units:
            print("\n前 5 個單元:")
            for unit in units[:5]:
                print(f"  - ID: {unit['unit_id']}")
                print(f"    Path: {unit['path']}")
                print(f"    Name: {unit['skill_name']}\n")
        
        # 測試 2: 查詢國一的課程
        print("\n測試 2: 查詢國一的課程")
        units_jh = get_flattened_unit_paths(grade=7, curriculum='junior_high')
        print(f"找到 {len(units_jh)} 個單元")
        
        if units_jh:
            print("\n前 3 個單元:")
            for unit in units_jh[:3]:
                print(f"  - ID: {unit['unit_id']}")
                print(f"    Path: {unit['path']}")
                print(f"    Name: {unit['skill_name']}\n")
        
        # 測試 3: 查詢所有年級
        print("\n測試 3: 查詢所有年級的普通高中課程")
        all_units = get_flattened_unit_paths(curriculum='general')
        print(f"找到 {len(all_units)} 個單元")
        
        print("\n✅ 路徑扁平化功能測試完成!")

if __name__ == '__main__':
    test_flattened_paths()
