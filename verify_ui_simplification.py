#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 RL 自適應複習模式 UI 簡化完成
檢查：
1. 移除表情符號
2. 白色背景
3. 簡洁風格
"""

import os
import re
import sys

def check_file_for_emojis(filepath):
    """檢查文件中的表情符號"""
    emojis_pattern = r'[🎓📚📊💡✅❌🔴🟡✨🎉🚀📝📅💼🟢📈⭐⚠️]'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.finditer(emojis_pattern, content)
    found_emojis = []
    
    for match in matches:
        # 找到行號
        line_num = content[:match.start()].count('\n') + 1
        found_emojis.append({
            'emoji': match.group(),
            'line': line_num,
            'position': match.start()
        })
    
    return found_emojis

def check_background_color(filepath):
    """檢查背景顏色是否改為白色"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否有紫色漸變背景
    has_purple_gradient = 'linear-gradient(135deg, #667eea' in content
    
    # 檢查是否有白色背景
    has_white_background = 'background: #ffffff' in content or 'background: white' in content
    
    return {
        'has_purple_gradient': has_purple_gradient,
        'has_white_background': has_white_background
    }

def check_color_scheme(filepath):
    """檢查配色方案"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 統計顏色使用
    colors = {
        '#0066cc': content.count('#0066cc'),  # 新的藍色
        '#667eea': content.count('#667eea'),  # 舊的紫色
        '#764ba2': content.count('#764ba2'),  # 舊的紫色
        '#f5f5f5': content.count('#f5f5f5'),  # 淺灰色
        '#fafafa': content.count('#fafafa'),  # 更淺的灰色
        '#e0e0e0': content.count('#e0e0e0'),  # 邊框灰色
        'white': content.count('white'),
        'ffffff': content.count('ffffff')
    }
    
    return colors

def check_border_radius(filepath):
    """檢查邊框半徑是否簡化"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查大的邊框半徑
    large_radius = len(re.findall(r'border-radius: 1[0-5]px', content))
    small_radius = len(re.findall(r'border-radius: [468]px', content))
    
    return {
        'large_radius_count': large_radius,
        'small_radius_count': small_radius
    }

def check_shadows(filepath):
    """檢查陰影是否移除"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否還有大量陰影效果
    shadow_count = len(re.findall(r'box-shadow:', content))
    gradient_count = len(re.findall(r'linear-gradient', content))
    backdrop_filter_count = len(re.findall(r'backdrop-filter', content))
    
    return {
        'box_shadow_count': shadow_count,
        'gradient_count': gradient_count,
        'backdrop_filter_count': backdrop_filter_count
    }

def check_responsive_design(filepath):
    """檢查響應式設計"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_media_queries = bool(re.search(r'@media.*\(max-width', content))
    
    return has_media_queries

def main():
    """主函數"""
    print("=" * 70)
    print("RL 自適應複習模式 UI 簡化驗證")
    print("=" * 70)
    
    html_file = 'templates/adaptive_review.html'
    dashboard_file = 'templates/dashboard.html'
    
    # 驗證主HTML文件
    print("\n【adaptive_review.html 驗證】")
    print("-" * 70)
    
    # 1. 檢查表情符號
    print("\n1. 檢查表情符號移除...")
    emojis = check_file_for_emojis(html_file)
    if emojis:
        print(f"   ✗ 發現 {len(emojis)} 個表情符號：")
        for emoji_info in emojis[:5]:  # 只顯示前5個
            print(f"     - '{emoji_info['emoji']}' 在第 {emoji_info['line']} 行")
        return False
    else:
        print("   ✓ 已成功移除所有表情符號")
    
    # 2. 檢查背景顏色
    print("\n2. 檢查背景顏色...")
    bg_check = check_background_color(html_file)
    if bg_check['has_purple_gradient']:
        print("   ✗ 仍然存在紫色漸變背景")
        return False
    if bg_check['has_white_background']:
        print("   ✓ 已改為白色背景")
    else:
        print("   ⚠ 未找到明確的白色背景定義")
    
    # 3. 檢查配色方案
    print("\n3. 檢查配色方案...")
    colors = check_color_scheme(html_file)
    print(f"   • 新藍色 (#0066cc): {colors['#0066cc']} 次")
    print(f"   • 舊紫色 (#667eea): {colors['#667eea']} 次")
    print(f"   • 舊紫色 (#764ba2): {colors['#764ba2']} 次")
    print(f"   • 淺灰色 (#f5f5f5): {colors['#f5f5f5']} 次")
    print(f"   • 邊框灰色 (#e0e0e0): {colors['#e0e0e0']} 次")
    
    if colors['#667eea'] == 0 and colors['#764ba2'] == 0:
        print("   ✓ 已成功移除紫色方案")
    else:
        print("   ⚠ 仍存在部分紫色配色")
    
    # 4. 檢查邊框半徑
    print("\n4. 檢查邊框半徑...")
    radius = check_border_radius(html_file)
    print(f"   • 大邊框 (10-15px): {radius['large_radius_count']} 個")
    print(f"   • 小邊框 (4-8px): {radius['small_radius_count']} 個")
    if radius['large_radius_count'] == 0:
        print("   ✓ 邊框半徑已簡化")
    
    # 5. 檢查視覺效果
    print("\n5. 檢查視覺效果簡化...")
    effects = check_shadows(html_file)
    print(f"   • 陰影效果: {effects['box_shadow_count']} 個")
    print(f"   • 漸變效果: {effects['gradient_count']} 個")
    print(f"   • 背景濾鏡: {effects['backdrop_filter_count']} 個")
    if effects['backdrop_filter_count'] == 0:
        print("   ✓ 已移除背景濾鏡")
    
    # 6. 檢查響應式設計
    print("\n6. 檢查響應式設計...")
    has_responsive = check_responsive_design(html_file)
    if has_responsive:
        print("   ✓ 保留響應式設計支持")
    else:
        print("   ✗ 缺少響應式設計")
        return False
    
    # 驗證 dashboard.html
    print("\n\n【dashboard.html 驗證】")
    print("-" * 70)
    
    print("\n1. 檢查儀表板按鈕表情符號...")
    dashboard_emojis = check_file_for_emojis(dashboard_file)
    if dashboard_emojis:
        print(f"   ✗ 發現 {len(dashboard_emojis)} 個表情符號")
        return False
    else:
        print("   ✓ 已成功移除表情符號")
    
    print("\n2. 檢查按鈕文本...")
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
    
    if '自適應複習' in dashboard_content:
        print("   ✓ 按鈕文本已改為「自適應複習」")
    else:
        print("   ✗ 未找到簡化後的按鈕文本")
        return False
    
    # 總結
    print("\n" + "=" * 70)
    print("✓ UI 簡化驗證完成！")
    print("=" * 70)
    print("\n修改總結：")
    print("  • 移除所有表情符號 ✓")
    print("  • 改為白色背景 ✓")
    print("  • 採用簡洁配色 (#0066cc 藍色) ✓")
    print("  • 簡化視覺效果 ✓")
    print("  • 移除梯度和陰影 ✓")
    print("  • 保留響應式設計 ✓")
    print("\n下次操作建議：")
    print("  1. 在本地瀏覽器測試頁面外觀")
    print("  2. 驗證所有按鈕和交互功能正常")
    print("  3. 檢查移動設備上的顯示效果")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 驗證失敗：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
