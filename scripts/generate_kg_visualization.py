# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): scripts/generate_kg_visualization.py
功能說明 (Description): 從 kg_outputs JSON 檔案生成知識圖譜的可視化 HTML
執行語法 (Usage): python scripts/generate_kg_visualization.py [--grade 國一上] [--output-dir outputs/]
版本資訊 (Version): V1.0
更新日期 (Date): 2026-04-07
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import sys
import os

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.kg_data_loader import KGDataLoader


class KGVisualizationGenerator:
    """知識圖譜可視化生成器"""
    
    def __init__(self, kg_outputs_path: str, output_dir: str = 'outputs'):
        """
        初始化可視化生成器
        
        Args:
            kg_outputs_path: kg_outputs 目錄路徑
            output_dir: 輸出目錄
        """
        self.kg_loader = KGDataLoader(kg_outputs_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_html(self, grade: str, unit_id: str = None) -> str:
        """
        生成可視化 HTML
        
        Args:
            grade: 年級名稱
            unit_id: 單元 ID（可選）
        
        Returns:
            生成的 HTML 文件路徑
        """
        # 獲取圖譜資料
        graph_data = self.kg_loader.get_graph_data(grade, unit_id)
        
        # 生成文件名
        if unit_id:
            filename = f"kg_{grade}_{unit_id}.html"
        else:
            filename = f"kg_{grade}_all.html"
        
        output_path = self.output_dir / filename
        
        # 生成統計信息
        difficulty_dist = self.kg_loader.get_difficulty_distribution(grade, unit_id)
        
        # 生成 HTML 內容
        html_content = self._generate_html_content(
            grade, unit_id, graph_data, difficulty_dist
        )
        
        # 寫入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ 已生成: {output_path}")
        return str(output_path)
    
    def _generate_html_content(self, grade: str, unit_id: str, graph_data: Dict, 
                               difficulty_dist: Dict) -> str:
        """生成 HTML 內容"""
        
        # 序列化圖譜資料為 JSON
        graph_json = json.dumps(graph_data, ensure_ascii=False, indent=2)
        difficulty_json = json.dumps(difficulty_dist, ensure_ascii=False, indent=2)
        
        # 標題
        title = f"知識圖譜 - {grade}"
        if unit_id:
            title += f" ({unit_id})"
        
        html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}

        .header h1 {{
            color: #2c3e50;
            font-size: 1.8rem;
            margin-bottom: 10px;
        }}

        .header p {{
            color: #666;
            font-size: 0.95rem;
        }}

        .stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}

        .stat-card strong {{
            display: block;
            color: #2c3e50;
            margin-bottom: 5px;
        }}

        .stat-card span {{
            font-size: 1.5rem;
            color: #3498db;
            font-weight: bold;
        }}

        /* SVG 容器 */
        #graph {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border: 1px solid #eee;
        }}

        /* 節點樣式 */
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .node:hover {{
            stroke-width: 3px;
            filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.3));
        }}

        .node.L0 {{ fill: #E8F4F8; }}
        .node.L1 {{ fill: #B3D9E8; }}
        .node.L2 {{ fill: #7AB3D1; }}
        .node.L3 {{ fill: #4A7BA7; }}
        .node.L4 {{ fill: #1D3557; }}

        /* 連接線樣式 */
        .link {{
            stroke: #999;
            stroke-width: 1.5px;
            stroke-opacity: 0.6;
        }}

        .link.highlighted {{
            stroke: #ff6b6b;
            stroke-width: 3px;
            stroke-opacity: 1;
        }}

        /* 文字 */
        .node-label {{
            font-size: 11px;
            pointer-events: none;
            text-anchor: middle;
            dominant-baseline: middle;
            fill: #fff;
            font-weight: 500;
        }}

        /* Tooltip */
        .tooltip {{
            position: absolute;
            background: #2c3e50;
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            max-width: 300px;
            z-index: 1000;
        }}

        .tooltip.visible {{
            opacity: 1;
        }}

        .legend {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}

        .legend h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1rem;
        }}

        .legend-items {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .legend-box {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 1px solid #999;
        }}

        .legend-item span {{
            font-size: 12px;
            color: #666;
        }}

        /* 控制面板 */
        .controls {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .controls button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s ease;
        }}

        .controls button:hover {{
            background: #2980b9;
        }}

        .controls button.active {{
            background: #27ae60;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>生成於 2026-04-07</p>
            <div class="stats">
                <div class="stat-card">
                    <strong>節點總數</strong>
                    <span id="total-nodes">{len(graph_data['nodes'])}</span>
                </div>
                <div class="stat-card">
                    <strong>連接總數</strong>
                    <span id="total-links">{len(graph_data['links'])}</span>
                </div>
                <div class="stat-card">
                    <strong>難度分佈</strong>
                    <span id="difficulty-summary"></span>
                </div>
            </div>
        </div>

        <div class="controls">
            <button id="zoom-in">放大</button>
            <button id="zoom-out">縮小</button>
            <button id="reset-view">重置視圖</button>
            <button id="toggle-labels">切換標籤</button>
        </div>

        <svg id="graph" width="100%" height="800"></svg>

        <div class="legend">
            <h3>難度分佈</h3>
            <div id="difficulty-chart" style="display: flex; gap: 15px; flex-wrap: wrap;"></div>
        </div>

        <div class="legend">
            <h3>階級說明 (Level Legend)</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-box" style="background: #E8F4F8;"></div>
                    <span>L0: 教育階段</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: #B3D9E8;"></div>
                    <span>L1: 領域</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: #7AB3D1;"></div>
                    <span>L2: 單元</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: #4A7BA7;"></div>
                    <span>L3: 主題</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: #1D3557;"></div>
                    <span>L4: 次主題</span>
                </div>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        // 圖譜資料
        const graphData = {graph_json};
        const difficultyDist = {difficulty_json};

        // 初始化
        const width = document.getElementById('graph').clientWidth || 1600;
        const height = 800;

        // 創建 SVG
        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');

        // 創建力導向圖
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links)
                .id(d => d.id)
                .distance(50)
                .strength(0.5))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide(30));

        // 繪製連接線
        const links = g.selectAll('.link')
            .data(graphData.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', d => {{
                const sourceLevel = graphData.nodes.find(n => n.id === d.source.id)?.level;
                const targetLevel = graphData.nodes.find(n => n.id === d.target.id)?.level;
                return '#ccc';
            }});

        // 繪製節點
        const nodes = g.selectAll('.node')
            .data(graphData.nodes)
            .enter()
            .append('circle')
            .attr('class', d => 'node ' + d.level)
            .attr('r', d => {{
                const sizeMap = {{'L0': 25, 'L1': 22, 'L2': 20, 'L3': 18, 'L4': 15}};
                return sizeMap[d.level] || 20;
            }})
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip);

        // 添加標籤
        const labels = g.selectAll('.node-label')
            .data(graphData.nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('dy', '0.3em')
            .text(d => d.name)
            .style('font-size', d => {{
                const sizeMap = {{'L0': '10px', 'L1': '9px', 'L2': '8px', 'L3': '7px', 'L4': '6px'}};
                return sizeMap[d.level] || '8px';
            }});

        // Tooltip
        const tooltip = document.getElementById('tooltip');

        function showTooltip(event, d) {{
            tooltip.innerHTML = `
                <strong>${{d.name}}</strong><br/>
                ID: ${{d.id}}<br/>
                Level: ${{d.level}}
                ${{d.description ? '<br/><br/>' + d.description : ''}}
                ${{d.difficulty ? '<br/><br/>難度: ' + d.difficulty : ''}}
            `;
            tooltip.classList.add('visible');
            tooltip.style.left = (event.pageX + 10) + 'px';
            tooltip.style.top = (event.pageY + 10) + 'px';
        }}

        function hideTooltip() {{
            tooltip.classList.remove('visible');
        }}

        // 拖拽事件
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}

        // 更新位置
        simulation.on('tick', () => {{
            links
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            nodes
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});

        // 縮放控制
        let currentScale = 1;
        
        document.getElementById('zoom-in').addEventListener('click', () => {{
            currentScale *= 1.2;
            g.attr('transform', `scale(${{currentScale}})`);
        }});

        document.getElementById('zoom-out').addEventListener('click', () => {{
            currentScale /= 1.2;
            g.attr('transform', `scale(${{currentScale}})`);
        }});

        document.getElementById('reset-view').addEventListener('click', () => {{
            currentScale = 1;
            g.attr('transform', 'scale(1)');
        }});

        // 標籤切換
        let labelsVisible = true;
        document.getElementById('toggle-labels').addEventListener('click', function() {{
            labelsVisible = !labelsVisible;
            labels.style('opacity', labelsVisible ? 1 : 0);
            this.classList.toggle('active', labelsVisible);
        }});

        // 生成難度分佈圖表
        const diffChart = document.getElementById('difficulty-chart');
        const diffSummary = document.getElementById('difficulty-summary');
        let diffSummaryText = '';
        
        for (const [difficulty, count] of Object.entries(difficultyDist).sort()) {{
            const bar = document.createElement('div');
            bar.style.display = 'flex';
            bar.style.alignItems = 'center';
            bar.style.gap = '8px';
            bar.innerHTML = `
                <span style="min-width: 40px;">難度 ${{difficulty}}:</span>
                <div style="background: #3498db; height: 20px; width: ${{Math.max(count * 5, 50)}}px; border-radius: 3px;"></div>
                <span>${{count}} 個</span>
            `;
            diffChart.appendChild(bar);
            diffSummaryText += (diffSummaryText ? ', ' : '') + `難度${{difficulty}}: ${{count}}`;
        }}
        diffSummary.textContent = diffSummaryText;
    </script>
</body>
</html>
"""
        return html
    
    def generate_all(self):
        """生成所有可用年級的可視化"""
        grades = self.kg_loader.get_all_grades()
        print(f"發現 {len(grades)} 個年級")
        
        for grade in grades:
            print(f"\n處理年級: {grade}")
            
            # 生成整個年級的可視化
            self.generate_html(grade)
            
            # 生成各個單元的可視化
            units = self.kg_loader.get_units_for_grade(grade)
            for unit_id in units:
                self.generate_html(grade, unit_id)
        
        print(f"\n✓ 全部完成！共生成 {len(grades)} 個年級的可視化")


def main():
    parser = argparse.ArgumentParser(description='從 JSON 檔案生成知識圖譜可視化')
    parser.add_argument('--grade', help='特定年級（如 國一上）')
    parser.add_argument('--unit', help='特定單元 ID（如 JH_NUM_INT_NL）')
    parser.add_argument('--output-dir', default='outputs', help='輸出目錄')
    parser.add_argument('--all', action='store_true', help='生成所有年級和單元')
    
    args = parser.parse_args()
    
    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent
    kg_outputs_path = project_root / 'kg_outputs'
    
    generator = KGVisualizationGenerator(str(kg_outputs_path), args.output_dir)
    
    if args.all:
        generator.generate_all()
    elif args.grade:
        generator.generate_html(args.grade, args.unit)
    else:
        print("請指定 --grade 或使用 --all 生成所有")


if __name__ == '__main__':
    main()
