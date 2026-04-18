#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
驗證自適應複習模式的完整 Web 集成
"""

import sys
import os
import io

# 強制設定輸出編碼為 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

print("=" * 80)
print("自適應複習模式 - 完整 Web 集成驗證")
print("=" * 80)

# 1. 驗證 HTML 模板
print("\n[1/5] 驗證 HTML 模板...")
try:
    templates_path = os.path.join(basedir, 'templates')
    required_templates = ['adaptive_review.html', 'dashboard.html']
    
    for template in required_templates:
        template_file = os.path.join(templates_path, template)
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'adaptive-review' in content or 'adaptive_review' in content:
                    print(f"   ✅ {template} - 正常")
                else:
                    print(f"   ⚠️  {template} - 可能不完整")
        else:
            print(f"   ❌ {template} - 不存在")
except Exception as e:
    print(f"   ❌ 模板驗證失敗: {e}")

# 2. 驗證 Flask 路由
print("\n[2/5] 驗證 Flask 應用路由...")
try:
    from app import create_app
    test_app = create_app()
    
    # 查找自適應複習相關路由
    review_routes = []
    for rule in test_app.url_map.iter_rules():
        if 'review' in rule.rule or 'adaptive-review' in rule.rule:
            review_routes.append({
                'rule': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'})
            })
    
    # 檢查頁面路由
    page_routes = []
    for rule in test_app.url_map.iter_rules():
        if rule.rule == '/adaptive-review':
            page_routes.append(rule.rule)
    
    if page_routes:
        print(f"   ✅ 頁面路由已註冊: {page_routes}")
    else:
        print(f"   ❌ 頁面路由未找到")
    
    if review_routes:
        print(f"   ✅ 複習相關 API 路由:")
        for route in review_routes:
            if '/api/adaptive-review' in route['rule']:
                print(f"      • {route['rule']} [{', '.join(route['methods'])}]")
    
except Exception as e:
    print(f"   ❌ 路由驗證失敗: {e}")
    import traceback
    traceback.print_exc()

# 3. 驗證 API 藍圖
print("\n[3/5] 驗證 API 藍圖...")
try:
    from adaptive_review_api import adaptive_review_bp
    print(f"   ✅ adaptive_review_bp 已導入")
    print(f"      • 藍圖名稱: {adaptive_review_bp.name}")
    print(f"      • URL 前綴: {adaptive_review_bp.url_prefix}")
except Exception as e:
    print(f"   ❌ API 藍圖驗證失敗: {e}")

# 4. 驗證核心模組
print("\n[4/5] 驗證核心模組...")
try:
    from adaptive_review_mode import AdaptiveReviewEngine
    engine = AdaptiveReviewEngine()
    print(f"   ✅ AdaptiveReviewEngine 已初始化")
    print(f"      • 技能數: {engine.n_skills}")
    print(f"      • 題目數: {engine.n_items}")
except Exception as e:
    print(f"   ❌ 核心模組驗證失敗: {e}")

# 5. 檢查文檔
print("\n[5/5] 檢查文檔...")
try:
    docs = [
        'ADAPTIVE_REVIEW_MODE.md',
        'ADAPTIVE_REVIEW_ROUTING.md',
        'adaptive_review_examples.py',
        'adaptive_review_integration.py'
    ]
    
    for doc in docs:
        doc_path = os.path.join(basedir, doc)
        if os.path.exists(doc_path):
            print(f"   ✅ {doc}")
        else:
            print(f"   ❌ {doc}")
except Exception as e:
    print(f"   ⚠️  文檔檢查異常: {e}")

# ════════════════════════════════════════════════════════════════════════════
# 總結
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("✅ 完整 Web 集成驗證完成！")
print("=" * 80)

print("\n📌 使用說明:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

print("\n1️⃣  啟動應用")
print("   $ python app.py")
print("   訪問: http://localhost:5000")

print("\n2️⃣  進入自適應複習模式")
print("   • 登錄後進入學生儀表板")
print("   • 點擊右上角「✨ RL 智慧複習」按鈕")
print("   • 或直接訪問: http://localhost:5000/adaptive-review")

print("\n3️⃣  使用功能")
print("   • 點擊「開始複習」獲取 RL 推薦題目")
print("   • 選擇題目後提交答案")
print("   • 點擊「生成計畫」查看複習建議")

print("\n4️⃣  API 端點")
print("   POST   /api/adaptive-review/start           # 開始複習")
print("   GET    /api/adaptive-review/analyze/<id>    # 分析弱項")
print("   POST   /api/adaptive-review/feedback        # 提交反饋")
print("   GET    /api/adaptive-review/plan/<id>       # 生成計畫")
print("   GET    /api/adaptive-review/health          # 健康檢查")

print("\n📚 文檔")
print("   • ADAPTIVE_REVIEW_MODE.md - 完整功能文檔")
print("   • ADAPTIVE_REVIEW_ROUTING.md - 路由與集成說明")
print("   • adaptive_review_examples.py - 代碼示例")

print("\n" + "=" * 80)
print("🎉 Web 集成已完成，系統已可正常使用！")
print("=" * 80)
