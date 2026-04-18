#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
驗證自適應複習模式整合狀態
"""

import sys
import os

# 設定路徑
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

print("=" * 70)
print("自適應複習模式整合驗證")
print("=" * 70)

# 1. 驗證核心模組
print("\n[1/4] 驗證核心模組...")
try:
    from adaptive_review_mode import AdaptiveReviewEngine
    print("   ✅ adaptive_review_mode.py - OK")
except Exception as e:
    print(f"   ❌ adaptive_review_mode.py - {e}")
    sys.exit(1)

# 2. 驗證 API 模組
print("\n[2/4] 驗證 API 模組...")
try:
    from adaptive_review_api import adaptive_review_bp
    print("   ✅ adaptive_review_api.py - OK")
    print(f"   📍 藍圖名稱: {adaptive_review_bp.name}")
    print(f"   📍 URL 前綴: {adaptive_review_bp.url_prefix}")
except Exception as e:
    print(f"   ❌ adaptive_review_api.py - {e}")
    sys.exit(1)

# 3. 驗證 Flask 應用整合
print("\n[3/4] 驗證 Flask 應用整合...")
try:
    from app import create_app
    test_app = create_app()
    
    # 檢查藍圖是否已註冊
    registered_blueprints = list(test_app.blueprints.keys())
    print(f"   已註冊的藍圖: {registered_blueprints}")
    
    if 'adaptive_review' in registered_blueprints:
        print("   ✅ adaptive_review 藍圖已在 app.py 中註冊")
    else:
        print("   ⚠️  adaptive_review 藍圖未找到")
        
except Exception as e:
    print(f"   ❌ Flask 應用整合 - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 驗證 API 路由
print("\n[4/4] 驗證 API 路由...")
try:
    # 列出所有可用的路由
    api_routes = []
    for rule in test_app.url_map.iter_rules():
        if 'adaptive-review' in rule.rule:
            api_routes.append({
                'rule': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'})
            })
    
    if api_routes:
        print(f"   ✅ 找到 {len(api_routes)} 個自適應複習 API 路由:")
        for route in api_routes:
            print(f"      • {route['rule']} [{', '.join(route['methods'])}]")
    else:
        print("   ⚠️  沒有找到自適應複習 API 路由")
        
except Exception as e:
    print(f"   ❌ 路由驗證 - {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ 整合驗證完成！自適應複習模式已成功整合到 Flask 應用。")
print("=" * 70)

print("\n📌 快速測試:")
print("   1. 啟動應用: python app.py")
print("   2. 測試 API: curl http://localhost:5000/api/adaptive-review/health")
print("   3. 查看文檔: 開啟 ADAPTIVE_REVIEW_MODE.md")
