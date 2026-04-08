# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/knowledge_graph.py
功能說明 (Description): 知識圖譜視覺化路由，提供知識點前置關係的樹狀圖展示（基於 JSON 文件）
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-04-07
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, render_template
from flask_login import current_user, login_required
from typing import Optional

from . import core_bp
from core.kg_data_loader import get_kg_loader

# ==========================================
# 知識圖譜頁面
# ==========================================

@core_bp.route('/knowledge-graph')
@login_required
def knowledge_graph():
    """
    顯示知識圖譜視覺化頁面
    """
    return render_template('knowledge_graph.html', username=current_user.username)


# ==========================================
# 知識圖譜資料 API
# ==========================================

@core_bp.route('/api/knowledge-graph/data')
@login_required
def get_knowledge_graph_data():
    """
    獲取知識圖譜的節點和連接資料（基於 JSON 文件）
    
    查詢參數:
        grade: 年級 (如 '國一上', '國一下', '國二上', '國二下')
        unit_id: 單元 ID（可選，如 'JH_NUM_INT_NL'）
    
    返回:
        JSON 格式的圖譜資料，包含 nodes 和 links
    """
    try:
        # 獲取篩選參數
        grade = request.args.get('grade')
        unit_id = request.args.get('unit_id')
        
        if not grade:
            return jsonify({'error': '缺少必要參數: grade'}), 400
        
        # 獲取 KG 資料加載器
        kg_loader = get_kg_loader()
        
        # 獲取圖譜資料
        graph_data = kg_loader.get_graph_data(grade, unit_id)
        
        return jsonify(graph_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==========================================
# 獲取篩選選項 API
# ==========================================

@core_bp.route('/api/knowledge-graph/filters')
@login_required
def get_knowledge_graph_filters():
    """
    獲取可用的篩選選項（年級、單元等）
    """
    try:
        grade = request.args.get('grade')
        
        # 獲取 KG 資料加載器
        kg_loader = get_kg_loader()
        
        result = {}
        
        # 獲取所有可用的年級
        if not grade:
            grades = kg_loader.get_all_grades()
            result['grades'] = grades
            return jsonify(result)
        
        # 獲取該年級的所有單元
        if grade:
            units = kg_loader.get_units_for_grade(grade)
            result['units'] = list(units.keys())
            return jsonify(result)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# 搜尋功能 API
# ==========================================

@core_bp.route('/api/knowledge-graph/search')
@login_required
def search_knowledge_graph():
    """
    搜尋知識圖譜中的節點（按名稱或描述）
    
    查詢參數:
        grade: 年級（必需）
        keyword: 搜尋關鍵字（必需）
        unit_id: 單元 ID（可選）
    
    返回:
        匹配的節點列表
    """
    try:
        grade = request.args.get('grade')
        keyword = request.args.get('keyword')
        unit_id = request.args.get('unit_id')
        
        if not grade or not keyword:
            return jsonify({'error': '缺少必要參數: grade 或 keyword'}), 400
        
        # 獲取 KG 資料加載器
        kg_loader = get_kg_loader()
        
        # 執行搜尋
        results = kg_loader.search_nodes(grade, keyword, unit_id)
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# 統計功能 API
# ==========================================

@core_bp.route('/api/knowledge-graph/statistics')
@login_required
def get_kg_statistics():
    """
    獲取知識圖譜的統計信息
    
    查詢參數:
        grade: 年級（必需）
        unit_id: 單元 ID（可選）
    
    返回:
        統計信息，包括難度分佈等
    """
    try:
        grade = request.args.get('grade')
        unit_id = request.args.get('unit_id')
        
        if not grade:
            return jsonify({'error': '缺少必要參數: grade'}), 400
        
        # 獲取 KG 資料加載器
        kg_loader = get_kg_loader()
        
        # 獲取難度分佈
        difficulty_dist = kg_loader.get_difficulty_distribution(grade, unit_id)
        
        # 獲取圖譜資料以統計節點數
        graph_data = kg_loader.get_graph_data(grade, unit_id)
        
        return jsonify({
            'difficulty_distribution': difficulty_dist,
            'total_nodes': len(graph_data['nodes']),
            'total_links': len(graph_data['links'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
